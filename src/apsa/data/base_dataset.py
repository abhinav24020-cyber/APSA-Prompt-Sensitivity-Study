"""Abstract base class for all dataset loaders."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from apsa.config.schema import TaskCategory


@dataclass
class DatasetItem:
    """Standardised unit of a benchmark dataset sample."""
    id: str
    task_category: TaskCategory
    input_text: str
    gold_answer: str | None
    metadata: dict[str, Any] = field(default_factory=dict)


class BaseDataset(ABC):
    """Abstract interface for dataset loaders.

    Every concrete loader must implement :meth:`load` and the
    :attr:`task_category` property.
    """

    @abstractmethod
    def load(
        self,
        split: str = "test",
        sample_size: int | None = None,
        seed: int = 42,
    ) -> list[DatasetItem]:
        """Load and return a list of :class:`DatasetItem` objects."""
        ...

    @property
    @abstractmethod
    def task_category(self) -> TaskCategory:
        """Return the :class:`TaskCategory` this dataset belongs to."""
        ...
