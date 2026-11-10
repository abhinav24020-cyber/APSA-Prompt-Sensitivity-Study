"""CLI entry point: run all statistical analyses on existing results.

Usage:
    python scripts/run_analysis.py --experiment-id apsa_20260911_abc12def_42
"""

import json
import click
from pathlib import Path

from apsa.analysis.sensitivity import SensitivityRecord, SensitivityAnalyzer
from apsa.storage.reader import ResultReader


@click.command()
@click.option("--experiment-id", required=True, help="Experiment ID to analyse.")
@click.option("--results-dir", default="results", show_default=True,
              type=click.Path(path_type=Path))
def main(experiment_id: str, results_dir: Path) -> None:
    """Run statistical analysis on a completed experiment."""
    exp_dir = Path(results_dir) / experiment_id
    results_file = exp_dir / "results.jsonl"

    if not results_file.exists():
        candidates = list(Path(results_dir).glob(f"*{experiment_id}*/**/results.jsonl"))
        if not candidates:
            candidates = list(Path(results_dir).glob(f"**/*{experiment_id}*.jsonl"))
        if candidates:
            results_file = candidates[0]
            exp_dir = results_file.parent
        else:
            raise click.ClickException(f"No results found for experiment '{experiment_id}' at {results_file}")

    print(f"Loading results from: {results_file}")
    reader = ResultReader(results_file)

    records: list[SensitivityRecord] = []
    for r in reader.stream():
        records.append(
            SensitivityRecord(
                experiment_id=r.experiment_id,
                model=r.model_name,
                task_category=r.task_category,
                prompt_id=r.dataset_item_id,
                perturbation_type=r.perturbation_type,
                d_input=r.epsilon_budget_used.lexical_char_normalized,
                d_semantic_input=r.epsilon_budget_used.semantic_cosine,
                d_output=r.composite_output_divergence,
                original_output_correct=r.functional_metrics.original_pass,
                perturbed_output_correct=r.functional_metrics.perturbed_pass,
            )
        )

    if not records:
        print("No records found in results file.")
        return

    analyzer = SensitivityAnalyzer(records)
    mean_dev = analyzer.mean_output_deviation()
    median_dev = analyzer.median_output_deviation()
    ci_95 = analyzer.confidence_interval_output_deviation(confidence=0.95)
    max_dev_10 = analyzer.max_output_deviation_under_budget(0.10)
    top_cases = analyzer.top_k_sensitivity_cases(k=5)
    highest_task = analyzer.highest_sensitivity_per_task()
    highest_pert = analyzer.highest_sensitivity_per_perturbation()
    highest_model = analyzer.highest_sensitivity_per_model()

    summary = {
        "experiment_id": experiment_id,
        "total_records": len(records),
        "mean_output_deviation": round(mean_dev, 4),
        "median_output_deviation": round(median_dev, 4),
        "ci_95_output_deviation": [round(ci_95[0], 4), round(ci_95[1], 4)],
        "max_deviation_under_budget_0_10": round(max_dev_10, 4),
        "highest_sensitivity_per_task": {k: round(v, 4) for k, v in highest_task.items()},
        "highest_sensitivity_per_perturbation": {k: round(v, 4) for k, v in highest_pert.items()},
        "highest_sensitivity_per_model": {k: round(v, 4) for k, v in highest_model.items()},
        "top_cases": [
            {
                "prompt_id": rec.prompt_id,
                "task_category": rec.task_category,
                "perturbation_type": rec.perturbation_type,
                "model": rec.model,
                "d_input": round(rec.d_input, 4),
                "d_output": round(rec.d_output, 4),
                "sensitivity": round(score, 4),
            }
            for rec, score in top_cases
        ],
    }

    out_file = exp_dir / "analysis_summary.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("\n" + "=" * 60)
    print("STATISTICAL SENSITIVITY ANALYSIS COMPLETE")
    print("=" * 60)
    print(json.dumps(summary, indent=2))
    print(f"\nSummary saved to: {out_file.resolve()}")


if __name__ == "__main__":
    main()
