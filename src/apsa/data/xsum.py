"""XSum dataset loader (abstractive summarization)."""

from apsa.config.schema import TaskCategory
from .base_dataset import BaseDataset, DatasetItem


class XSumDataset(BaseDataset):
    """Loader for the BBC XSum abstractive summarization benchmark."""

    @property
    def task_category(self) -> TaskCategory:
        return TaskCategory.SUMMARIZATION

    def load(self, split="test", sample_size=None, seed=42) -> list[DatasetItem]:
        raise NotImplementedError
