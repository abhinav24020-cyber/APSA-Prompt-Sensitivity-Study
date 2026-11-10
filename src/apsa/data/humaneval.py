"""HumanEval dataset loader (code generation)."""

import random
import socket
from apsa.config.schema import TaskCategory
from .base_dataset import BaseDataset, DatasetItem


def _has_network() -> bool:
    try:
        s = socket.create_connection(("huggingface.co", 443), timeout=1.5)
        s.close()
        return True
    except OSError:
        return False


class HumanEvalDataset(BaseDataset):
    """Loader for the OpenAI HumanEval code benchmark."""

    @property
    def task_category(self) -> TaskCategory:
        return TaskCategory.CODE_GENERATION

    def load(
        self,
        split: str = "test",
        sample_size: int | None = None,
        seed: int = 42,
    ) -> list[DatasetItem]:
        items: list[DatasetItem] = []
        loaded = False

        if _has_network():
            try:
                from datasets import load_dataset
                ds = load_dataset("openai_humaneval", split="test")
                for row in ds:
                    items.append(
                        DatasetItem(
                            id=row["task_id"].replace("/", "_"),
                            task_category=self.task_category,
                            input_text=row["prompt"],
                            gold_answer=row["canonical_solution"],
                            metadata={
                                "source": "humaneval",
                                "task_id": row["task_id"],
                                "entry_point": row["entry_point"],
                                "test": row["test"],
                            },
                        )
                    )
                loaded = True
            except Exception:
                loaded = False

        if not loaded:
            # Fast fallback to local baseline CSV
            from .baseline import BaselineCSVDataset
            base_loader = BaselineCSVDataset()
            all_items = base_loader.load(split=split, seed=seed)
            items = [it for it in all_items if it.task_category == self.task_category]

        if sample_size and sample_size < len(items):
            rng = random.Random(seed)
            items = rng.sample(items, sample_size)
        return items
