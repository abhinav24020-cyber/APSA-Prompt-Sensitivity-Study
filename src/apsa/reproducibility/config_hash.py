"""Deterministic SHA-256 hash of a fully-resolved ExperimentConfig."""

import hashlib
import json
from typing import Any


def hash_config(config) -> str:  # ExperimentConfig
    """Return the full SHA-256 hex digest of the serialized config.

    The config is serialized to JSON with sorted keys to guarantee
    determinism regardless of dict insertion order.
    """
    config_dict = config.model_dump()
    canonical_json = json.dumps(config_dict, sort_keys=True, default=str)
    return hashlib.sha256(canonical_json.encode()).hexdigest()


def short_hash(config) -> str:
    """Return the first 8 hex characters of the config hash (for experiment IDs)."""
    return hash_config(config)[:8]
