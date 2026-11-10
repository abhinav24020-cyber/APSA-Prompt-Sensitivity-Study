"""Structured JSON logger for the APSA system."""

import logging
import sys
from pathlib import Path
from typing import Any


def get_logger(name: str) -> logging.Logger:
    """Return a configured logger for the given module name."""
    logger = logging.getLogger(name)
    if not logger.handlers and not logging.getLogger("apsa").handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(
            "%(asctime)s [%(levelname)-8s] %(name)s: %(message)s",
            datefmt="%H:%M:%S",
        ))
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
    return logger


def configure_logging(
    log_dir: Path,
    experiment_id: str,
    log_level: str = "INFO",
) -> None:
    """Set up all log handlers for an experiment run."""
    log_dir = Path(log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)

    root = logging.getLogger("apsa")
    root.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    root.handlers.clear()

    # Console handler
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    console.setFormatter(logging.Formatter(
        "%(asctime)s [%(levelname)-8s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    ))
    root.addHandler(console)

    # JSON file handler (experiment.log)
    file_fmt = logging.Formatter(
        '{"time":"%(asctime)s","level":"%(levelname)s","module":"%(name)s","msg":"%(message)s"}'
    )
    file_handler = logging.FileHandler(log_dir / "experiment.log", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_fmt)
    root.addHandler(file_handler)

    # Error-only file handler (errors.log)
    error_handler = logging.FileHandler(log_dir / "errors.log", encoding="utf-8")
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_fmt)
    root.addHandler(error_handler)
