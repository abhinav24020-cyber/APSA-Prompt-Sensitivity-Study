"""HotpotQA dataset loader (multi-hop closed QA)."""

from apsa.config.schema import TaskCategory
from .base_dataset import BaseDataset, DatasetItem


class HotpotQADataset(BaseDataset):
    """Loader for the HotpotQA multi-hop QA benchmark."""

    @property
    def task_category(self) -> TaskCategory:
        return TaskCategory.CLOSED_QA_EXTRACTION

    def load(self, split="validation", sample_size=None, seed=42) -> list[DatasetItem]:
        raise NotImplementedError
