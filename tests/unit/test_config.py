"""Unit tests for configuration loading and validation."""

import pytest
from pathlib import Path
import yaml
from apsa.config.loader import load_config, _deep_merge, _DEFAULT_CONFIG_PATH


class TestConfigLoader:
    def test_default_config_loads(self):
        with _DEFAULT_CONFIG_PATH.open(encoding="utf-8-sig") as f:
            data = yaml.safe_load(f)
        assert "experiment" in data
        assert "generation" in data
        assert "epsilon_budget" in data
        assert "metric_weights" in data

    def test_experiment_config_loads(self):
        pilot_cfg_path = Path("config/experiments/pilot_small.yaml")
        cfg = load_config(pilot_cfg_path)
        assert cfg.experiment.name == "apsa_pilot"
        assert len(cfg.models) >= 1
        assert len(cfg.perturbations) >= 1

    def test_deep_merge(self):
        base = {"a": {"b": 1, "c": 2}, "d": 3}
        override = {"a": {"b": 99}, "d": 4}
        merged = _deep_merge(base, override)
        assert merged == {"a": {"b": 99, "c": 2}, "d": 4}
