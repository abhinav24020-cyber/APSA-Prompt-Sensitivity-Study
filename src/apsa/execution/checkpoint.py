"""Resume-from-checkpoint support."""

from pathlib import Path


class CheckpointManager:
    """Tracks completed ``run_id`` strings in a sidecar file.

    On resume, completed trials are skipped by the :class:`Scheduler`.
    """

    def __init__(self, checkpoint_path: Path) -> None:
        self._path = checkpoint_path

    def load_completed(self) -> set[str]:
        """Return the set of ``run_id`` strings already completed."""
        if not self._path.exists():
            return set()
        return set(self._path.read_text().splitlines())

    def mark_completed(self, run_id: str) -> None:
        """Append a completed ``run_id`` to the checkpoint file."""
        with self._path.open("a") as fh:
            fh.write(run_id + "\n")
