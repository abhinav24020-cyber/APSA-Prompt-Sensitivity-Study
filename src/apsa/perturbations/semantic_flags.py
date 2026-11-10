"""Conservative, rule-based semantic-risk flags for prompt perturbations.

These heuristics identify some high-risk edits; they do not prove semantic
equivalence. In particular, punctuation, lexical changes, and unknown patterns
are never automatically treated as meaning-preserving.
"""

from __future__ import annotations

import re
from collections import Counter
from enum import Enum


class SemanticRiskLevel(str, Enum):
    MINIMAL = "minimal"
    MODERATE = "moderate"
    HIGH = "high"


# ---------------------------------------------------------------------------
# Keyword tables for rule-based detection
# ---------------------------------------------------------------------------

# Words whose addition or removal is likely to flip meaning
_NEGATION_WORDS: frozenset[str] = frozenset({
    "not", "no", "never", "none", "neither", "nor", "without",
    "cannot", "can't", "don't", "doesn't", "didn't", "isn't",
    "wasn't", "won't", "wouldn't", "shouldn't", "couldn't",
    "hardly", "barely", "scarcely",
})

_QUANTIFIERS: frozenset[str] = frozenset({
    "all", "every", "each", "any", "some", "none", "neither", "either",
    "both", "only", "exactly",
})

# Prefix or word changes that flip polarity
_POLARITY_FLIP_PAIRS: list[tuple[str, str]] = [
    ("correct", "incorrect"),
    ("possible", "impossible"),
    ("relevant", "irrelevant"),
    ("legal", "illegal"),
    ("valid", "invalid"),
    ("complete", "incomplete"),
    ("accurate", "inaccurate"),
    ("agree", "disagree"),
    ("appear", "disappear"),
    ("connect", "disconnect"),
    ("honest", "dishonest"),
    ("happy", "unhappy"),
    ("fair", "unfair"),
    ("true", "false"),
    ("false", "true"),
    ("yes", "no"),
    ("no", "yes"),
    ("always", "never"),
    ("never", "always"),
    ("all", "none"),
    ("none", "all"),
    ("increase", "decrease"),
    ("decrease", "increase"),
    ("before", "after"),
    ("after", "before"),
    ("more", "less"),
    ("less", "more"),
    ("maximum", "minimum"),
    ("minimum", "maximum"),
]

# Build a fast lookup dict in both directions
_POLARITY_MAP: dict[str, str] = {}
for _a, _b in _POLARITY_FLIP_PAIRS:
    _POLARITY_MAP[_a] = _b
    _POLARITY_MAP[_b] = _a

def _tokenize(text: str) -> list[str]:
    """Return case-folded word tokens while keeping contractions intact."""
    return re.findall(r"[a-z0-9]+(?:['’][a-z0-9]+)*", text.casefold().replace("’", "'"))


_NUMBER_PATTERN = re.compile(
    r"(?<!\w)[+-]?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?(?:[eE][+-]?\d+)?%?(?!\w)"
)


class SemanticFlagDetector:
    """Rule-based semantic risk assessor.

    Usage
    -----
    >>> detector = SemanticFlagDetector()
    >>> detector.assess("The answer is correct.", "The answer is incorrect.")
    <SemanticRiskLevel.HIGH: 'high'>

    Design note
    -----------
    All detection is stateless and pure-Python.  To upgrade to embedding-based
    detection, subclass this class and override :meth:`assess`.
    """

    def assess(self, original: str, perturbed: str) -> SemanticRiskLevel:
        """Return a heuristic risk level; this is not a semantic-equivalence claim."""
        return self.assess_with_reasons(original, perturbed)[0]

    def assess_with_reasons(
        self, original: str, perturbed: str
    ) -> tuple[SemanticRiskLevel, list[str]]:
        """Return a conservative risk level and the rule(s) that triggered it.

        Parameters
        ----------
        original:
            The unmodified baseline prompt.
        perturbed:
            The perturbed prompt.

        Returns
        -------
        A risk level and human-readable rationale.
        """
        orig_tokens = _tokenize(original)
        pert_tokens = _tokenize(perturbed)
        orig_set = set(orig_tokens)
        pert_set = set(pert_tokens)
        orig_counter = Counter(orig_tokens)
        pert_counter = Counter(pert_tokens)
        added_multi = set((pert_counter - orig_counter).elements())
        removed_multi = set((orig_counter - pert_counter).elements())

        changed_negations = (added_multi | removed_multi) & _NEGATION_WORDS
        if changed_negations:
            changed = ", ".join(sorted(changed_negations))
            return SemanticRiskLevel.HIGH, [f"Negation token added or removed: {changed}."]

        for word in added_multi:
            if word in _POLARITY_MAP and _POLARITY_MAP[word] in orig_set:
                return SemanticRiskLevel.HIGH, [
                    f"Polarity-related token changed: {_POLARITY_MAP[word]} -> {word}."
                ]
        for word in removed_multi:
            if word in _POLARITY_MAP and _POLARITY_MAP[word] in pert_set:
                return SemanticRiskLevel.HIGH, [
                    f"Polarity-related token changed: {word} -> {_POLARITY_MAP[word]}."
                ]

        changed_quantifiers = (added_multi | removed_multi) & _QUANTIFIERS
        if changed_quantifiers:
            changed = ", ".join(sorted(changed_quantifiers))
            return SemanticRiskLevel.HIGH, [f"Quantifier token added or removed: {changed}."]

        orig_nums = Counter(_NUMBER_PATTERN.findall(original))
        pert_nums = Counter(_NUMBER_PATTERN.findall(perturbed))
        if orig_nums != pert_nums:
            return SemanticRiskLevel.HIGH, ["Numeric value added, removed, or changed."]

        # Case/whitespace-only changes are the sole changes classified as minimal.
        if re.sub(r"\s+", "", original).casefold() == re.sub(r"\s+", "", perturbed).casefold():
            return SemanticRiskLevel.MINIMAL, ["Only case and/or whitespace changed."]

        if added_multi or removed_multi:
            return SemanticRiskLevel.MODERATE, [
                "Lexical change detected; semantic preservation is not established."
            ]
        return SemanticRiskLevel.MODERATE, [
            "Non-lexical text change detected; semantic preservation is not established."
        ]
