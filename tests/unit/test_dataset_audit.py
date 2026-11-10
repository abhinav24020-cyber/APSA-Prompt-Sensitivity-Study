import csv

from experiments.validate_baseline_dataset import audit_dataset


def test_audit_reports_structural_errors_and_does_not_claim_answer_validation(tmp_path):
    dataset = tmp_path / "baseline.csv"
    fields = [
        "prompt_id",
        "task_category",
        "task_description",
        "original_prompt",
        "expected_answer",
        "difficulty_level",
        "metadata",
    ]
    rows = [
        {
            "prompt_id": "QA-001",
            "task_category": "question_answering",
            "task_description": "Fact retrieval",
            "original_prompt": "What is 2+2?",
            "expected_answer": "4",
            "difficulty_level": "easy",
            "metadata": '{"is_deterministic": true}',
        },
        {
            "prompt_id": "QA-001",
            "task_category": "question_answering",
            "task_description": "Duplicate id",
            "original_prompt": "What is 3+3?",
            "expected_answer": "6",
            "difficulty_level": "easy",
            "metadata": "bad json",
        },
    ]
    with dataset.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    report = audit_dataset(dataset)

    assert report["row_count"] == 2
    assert report["duplicate_prompt_ids"] == ["QA-001"]
    assert len(report["metadata_errors"]) == 1
    assert report["reference_answer_correctness"]["review_required"] is True
    assert report["structural_checks_passed"] is False
