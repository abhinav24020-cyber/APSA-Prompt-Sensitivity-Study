"""MATH dataset loader (mathematical reasoning subset)."""

from apsa.config.schema import TaskCategory
from .base_dataset import BaseDataset, DatasetItem


class MATHDataset(BaseDataset):
    """Loader for the MATH competition benchmark subset."""

    @property
    def task_category(self) -> TaskCategory:
        return TaskCategory.MATHEMATICAL_REASONING

    def load(self, split="test", sample_size=None, seed=42) -> list[DatasetItem]:
        raise NotImplementedError
