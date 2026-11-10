"""Abstract base class for all prompt formatters."""

from abc import ABC, abstractmethod
from dataclasses import dataclass

from apsa.data.base_dataset import DatasetItem


@dataclass
class PromptRecord:
    """A fully-formatted prompt pair ready for inference."""
    original_prompt: str
    system_prompt: str
    task_category: str
    dataset_item_id: str


class BaseFormatter(ABC):
    """Convert a :class:`DatasetItem` into a :class:`PromptRecord`."""

    DEFAULT_SYSTEM_PROMPT: str = (
        "You are a precise academic assistant. Follow instructions exactly."
    )

    @abstractmethod
    def format(
        self,
        item: DatasetItem,
        system_prompt: str = DEFAULT_SYSTEM_PROMPT,
    ) -> PromptRecord:
        """Return a formatted :class:`PromptRecord` for the given item."""
        ...
