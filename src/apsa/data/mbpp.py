"""MBPP dataset loader (code generation)."""

from apsa.config.schema import TaskCategory
from .base_dataset import BaseDataset, DatasetItem


class MBPPDataset(BaseDataset):
    """Loader for the Mostly Basic Python Problems benchmark."""

    @property
    def task_category(self) -> TaskCategory:
        return TaskCategory.CODE_GENERATION

    def load(self, split="test", sample_size=None, seed=42) -> list[DatasetItem]:
        raise NotImplementedError
