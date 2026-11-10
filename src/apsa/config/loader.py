"""YAML configuration loader with default-merging and Pydantic validation."""

from pathlib import Path
from typing import Any

from .experiment_config import ExperimentConfig

_DEFAULT_CONFIG_PATH = Path(__file__).parent.parent.parent.parent / "config" / "default.yaml"


def _deep_merge(base: dict, override: dict) -> dict:
    """Recursively merge ``override`` into ``base`` (override wins)."""
    result = dict(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def _resolve_sub_configs(config_dict: dict, root_dir: Path) -> dict:
    import yaml
    if "models" in config_dict and isinstance(config_dict["models"], list):
        resolved_models = []
        for m in config_dict["models"]:
            if isinstance(m, dict) and "config_file" in m:
                p = root_dir / m["config_file"]
                if not p.exists():
                    p = Path(m["config_file"])
                if p.exists():
                    with p.open(encoding="utf-8-sig") as f:
                        data = yaml.safe_load(f) or {}
                    merged_m = {**data, **{k: v for k, v in m.items() if k != "config_file"}}
                    resolved_models.append(merged_m)
                else:
                    resolved_models.append(m)
            else:
                resolved_models.append(m)
        config_dict["models"] = resolved_models

    if "perturbations" in config_dict and isinstance(config_dict["perturbations"], list):
        resolved_perts = []
        for p_item in config_dict["perturbations"]:
            if isinstance(p_item, dict) and "config_file" in p_item:
                p = root_dir / p_item["config_file"]
                if not p.exists():
                    p = Path(p_item["config_file"])
                if p.exists():
                    with p.open(encoding="utf-8-sig") as f:
                        data = yaml.safe_load(f) or {}
                    p_type = p_item.get("type", "")
                    params = data.get(p_type, {}) if isinstance(data, dict) else {}
                    merged_p = {
                        "type": p_type,
                        "params": p_item.get("params", params),
                    }
                    resolved_perts.append(merged_p)
                else:
                    resolved_perts.append(p_item)
            else:
                resolved_perts.append(p_item)
        config_dict["perturbations"] = resolved_perts

    return config_dict


def load_config(
    experiment_config_path: Path,
    default_config_path: Path = _DEFAULT_CONFIG_PATH,
) -> ExperimentConfig:
    """Load, merge (with defaults), and validate the experiment config.

    Args:
        experiment_config_path: Path to the experiment-specific YAML override.
        default_config_path: Path to the master defaults YAML.

    Returns:
        A fully-resolved and validated :class:`ExperimentConfig`.
    """
    import yaml
    with default_config_path.open(encoding="utf-8-sig") as f:
        defaults: dict[str, Any] = yaml.safe_load(f) or {}

    with experiment_config_path.open(encoding="utf-8-sig") as f:
        overrides: dict[str, Any] = yaml.safe_load(f) or {}

    merged = _deep_merge(defaults, overrides)
    root_dir = default_config_path.parent.parent
    merged = _resolve_sub_configs(merged, root_dir)
    return ExperimentConfig(**merged)
