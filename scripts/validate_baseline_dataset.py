"""Validation script to ensure data/baseline_prompts.csv meets all benchmark requirements."""

import csv
import json
import sys
from collections import Counter
from pathlib import Path

CSV_PATH = Path("data/baseline_prompts.csv")

EXPECTED_CATEGORIES = {
    "mathematical_reasoning": 20,
    "logical_reasoning": 20,
    "question_answering": 20,
    "classification": 20,
    "code_generation": 20,
}

EXPECTED_FIELDS = [
    "prompt_id",
    "task_category",
    "task_description",
    "original_prompt",
    "expected_answer",
    "difficulty_level",
    "metadata",
]

ALLOWED_DIFFICULTIES = {"easy", "medium", "hard"}


def validate_dataset() -> bool:
    print(f"Validating baseline dataset at: {CSV_PATH}")

    if not CSV_PATH.exists():
        print(f"FAIL: File {CSV_PATH} does not exist.")
        return False

    errors = []
    ids = set()
    category_counts = Counter()

    with open(CSV_PATH, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        # 1. Header check
        if reader.fieldnames != EXPECTED_FIELDS:
            errors.append(f"Header mismatch. Expected {EXPECTED_FIELDS}, got {reader.fieldnames}")

        row_count = 0
        for i, row in enumerate(reader, start=1):
            row_count += 1
            pid = row.get("prompt_id", "").strip()

            # 2. Unique prompt_id check
            if not pid:
                errors.append(f"Row {i}: Missing prompt_id")
            elif pid in ids:
                errors.append(f"Row {i}: Duplicate prompt_id '{pid}'")
            else:
                ids.add(pid)

            # 3. Category check
            cat = row.get("task_category", "").strip()
            if cat not in EXPECTED_CATEGORIES:
                errors.append(f"Row {i} ({pid}): Invalid category '{cat}'")
            else:
                category_counts[cat] += 1

            # 4. Mandatory fields non-empty
            for field in EXPECTED_FIELDS:
                if field != "expected_answer" and not row.get(field, "").strip():
                    errors.append(f"Row {i} ({pid}): Mandatory field '{field}' is empty")

            # 5. Difficulty level check
            diff = row.get("difficulty_level", "").strip()
            if diff not in ALLOWED_DIFFICULTIES:
                errors.append(f"Row {i} ({pid}): Invalid difficulty '{diff}'")

            # 6. JSON metadata parse check
            meta_str = row.get("metadata", "").strip()
            if meta_str:
                try:
                    meta_obj = json.loads(meta_str)
                    if not isinstance(meta_obj, dict):
                        errors.append(f"Row {i} ({pid}): Metadata JSON must be an object/dict")
                    if "is_deterministic" not in meta_obj:
                        errors.append(f"Row {i} ({pid}): Metadata missing 'is_deterministic'")
                except json.JSONDecodeError as e:
                    errors.append(f"Row {i} ({pid}): Invalid JSON metadata - {e}")

    # 7. Total count check
    if row_count != 100:
        errors.append(f"Total row count is {row_count}, expected 100")

    # 8. Category distribution check
    for cat, expected in EXPECTED_CATEGORIES.items():
        actual = category_counts[cat]
        if actual != expected:
            errors.append(f"Category '{cat}' has {actual} examples, expected {expected}")

    if errors:
        print(f"Validation FAILED with {len(errors)} error(s):")
        for err in errors:
            print(f" - {err}")
        return False

    print("Validation SUCCESSFUL!")
    print(f" - Total prompts: {row_count}")
    print(f" - Unique prompt IDs: {len(ids)}")
    print(" - Category distribution:")
    for cat, count in category_counts.items():
        print(f"    * {cat}: {count}")
    return True


if __name__ == "__main__":
    success = validate_dataset()
    sys.exit(0 if success else 1)
