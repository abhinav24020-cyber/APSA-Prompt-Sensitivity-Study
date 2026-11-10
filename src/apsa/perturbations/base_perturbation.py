"""Abstract base class for all perturbation operators."""

from __future__ import annotations

import hashlib
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from apsa.perturbations.distance_utils import (
    changed_tokens,
    char_edit_distance,
    is_lexically_minimal,
    word_edit_distance,
)
from apsa.perturbations.semantic_flags import SemanticFlagDetector, SemanticRiskLevel


@dataclass
class PerturbationConfig:
    """Per-operator configuration, typically loaded from YAML experiment config."""
    params: dict[str, Any] = field(default_factory=dict)
    seed: int = 42


# Shared detector instance (stateless — safe to reuse)
_detector = SemanticFlagDetector()

# Operators whose transformations are limited to case or whitespace.
_SURFACE_TYPES: frozenset[str] = frozenset({
    "capitalization",
    "whitespace",
})


class BasePerturbation(ABC):
    """Stateless perturbation operator.

    Subclasses implement :meth:`_apply_transform`, which receives the raw prompt
    string and returns either a modified string or ``None`` if the perturbation
    cannot be applied (e.g. no suitable token found).

    The public entry-point is :meth:`perturb`, which wraps the result in a
    :class:`~apsa.perturbations.perturbation_record.PerturbationRecord` with
    all distance metrics and semantic flags computed automatically.
    """

    @abstractmethod
    def _apply_transform(self, prompt: str, config: PerturbationConfig) -> str | None:
        """Apply the transformation and return the result, or ``None``."""
        ...

    @property
    @abstractmethod
    def perturbation_type(self) -> str:
        """Return the canonical string identifier for this perturbation."""
        ...

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def apply(self, prompt: str, config: PerturbationConfig) -> str | None:
        """Legacy single-string interface kept for backward compatibility.

        Prefer :meth:`perturb` which returns a full :class:`PerturbationRecord`.
        """
        return self._apply_transform(prompt, config)

    def perturb(
        self,
        prompt: str,
        prompt_id: str = "unknown",
        config: PerturbationConfig | None = None,
    ) -> PerturbationRecord | None:  # noqa: F821
        """Apply the perturbation and return a :class:`PerturbationRecord`, or ``None``.

        Parameters
        ----------
        prompt:
            The original baseline prompt string.
        prompt_id:
            The source prompt identifier (used to build ``perturbation_id``).
        config:
            Optional operator configuration; defaults to ``PerturbationConfig()``.
        """
        # Lazy import to avoid circular-import issues at module load time
        from apsa.perturbations.perturbation_record import PerturbationRecord

        if config is None:
            config = PerturbationConfig()

        perturbed = self._apply_transform(prompt, config)
        if perturbed is None or perturbed == prompt:
            return None

        ced = char_edit_distance(prompt, perturbed)
        wed = word_edit_distance(prompt, perturbed)
        tokens = changed_tokens(prompt, perturbed)
        risk, risk_reasons = _detector.assess_with_reasons(prompt, perturbed)
        p_type = self.perturbation_type
        char_denominator = max(len(prompt), len(perturbed), 1)
        word_denominator = max(len(prompt.split()), len(perturbed.split()), 1)
        identity = json.dumps(
            {
                "prompt_id": prompt_id,
                "type": p_type,
                "seed": config.seed,
                "params": config.params,
                "original_prompt": prompt,
                "perturbed_prompt": perturbed,
            },
            ensure_ascii=False,
            sort_keys=True,
            default=repr,
        )
        identity_suffix = hashlib.sha256(identity.encode("utf-8")).hexdigest()[:12]

        return PerturbationRecord(
            perturbation_id=f"{prompt_id}__{p_type}__{config.seed}__{identity_suffix}",
            original_prompt=prompt,
            perturbed_prompt=perturbed,
            perturbation_type=p_type,
            changed_tokens=tokens,
            num_changed_characters=ced,
            num_changed_words=wed,
            edit_distance=ced,
            char_edit_distance_normalized=ced / char_denominator,
            word_edit_distance_normalized=wed / word_denominator,
            semantic_risk_level=risk,
            semantic_risk_reasons=risk_reasons,
            is_syntactically_minimal=(p_type in _SURFACE_TYPES),
            is_lexically_minimal=is_lexically_minimal(prompt, perturbed),
            is_semantically_minimal=(risk == SemanticRiskLevel.MINIMAL),
            metadata={
                "seed": config.seed,
                "params": config.params,
                "semantic_risk_method": "rule_based_heuristic",
            },
        )
