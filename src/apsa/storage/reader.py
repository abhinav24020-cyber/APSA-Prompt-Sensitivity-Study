"""JSONL result reader with filtering support."""

import json
from collections.abc import Iterator
from pathlib import Path

from .schema import ExperimentRun


class ResultReader:
    """Stream :class:`ExperimentRun` records from a JSONL results file.

    Supports filtering by ``model_name``, ``task_category``, and
    ``perturbation_type``.
    """

    def __init__(self, runs_path: Path) -> None:
        self._path = runs_path

    def stream(
        self,
        model_name: str | None = None,
        task_category: str | None = None,
        perturbation_type: str | None = None,
    ) -> Iterator[ExperimentRun]:
        """Yield matching :class:`ExperimentRun` records from the JSONL file."""
        with self._path.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                record = ExperimentRun.model_validate_json(line)
                if model_name and record.model_name != model_name:
                    continue
                if task_category and record.task_category != task_category:
                    continue
                if perturbation_type and record.perturbation_type != perturbation_type:
                    continue
                yield record
