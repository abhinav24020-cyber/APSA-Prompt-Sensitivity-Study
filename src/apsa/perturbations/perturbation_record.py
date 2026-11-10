"""PerturbationRecord: the canonical output of every perturbation operator."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from apsa.perturbations.semantic_flags import SemanticRiskLevel


@dataclass
class PerturbationRecord:
    """Full record produced by a single perturbation operator application.

    Fields
    ------
    perturbation_id : str
        Stable identifier derived from prompt ID, operator, seed, parameters, and variant.
    original_prompt : str
        The unmodified baseline prompt.
    perturbed_prompt : str
        The generated candidate prompt.
    perturbation_type : str
        Canonical operator name (e.g., ``"capitalization"``, ``"word_deletion"``).
    changed_tokens : list[str]
        The specific word tokens that were added, removed, or changed.
    num_changed_characters : int
        Character-level Levenshtein distance between original and perturbed.
    num_changed_words : int
        Word-level edit distance between original and perturbed.
    char_edit_distance_normalized : float
        Character edit distance divided by the longer prompt length.
    word_edit_distance_normalized : float
        Word edit distance divided by the longer token count.
    edit_distance : int
        Raw character Levenshtein edit distance (same as num_changed_characters).
    semantic_risk_level : SemanticRiskLevel
        Conservative rule-based semantic risk flag, not a semantic-equivalence result.
    semantic_risk_reasons : list[str]
        Human-readable heuristic rule(s) that assigned the risk level.
    is_syntactically_minimal : bool
        Operator-level flag for case/whitespace transformations; no syntax parser is used.
    is_lexically_minimal : bool
        True iff the normalised word edit distance ≤ 0.15.
    is_semantically_minimal : bool
        True iff the heuristic only detects case/whitespace changes; not proof of equivalence.
    metadata : dict
        Operator-specific additional information (e.g., substitution mode, position).
    """

    perturbation_id: str
    original_prompt: str
    perturbed_prompt: str
    perturbation_type: str
    changed_tokens: list[str]
    num_changed_characters: int
    num_changed_words: int
    edit_distance: int
    char_edit_distance_normalized: float
    word_edit_distance_normalized: float
    semantic_risk_level: SemanticRiskLevel
    semantic_risk_reasons: list[str]
    is_syntactically_minimal: bool
    is_lexically_minimal: bool
    is_semantically_minimal: bool
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialise to a flat dictionary suitable for CSV / JSON export."""
        return {
            "perturbation_id": self.perturbation_id,
            "original_prompt": self.original_prompt,
            "perturbed_prompt": self.perturbed_prompt,
            "perturbation_type": self.perturbation_type,
            "changed_tokens": "|".join(self.changed_tokens),
            "num_changed_characters": self.num_changed_characters,
            "num_changed_words": self.num_changed_words,
            "edit_distance": self.edit_distance,
            "char_edit_distance_normalized": self.char_edit_distance_normalized,
            "word_edit_distance_normalized": self.word_edit_distance_normalized,
            "semantic_risk_level": self.semantic_risk_level.value,
            "semantic_risk_reasons": self.semantic_risk_reasons,
            "is_syntactically_minimal": self.is_syntactically_minimal,
            "is_lexically_minimal": self.is_lexically_minimal,
            "is_semantically_minimal": self.is_semantically_minimal,
            "metadata": self.metadata,
        }
