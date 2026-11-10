"""Append-only JSONL result writer. Thread-safe."""

import threading
from pathlib import Path

from .schema import ExperimentFailure, ExperimentRun


class ResultWriter:
    """Write :class:`ExperimentRun` records to an append-only JSONL file.

    Thread-safe: multiple :class:`~apsa.execution.trial.TrialRunner`
    threads may call :meth:`write` concurrently.
    """

    def __init__(self, output_path: Path) -> None:
        self._path = output_path
        self._lock = threading.Lock()
        output_path.parent.mkdir(parents=True, exist_ok=True)

    def write(self, run: ExperimentRun) -> None:
        """Serialize and append one run record; flush immediately."""
        line = run.model_dump_json() + "\n"
        with self._lock, self._path.open("a", encoding="utf-8") as fh:
            fh.write(line)
            fh.flush()

    def write_failure(self, failure: ExperimentFailure) -> None:
        """Append a failed trial to the sibling failures JSONL file."""
        failure_path = self._path.with_name("failures.jsonl")
        line = failure.model_dump_json() + "\n"
        with self._lock, failure_path.open("a", encoding="utf-8") as fh:
            fh.write(line)
            fh.flush()
