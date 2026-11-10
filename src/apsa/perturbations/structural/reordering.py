"""T_reorder: Instruction reordering perturbation operator.

For multi-sentence prompts: swaps the position of the last sentence
(typically the instruction) and the first sentence (typically context).

Returns ``None`` for single-sentence prompts since reordering is undefined.

Supported modes (set via config.params['mode']):
    - 'last_to_first'  : Move last sentence to the beginning (DEFAULT)
    - 'first_to_last'  : Move first sentence to the end
"""

from __future__ import annotations

import re
from apsa.perturbations.base_perturbation import BasePerturbation, PerturbationConfig


def _split_sentences(text: str) -> list[str]:
    """Split on sentence-ending punctuation while keeping the delimiter."""
    # Split on '.', '?', '!' followed by whitespace or end-of-string
    parts = re.split(r'(?<=[.?!])\s+', text.strip())
    return [p.strip() for p in parts if p.strip()]


class ReorderingPerturbation(BasePerturbation):
    """Swap the last instruction sentence with the first context sentence."""

    @property
    def perturbation_type(self) -> str:
        return "instruction_reordering"

    def _apply_transform(self, prompt: str, config: PerturbationConfig) -> str | None:
        mode: str = config.params.get("mode", "last_to_first")
        sentences = _split_sentences(prompt)

        if len(sentences) < 2:
            return None  # Cannot reorder a single-sentence prompt

        if mode == "last_to_first":
            reordered = [sentences[-1]] + sentences[:-1]
        elif mode == "first_to_last":
            reordered = sentences[1:] + [sentences[0]]
        else:
            raise ValueError(f"Unknown reordering mode: {mode!r}")

        result = " ".join(reordered)
        return result if result != prompt else None
