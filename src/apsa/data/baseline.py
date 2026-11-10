"""Baseline CSV dataset loader for APSA sensitivity experiments."""

import csv
import json
from pathlib import Path
from typing import Any

from apsa.config.schema import TaskCategory
from apsa.data.base_dataset import BaseDataset, DatasetItem


class BaselineCSVDataset(BaseDataset):
    """Loader for the 100-prompt APSA baseline dataset stored in CSV format."""

    def __init__(self, csv_path: str | Path = "data/baseline_prompts.csv"):
        self.csv_path = Path(csv_path)

    @property
    def task_category(self) -> TaskCategory:
        """Returns default general category or mathematical_reasoning as primary."""
        return TaskCategory.MATHEMATICAL_REASONING

    def load(
        self,
        split: str = "test",
        sample_size: int | None = None,
        seed: int = 42,
    ) -> list[DatasetItem]:
        """Load prompts from CSV and convert to DatasetItem instances."""
        if not self.csv_path.exists():
            raise FileNotFoundError(f"Baseline CSV file not found at {self.csv_path}")

        items: list[DatasetItem] = []
        with open(self.csv_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                meta: dict[str, Any] = {}
                if row.get("metadata"):
                    try:
                        meta = json.loads(row["metadata"])
                    except json.JSONDecodeError:
                        meta = {"raw_metadata": row["metadata"]}

                meta["task_description"] = row.get("task_description", "")
                meta["difficulty_level"] = row.get("difficulty_level", "medium")

                # Map task_category string to Enum
                cat_str = row.get("task_category", "mathematical_reasoning")
                try:
                    category_enum = TaskCategory(cat_str)
                except ValueError:
                    category_enum = TaskCategory.MATHEMATICAL_REASONING

                item = DatasetItem(
                    id=row["prompt_id"],
                    task_category=category_enum,
                    input_text=row["original_prompt"],
                    gold_answer=row.get("expected_answer"),
                    metadata=meta,
                )
                items.append(item)

        if sample_size is not None and sample_size < len(items):
            import random

            rng = random.Random(seed)
            items = rng.sample(items, sample_size)

        return items
