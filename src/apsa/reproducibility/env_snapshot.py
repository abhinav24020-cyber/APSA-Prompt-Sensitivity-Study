"""Environment manifest capture for full reproducibility."""

import platform
import subprocess
import sys
from typing import Any


def capture_environment() -> dict[str, Any]:
    """Capture a full snapshot of the current execution environment."""
    return {
        "python_version": sys.version,
        "platform": platform.platform(),
        "packages": _get_pip_packages(),
        "cuda_version": _get_cuda_version(),
        "git_commit": _get_git_commit(),
    }


def _get_pip_packages() -> dict[str, str]:
    try:
        import importlib.metadata as metadata
        packages = {}
        for dist in metadata.distributions():
            name = dist.metadata.get("Name")
            ver = dist.metadata.get("Version")
            if name and ver:
                packages[name] = ver
        return packages
    except Exception:
        return {}


def _get_cuda_version() -> str | None:
    try:
        import torch
        return torch.version.cuda
    except Exception:
        return None


def _get_git_commit() -> str | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True, text=True, timeout=5
        )
        return result.stdout.strip() if result.returncode == 0 else None
    except Exception:
        return None
