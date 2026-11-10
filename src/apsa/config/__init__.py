"""Configuration sub-package."""

def __getattr__(name: str):
    if name == "load_config":
        from .loader import load_config
        return load_config
    if name == "ExperimentConfig":
        from .experiment_config import ExperimentConfig
        return ExperimentConfig
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = ["load_config", "ExperimentConfig"]
