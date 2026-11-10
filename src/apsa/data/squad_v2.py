"""SQuAD v2.0 dataset loader (closed QA / extraction)."""

from apsa.config.schema import TaskCategory
from .base_dataset import BaseDataset, DatasetItem


class SQuADv2Dataset(BaseDataset):
    """Loader for the Stanford Question Answering Dataset v2.0."""

    @property
    def task_category(self) -> TaskCategory:
        return TaskCategory.CLOSED_QA_EXTRACTION

    def load(self, split="validation", sample_size=None, seed=42) -> list[DatasetItem]:
        raise NotImplementedError
