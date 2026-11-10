"""T_add: Single-word insertion — inject a low-information filler word.

Inserts one filler word (e.g. 'please', 'carefully', 'simply') at a
seed-determined position.  The inserted word is semantically inert so that
the perturbation remains MINIMAL risk.
"""

from __future__ import annotations

import random

from apsa.perturbations.base_perturbation import BasePerturbation, PerturbationConfig

# Filler words in order of informativeness (least → most).
# The engine selects from these deterministically via seed.
_FILLER_WORDS: list[str] = [
    "please",
    "carefully",
    "simply",
    "basically",
    "clearly",
    "also",
    "kindly",
    "indeed",
    "actually",
    "certainly",
]

# Insertion positions (relative to word list)
# 'start' = before first word, 'after_first' = after 1st word, 'end' = append
_POSITIONS = ["start", "after_first", "end"]


class AdditionPerturbation(BasePerturbation):
    """Insert one low-information filler word at a deterministic position."""

    @property
    def perturbation_type(self) -> str:
        return "word_insertion"

    def _apply_transform(self, prompt: str, config: PerturbationConfig) -> str | None:
        rng = random.Random(config.seed)
        filler = config.params.get("filler_word") or rng.choice(_FILLER_WORDS)
        position = config.params.get("position") or rng.choice(_POSITIONS)

        words = prompt.split()
        if not words:
            return None

        if position == "start":
            words = [filler.capitalize()] + words
        elif position == "after_first":
            words = [words[0], filler] + words[1:]
        else:  # end
            # Strip trailing punctuation, append filler, then re-add punctuation
            if words[-1] and words[-1][-1] in ".?!":
                punct = words[-1][-1]
                words[-1] = words[-1][:-1]
                words.append(filler + punct)
            else:
                words.append(filler)

        result = " ".join(words)
        return result if result != prompt else None
