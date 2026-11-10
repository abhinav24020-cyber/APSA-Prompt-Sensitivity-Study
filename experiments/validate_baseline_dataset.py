"""Audit baseline CSV structure and sampling coverage without asserting gold correctness."""

import argparse
import ast
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

REQUIRED_FIELDS = {
    "prompt_id",
    "task_category",
    "task_description",
    "original_prompt",
    "expected_answer",
    "difficulty_level",
    "metadata",
}


def audit_dataset(dataset_path: Path) -> dict[str, Any]:
    with dataset_path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        headers = set(reader.fieldnames or [])
        rows = list(reader)

    missing_columns = sorted(REQUIRED_FIELDS - headers)
    prompt_ids = [row.get("prompt_id", "").strip() for row in rows]
    duplicate_ids = sorted(
        prompt_id for prompt_id, count in Counter(prompt_ids).items()
        if prompt_id and count > 1
    )
    blank_required_fields = {
        field: [
            row.get("prompt_id") or f"line-{index + 2}"
            for index, row in enumerate(rows)
            if not (row.get(field) or "").strip()
        ]
        for field in sorted(REQUIRED_FIELDS)
        if field in headers
    }

    metadata_errors = []
    duplicate_prompts = []
    seen_prompts: dict[str, str] = {}
    category_counts = Counter()
    difficulty_counts = Counter()
    expected_answer_coverage = Counter()
    code_syntax_errors = []
    for index, row in enumerate(rows, start=2):
        category_counts[(row.get("task_category") or "").strip()] += 1
        difficulty_counts[(row.get("difficulty_level") or "").strip()] += 1
        expected_answer_coverage[
            "present" if (row.get("expected_answer") or "").strip() else "missing"
        ] += 1
        try:
            metadata = json.loads(row.get("metadata") or "")
            if not isinstance(metadata, dict):
                raise TypeError("metadata must be a JSON object")
        except (json.JSONDecodeError, TypeError) as error:
            metadata_errors.append({
                "line": index,
                "prompt_id": row.get("prompt_id"),
                "error": str(error),
            })

        if row.get("task_category") == "code_generation":
            try:
                ast.parse(row.get("expected_answer") or "")
            except SyntaxError as error:
                code_syntax_errors.append({
                    "line": index,
                    "prompt_id": row.get("prompt_id"),
                    "error": error.msg,
                })

        normalized_prompt = " ".join((row.get("original_prompt") or "").casefold().split())
        if normalized_prompt in seen_prompts:
            duplicate_prompts.append({
                "prompt_id": row.get("prompt_id"),
                "duplicate_of": seen_prompts[normalized_prompt],
            })
        elif normalized_prompt:
            seen_prompts[normalized_prompt] = row.get("prompt_id", "")

    eligible_categories = {
        category: count
        for category, count in category_counts.items()
        if category and count >= 10
    }
    dataset_digest = hashlib.sha256(dataset_path.read_bytes()).hexdigest()
    return {
        "dataset_path": str(dataset_path),
        "dataset_sha256": dataset_digest,
        "row_count": len(rows),
        "columns": sorted(headers),
        "missing_columns": missing_columns,
        "duplicate_prompt_ids": duplicate_ids,
        "duplicate_prompt_texts": duplicate_prompts,
        "blank_required_fields": blank_required_fields,
        "metadata_errors": metadata_errors,
        "category_counts": dict(sorted(category_counts.items())),
        "difficulty_counts": dict(sorted(difficulty_counts.items())),
        "expected_answer_coverage": dict(expected_answer_coverage),
        "code_reference_syntax": {
            "parseable_python_references": (
                category_counts.get("code_generation", 0) - len(code_syntax_errors)
            ),
            "syntax_errors": code_syntax_errors,
            "functional_correctness": "not tested",
        },
        "pilot_sampling_eligibility": {
            "categories_with_at_least_10_rows": dict(sorted(eligible_categories.items())),
            "pilot_selects_first_10_rows_per_category_in_csv_order": True,
            "randomized_sampling": False,
        },
        "rows_excluded_by_audit": [],
        "reference_answer_correctness": {
            "status": "not established by structural audit",
            "review_required": True,
        },
        "structural_checks_passed": not (
            missing_columns
            or duplicate_ids
            or metadata_errors
            or any(blank_required_fields.values())
            or code_syntax_errors
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dataset",
        type=Path,
        default=Path("data/baseline_prompts.csv"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/baseline_dataset_audit.json"),
    )
    args = parser.parse_args()

    report = audit_dataset(args.dataset)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    if not report["structural_checks_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
