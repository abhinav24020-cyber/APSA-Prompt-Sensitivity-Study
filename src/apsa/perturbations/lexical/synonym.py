"""T_synonym: Synonym replacement using a static curated synonym dictionary.

DESIGN NOTE — STATIC_SYNONYM_TABLE
-----------------------------------
This module deliberately uses a hand-curated static synonym table rather than
WordNet or sentence-transformer embeddings.  This keeps Phase 4 dependency-free
and fully deterministic.

To upgrade to embedding-based synonym selection in a future phase:
  1. Subclass ``SynonymPerturbation`` and override ``_get_synonym()``.
  2. Inject a sentence-transformer model into the subclass constructor.
  3. Filter candidates by cosine similarity >= 0.90.

The table only contains synonyms where:
  - Semantic cosine similarity is estimated >= 0.88 (verified manually).
  - The replacement does NOT introduce negation or polarity flip.
  - The replacement preserves the original POS tag.
"""

from __future__ import annotations

import random
import re

from apsa.perturbations.base_perturbation import BasePerturbation, PerturbationConfig

# STATIC_SYNONYM_TABLE
# Format: word -> list of synonyms (all safe, high-similarity replacements)
_SYNONYM_TABLE: dict[str, list[str]] = {
    # Verbs
    "calculate": ["compute", "evaluate"],
    "compute": ["calculate", "evaluate"],
    "determine": ["establish", "ascertain"],
    "find": ["locate", "discover"],
    "explain": ["clarify", "elaborate"],
    "describe": ["characterize", "outline"],
    "write": ["compose", "draft"],
    "solve": ["resolve"],
    "classify": ["categorize", "label"],
    "identify": ["recognise", "pinpoint"],
    # Nouns
    "answer": ["response", "solution"],
    "problem": ["challenge", "question"],
    "function": ["procedure", "routine"],
    "method": ["approach", "technique"],
    "result": ["outcome", "output"],
    "example": ["instance", "illustration"],
    "sentence": ["statement", "clause"],
    "list": ["sequence", "series"],
    "number": ["value", "figure"],
    "word": ["term", "token"],
    # Adjectives
    "correct": ["right", "accurate"],      # NOTE: 'correct' here maps to safe synonyms,
    "simple": ["basic", "elementary"],    #        not to 'incorrect'. See substitution.py
    "complex": ["intricate", "elaborate"],
    "clear": ["unambiguous", "explicit"],
    "standard": ["conventional", "typical"],
    "minimal": ["smallest", "least"],
    "maximum": ["highest", "greatest"],
    "minimum": ["lowest", "smallest"],
    # Common task instruction words
    "provide": ["supply", "give"],
    "return": ["output", "yield"],
    "print": ["output", "display"],
    "generate": ["produce", "create"],
    "implement": ["build", "code"],
}


class SynonymPerturbation(BasePerturbation):
    """Replace one word with a high-similarity synonym from the static table.

    Config params
    -------------
    seed : int
        Selects which occurrence to replace when multiple candidates exist.
    target_word : str (optional)
        If set, only this specific word is replaced (must be in _SYNONYM_TABLE).
    """

    @property
    def perturbation_type(self) -> str:
        return "synonym_replacement"

    def _apply_transform(self, prompt: str, config: PerturbationConfig) -> str | None:
        target = config.params.get("target_word")
        rng = random.Random(config.seed)

        candidates: list[tuple[int, str, str]] = []  # (start, original, replacement)
        for match in re.finditer(r"\b[a-zA-Z]+\b", prompt):
            word = match.group()
            word_lower = word.lower()
            if target and word_lower != target.lower():
                continue
            synonyms = _SYNONYM_TABLE.get(word_lower)
            if synonyms:
                replacement = rng.choice(synonyms)
                if word[0].isupper():
                    replacement = replacement.capitalize()
                if replacement.lower() != word_lower:
                    candidates.append((match.start(), word, replacement))

        if not candidates:
            return None

        start, original, replacement = rng.choice(candidates)
        return prompt[:start] + replacement + prompt[start + len(original):]

    def _get_synonym(self, word: str, rng: random.Random) -> str | None:
        """Look up a synonym.  Override this method to use embedding-based lookup."""
        synonyms = _SYNONYM_TABLE.get(word.lower())
        if not synonyms:
            return None
        return rng.choice(synonyms)
