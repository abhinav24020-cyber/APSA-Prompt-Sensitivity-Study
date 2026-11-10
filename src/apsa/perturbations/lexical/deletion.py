"""T_del: Single-word deletion — remove one non-essential token.

Removes the first occurrence of an article, determiner, or politeness marker
that is safe to drop without changing the core meaning.  Returns ``None``
if no deletable token is found.
"""

from __future__ import annotations

from apsa.perturbations.base_perturbation import BasePerturbation, PerturbationConfig

# Tokens safe to delete (case-insensitive match)
_DELETABLE_TOKENS: list[str] = [
    "the", "a", "an", "please", "kindly", "carefully",
    "simply", "also", "indeed", "certainly",
]


class DeletionPerturbation(BasePerturbation):
    """Remove the first occurrence of a non-essential token in the prompt."""

    @property
    def perturbation_type(self) -> str:
        return "word_deletion"

    def _apply_transform(self, prompt: str, config: PerturbationConfig) -> str | None:
        target = config.params.get("target_word")
        words = prompt.split()

        if target:
            candidates = [target.lower()]
        else:
            candidates = _DELETABLE_TOKENS

        for candidate in candidates:
            for i, word in enumerate(words):
                # Match case-insensitively, stripping trailing punctuation for comparison
                core = word.rstrip(".,?!;:")
                if core.lower() == candidate:
                    suffix = word[len(core):]
                    if suffix and (i != len(words) - 1 or not all(c in ".?!" for c in suffix)):
                        continue
                    new_words = words[:i] + words[i + 1:]
                    if suffix and new_words:
                        new_words[-1] += suffix
                    elif suffix:
                        continue
                    result = " ".join(new_words)
                    return result if result != prompt else None

        return None  # No deletable token found
