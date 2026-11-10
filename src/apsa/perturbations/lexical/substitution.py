"""T_sub: Single-word substitution with a curated contextual alternative.

Uses a static substitution table of safe near-neutral word pairs.
Polarity-flipping substitutions (e.g. 'correct' -> 'incorrect') ARE included
but are flagged as HIGH semantic risk by the SemanticFlagDetector automatically.

The substitution is always exactly one word replaced with one word.
"""

from __future__ import annotations

import random
import re
from apsa.perturbations.base_perturbation import BasePerturbation, PerturbationConfig

# Static substitution table: original -> substitute
# Grouped by risk level for documentation clarity.
#
# MODERATE-risk substitutions (wording change, intent preserved):
_SUBSTITUTION_TABLE: dict[str, str] = {
    # Verbs
    "calculate": "compute",
    "compute": "calculate",
    "determine": "find",
    "find": "determine",
    "explain": "describe",
    "describe": "explain",
    "write": "create",
    "create": "write",
    "provide": "give",
    "give": "provide",
    "show": "demonstrate",
    "demonstrate": "show",
    "identify": "detect",
    "detect": "identify",
    "evaluate": "assess",
    "assess": "evaluate",
    # Adjectives (neutral swap)
    "simple": "straightforward",
    "straightforward": "simple",
    "clear": "concise",
    "concise": "clear",
    "precise": "exact",
    "exact": "precise",
    "standard": "typical",
    "typical": "standard",
    # HIGH-risk substitutions (polarity flip — automatically flagged by SemanticFlagDetector)
    "correct": "incorrect",
    "incorrect": "correct",
    "valid": "invalid",
    "invalid": "valid",
    "possible": "impossible",
    "impossible": "possible",
    "true": "false",
    "false": "true",
}


class SubstitutionPerturbation(BasePerturbation):
    """Replace one content word with an entry from the static substitution table.

    Config params
    -------------
    seed : int
        Selects which occurrence to substitute when multiple candidates exist.
    target_word : str (optional)
        If set, only this specific word is replaced (must be in _SUBSTITUTION_TABLE).
    """

    @property
    def perturbation_type(self) -> str:
        return "word_substitution"

    def _apply_transform(self, prompt: str, config: PerturbationConfig) -> str | None:
        target = config.params.get("target_word")
        rng = random.Random(config.seed)

        # Find all substitutable word occurrences
        candidates: list[tuple[int, str, str]] = []  # (start, original_word, replacement)

        for match in re.finditer(r"\b[a-zA-Z]+\b", prompt):
            word = match.group()
            word_lower = word.lower()
            if target:
                if word_lower != target.lower():
                    continue
            if word_lower in _SUBSTITUTION_TABLE:
                replacement = _SUBSTITUTION_TABLE[word_lower]
                # Preserve original capitalisation
                if word[0].isupper():
                    replacement = replacement.capitalize()
                candidates.append((match.start(), word, replacement))

        if not candidates:
            return None

        start, original, replacement = rng.choice(candidates)
        result = prompt[:start] + replacement + prompt[start + len(original):]
        return result if result != prompt else None
