import json

from apsa.metrics.functional.pilot_correctness import evaluate_pilot_answer
from experiments.evaluate_experiment import evaluate_results


def test_pilot_answer_evaluation_handles_labels_and_numeric_answers():
    assert evaluate_pilot_answer(
        "**Politics**",
        "Business",
        "classification",
    ) is False
    assert evaluate_pilot_answer(
        "The answer is $7.20.",
        "$7.20",
        "mathematical_reasoning",
    ) is True
    assert evaluate_pilot_answer(
        "The solution is approximately (2.6154, 4.0769).",
        "(34/13, 53/13)",
        "mathematical_reasoning",
    ) is True
    assert evaluate_pilot_answer(
        "The solution is (2, 5).",
        "(34/13, 53/13)",
        "mathematical_reasoning",
    ) is False
    assert evaluate_pilot_answer(
        "The capital of France is Paris.",
        "Paris",
        "question_answering",
    ) is True
    assert evaluate_pilot_answer(
        "A -> D -> B -> C",
        "A -> B -> D -> C; A -> D -> B -> C",
        "logical_reasoning",
    ) is True
    assert evaluate_pilot_answer(
        "def solve(): return 42",
        "42",
        "code_generation",
    ) is None
    assert evaluate_pilot_answer(
        "Assume there are finitely many primes, then construct their product plus one.",
        "1. Assume finitely many primes p1..pn. 2. Construct N = p1*...*pn + 1. "
        "3. Show N has a prime factor not in the list, contradicting the assumption.",
        "mathematical_reasoning",
    ) is None


def test_evaluator_reports_correctness_semantics_and_controls(tmp_path):
    source = tmp_path / "raw.jsonl"
    records = [
        {
            "status": "success",
            "condition": "treatment",
            "perturbation_type": "word_substitution",
            "experiment_id": "pilot_test",
            "model": "mock-model",
            "task_category": "classification",
            "prompt_id": "CLASS-001",
            "expected_answer": "Business",
            "original_output": "Business",
            "perturbed_output": "**Politics**",
            "input_distances": {
                "char_levenshtein_normalized": 0.02,
                "semantic_cosine_distance": 0.03,
            },
        },
        {
            "status": "success",
            "condition": "control",
            "experiment_id": "pilot_test",
            "model": "mock-model",
            "task_category": "classification",
            "prompt_id": "CLASS-001",
            "expected_answer": "Business",
            "original_output": "Business",
            "perturbed_output": "Business.",
            "input_distances": {
                "char_levenshtein_normalized": 0.0,
                "semantic_cosine_distance": 0.0,
            },
        },
    ]
    source.write_text(
        "".join(json.dumps(record) + "\n" for record in records),
        encoding="utf-8",
    )
    (tmp_path / "failed_trials.jsonl").write_text(
        json.dumps({"status": "failed", "error_type": "RateLimitError"}) + "\n",
        encoding="utf-8",
    )

    summary = evaluate_results(source, tmp_path / "analysis")

    assert summary["total_treatment_records_analyzed"] == 1
    assert summary["failed_records_skipped"] == 1
    assert summary["records_missing_semantic_input_distance"] == 0
    assert summary["correctness"]["applicable_pairs"] == 1
    assert summary["correctness"]["correct_to_incorrect"] == 1
    assert summary["unchanged_prompt_control"]["records"] == 1

    evaluated = (tmp_path / "analysis" / "evaluated_records.jsonl").read_text(
        encoding="utf-8"
    ).splitlines()
    treatment = json.loads(evaluated[0])
    assert treatment["sensitivity"]["composite_input_distance"] == 0.025


def test_missing_semantic_distance_is_not_substituted_or_scored(tmp_path):
    source = tmp_path / "raw.jsonl"
    source.write_text(
        json.dumps({
            "status": "success",
            "condition": "treatment",
            "experiment_id": "pilot_test",
            "model": "mock-model",
            "task_category": "code_generation",
            "prompt_id": "CODE-001",
            "perturbation_type": "word_insertion",
            "original_output": "A",
            "perturbed_output": "B",
            "input_distances": {"char_levenshtein_normalized": 0.02},
        }) + "\n",
        encoding="utf-8",
    )

    summary = evaluate_results(source, tmp_path / "analysis")
    evaluated = json.loads(
        (tmp_path / "analysis" / "evaluated_records.jsonl").read_text(
            encoding="utf-8"
        )
    )

    assert summary["records_missing_semantic_input_distance"] == 1
    assert summary["max_output_character_distance_under_semantic_input_budget_0_05"] is None
    assert evaluated["sensitivity"]["composite_input_distance"] is None
    assert evaluated["sensitivity"]["composite_input_ratio"] is None
