"""Evaluate paired pilot outputs and unchanged-prompt controls."""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any

sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

from apsa.analysis.sensitivity import SensitivityAnalyzer, SensitivityRecord
from apsa.metrics.functional.pilot_correctness import evaluate_pilot_answer
from apsa.metrics.output_distance import OutputDeviationMetrics

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

LEXICAL_INPUT_WEIGHT = 0.5
SEMANTIC_INPUT_WEIGHT = 0.5


def evaluate_results(
    input_jsonl: Path,
    output_dir: Path,
    use_semantic: bool = False,
) -> dict[str, Any]:
    """Evaluate successful treatment/control records, preserving unavailable metrics."""
    logger.info("Loading raw trial records from %s", input_jsonl)
    metrics_calc = OutputDeviationMetrics(use_semantic=use_semantic)
    treatment_records: list[SensitivityRecord] = []
    evaluated_records: list[dict[str, Any]] = []
    control_deviations: list[float] = []
    correctness = {
        "applicable_pairs": 0,
        "original_correct": 0,
        "perturbed_correct": 0,
        "correct_to_incorrect": 0,
        "incorrect_to_correct": 0,
    }
    failed_records = 0
    missing_semantic_records = 0

    def rounded_max_if_any(records: list[SensitivityRecord]) -> float | None:
        maximum = max((record.d_output for record in records), default=None)
        return round(maximum, 4) if maximum is not None else None

    with input_jsonl.open("r", encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, start=1):
            if not line.strip():
                continue
            row = json.loads(line)
            if row.get("status") != "success":
                failed_records += 1
                continue

            output_metrics = metrics_calc.compute_all(
                row["original_output"], row["perturbed_output"]
            )
            d_output = output_metrics["normalized_character_distance"]
            d_input_char = row.get("input_distances", {}).get(
                "char_levenshtein_normalized"
            )
            d_input_semantic = row.get("input_distances", {}).get(
                "semantic_cosine_distance"
            )
            correctness_original = evaluate_pilot_answer(
                row["original_output"],
                row.get("expected_answer"),
                row["task_category"],
            )
            correctness_perturbed = evaluate_pilot_answer(
                row["perturbed_output"],
                row.get("expected_answer"),
                row["task_category"],
            )

            evaluated = {
                **row,
                "output_deviation_metrics": output_metrics,
                "correctness": {
                    "applicable": correctness_original is not None
                    and correctness_perturbed is not None,
                    "original_correct": correctness_original,
                    "perturbed_correct": correctness_perturbed,
                    "functional_failure": (
                        correctness_original is True and correctness_perturbed is False
                    ),
                    "correctness_flip": (
                        correctness_original is not None
                        and correctness_perturbed is not None
                        and correctness_original != correctness_perturbed
                    ),
                },
            }

            if row.get("condition") == "control":
                control_deviations.append(d_output)
                evaluated_records.append(evaluated)
                continue

            if d_input_char is None:
                raise ValueError(
                    f"Successful treatment record on line {line_number} is missing "
                    "input_distances.char_levenshtein_normalized"
                )
            if d_input_semantic is None:
                missing_semantic_records += 1

            composite_input_distance = None
            composite_sensitivity = None
            if d_input_semantic is not None:
                composite_input_distance = (
                    LEXICAL_INPUT_WEIGHT * d_input_char
                    + SEMANTIC_INPUT_WEIGHT * d_input_semantic
                )
                composite_sensitivity = d_output / (composite_input_distance + 1e-4)

            char_sensitivity = d_output / (d_input_char + 1e-4)
            evaluated["sensitivity"] = {
                "character_input_ratio": char_sensitivity,
                "composite_input_distance": composite_input_distance,
                "composite_input_ratio": composite_sensitivity,
                "input_weights": {
                    "lexical_character": LEXICAL_INPUT_WEIGHT,
                    "semantic_embedding": SEMANTIC_INPUT_WEIGHT,
                },
            }
            evaluated_records.append(evaluated)

            treatment_records.append(
                SensitivityRecord(
                    experiment_id=row["experiment_id"],
                    model=row["model"],
                    task_category=row["task_category"],
                    prompt_id=row["prompt_id"],
                    perturbation_type=row["perturbation_type"],
                    d_input=d_input_char,
                    d_output=d_output,
                    d_semantic_input=d_input_semantic,
                    original_output_correct=correctness_original,
                    perturbed_output_correct=correctness_perturbed,
                )
            )

            if correctness_original is not None and correctness_perturbed is not None:
                correctness["applicable_pairs"] += 1
                correctness["original_correct"] += int(correctness_original)
                correctness["perturbed_correct"] += int(correctness_perturbed)
                correctness["correct_to_incorrect"] += int(
                    correctness_original and not correctness_perturbed
                )
                correctness["incorrect_to_correct"] += int(
                    not correctness_original and correctness_perturbed
                )

    failure_file = input_jsonl.with_name("failed_trials.jsonl")
    if failure_file.exists():
        with failure_file.open("r", encoding="utf-8") as stream:
            for line in stream:
                if line.strip():
                    json.loads(line)
                    failed_records += 1

    if not treatment_records:
        raise ValueError(f"No successful treatment records found in {input_jsonl}")

    analyzer = SensitivityAnalyzer(treatment_records)
    top_sensitivity = []
    for record, char_score in analyzer.top_k_sensitivity_cases(5):
        composite_distance = None
        composite_score = None
        if record.d_semantic_input is not None:
            composite_distance = (
                LEXICAL_INPUT_WEIGHT * record.d_input
                + SEMANTIC_INPUT_WEIGHT * record.d_semantic_input
            )
            composite_score = record.d_output / (composite_distance + 1e-4)
        top_sensitivity.append({
            "prompt_id": record.prompt_id,
            "task_category": record.task_category,
            "perturbation_type": record.perturbation_type,
            "model": record.model,
            "d_input_character": record.d_input,
            "d_input_semantic": record.d_semantic_input,
            "d_output_character": record.d_output,
            "character_input_ratio": char_score,
            "composite_input_ratio": composite_score,
        })

    summary = {
        "total_treatment_records_analyzed": len(treatment_records),
        "failed_records_skipped": failed_records,
        "failed_trials_file": str(failure_file) if failure_file.exists() else None,
        "records_missing_semantic_input_distance": missing_semantic_records,
        "mean_output_character_distance": round(
            analyzer.mean_output_deviation(), 4
        ),
        "median_output_character_distance": round(
            analyzer.median_output_deviation(), 4
        ),
        "record_level_95_percent_interval": [
            round(value, 4)
            for value in analyzer.confidence_interval_output_deviation()
        ],
        "max_output_character_distance_under_character_input_budget_0_10": (
            rounded_max_if_any([
                record for record in treatment_records if record.d_input <= 0.10
            ])
        ),
        "max_output_character_distance_under_character_input_budget_0_05": (
            rounded_max_if_any([
                record for record in treatment_records if record.d_input <= 0.05
            ])
        ),
        "max_output_character_distance_under_semantic_input_budget_0_05": (
            rounded_max_if_any([
                record for record in treatment_records
                if record.d_semantic_input is not None
                and record.d_semantic_input <= 0.05
            ])
        ),
        "sensitivity_input_weights": {
            "lexical_character": LEXICAL_INPUT_WEIGHT,
            "semantic_embedding": SEMANTIC_INPUT_WEIGHT,
        },
        "highest_character_input_sensitivity_per_task": {
            key: round(value, 4)
            for key, value in analyzer.highest_sensitivity_per_task().items()
        },
        "highest_character_input_sensitivity_per_perturbation": {
            key: round(value, 4)
            for key, value in analyzer.highest_sensitivity_per_perturbation().items()
        },
        "correctness": {
            **correctness,
            "original_accuracy": (
                correctness["original_correct"] / correctness["applicable_pairs"]
                if correctness["applicable_pairs"]
                else None
            ),
            "perturbed_accuracy": (
                correctness["perturbed_correct"] / correctness["applicable_pairs"]
                if correctness["applicable_pairs"]
                else None
            ),
        },
        "unchanged_prompt_control": {
            "records": len(control_deviations),
            "mean_output_character_distance": (
                round(sum(control_deviations) / len(control_deviations), 4)
                if control_deviations
                else None
            ),
            "maximum_output_character_distance": (
                max(control_deviations) if control_deviations else None
            ),
        },
        "top_5_character_input_sensitivity_cases": top_sensitivity,
        "interpretation_note": (
            "Output deviation is normalized character distance. Correctness uses "
            "category-specific reference-answer heuristics, not human adjudication. "
            "Control records compare repeated identical prompts and are not treatment trials."
        ),
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    summary_path = output_dir / "sensitivity_analysis_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    evaluated_path = output_dir / "evaluated_records.jsonl"
    with evaluated_path.open("w", encoding="utf-8") as stream:
        for row in evaluated_records:
            stream.write(json.dumps(row) + "\n")

    logger.info("Analysis summary saved to %s", summary_path)
    logger.info("Detailed evaluated records saved to %s", evaluated_path)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Evaluate pilot treatment and unchanged-prompt control results"
    )
    parser.add_argument("--input", type=Path, required=True, help="Raw pilot JSONL path")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("results/pilot_experiment/analysis"),
        help="Directory for analysis outputs",
    )
    parser.add_argument(
        "--use-semantic",
        action="store_true",
        help="Calculate optional output-embedding metrics (downloads/loads the model if needed)",
    )
    args = parser.parse_args()
    summary = evaluate_results(args.input, args.output_dir, use_semantic=args.use_semantic)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
