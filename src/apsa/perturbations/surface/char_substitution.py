"""T_char_sub: Single character substitution perturbation operator.

Replaces one character in a non-critical word with a visually similar or
adjacent-keyboard character (e.g. 'o' -> '0', 'a' -> '@', 'e' -> '3').

Critical words (negation, numbers, polarity-flipper words) are skipped
to ensure the substitution stays syntactically and lexically minimal.
"""

from __future__ import annotations

import random
import re
from apsa.perturbations.base_perturbation import BasePerturbation, PerturbationConfig


# Map of char -> visually-similar substitute (leet-style, keyboard-adjacent)
_CHAR_SUBS: dict[str, str] = {
    "a": "@", "e": "3", "i": "1", "o": "0", "s": "5",
    "l": "1", "g": "9", "b": "6", "t": "+",
}

# Words that must NOT be touched (negations, quantifiers, critical determiners)
_PROTECTED_WORDS: frozenset[str] = frozenset({
    "not", "no", "nor", "never", "none", "without",
    "cannot", "true", "false", "all", "any", "every",
    "more", "less", "both", "either", "neither",
    "always", "only", "just", "yes",
})


class CharSubstitutionPerturbation(BasePerturbation):
    """Replace one character in a content word with a visually similar alternative.

    Config params
    -------------
    seed : int
        Random seed for deterministic word/character selection.
    """

    @property
    def perturbation_type(self) -> str:
        return "char_substitution"

    def _apply_transform(self, prompt: str, config: PerturbationConfig) -> str | None:
        seed = config.seed

        # Find candidate words: alpha-only, length >= 3, not protected
        words = re.findall(r"\b[a-zA-Z]{3,}\b", prompt)
        candidates: list[tuple[int, str]] = []  # (start_index, word)

        pos = 0
        for word in words:
            idx = prompt.find(word, pos)
            if idx == -1:
                continue
            pos = idx + len(word)
            if word.lower() not in _PROTECTED_WORDS:
                # Check if word has at least one substitutable char
                if any(c.lower() in _CHAR_SUBS for c in word):
                    candidates.append((idx, word))

        if not candidates:
            return None

        rng = random.Random(seed)
        start, word = rng.choice(candidates)

        # Find substitutable positions within the word
        sub_positions = [i for i, c in enumerate(word) if c.lower() in _CHAR_SUBS]
        char_pos = rng.choice(sub_positions)
        original_char = word[char_pos]
        replacement = _CHAR_SUBS[original_char.lower()]
        # Preserve case
        if original_char.isupper():
            replacement = replacement.upper()

        new_word = word[:char_pos] + replacement + word[char_pos + 1:]
        return prompt[:start] + new_word + prompt[start + len(word):]
