"""T_punct: Punctuation modification perturbation operator.

Supported modes (set via config.params['mode']):
    - 'add_trailing_period' / 'add_period'    : Append '.' if prompt doesn't end with punctuation (DEFAULT)
    - 'remove_trailing_period' / 'remove_period' : Remove trailing '.' or '?' or '!'
    - 'add_trailing_question'  : Replace final '.' with '?'
    - 'add_comma'              : Insert a comma after the first clause
    - 'remove_comma'           : Remove the first comma found in the prompt
    - 'add_exclamation'        : Replace trailing '.' or '?' with '!'
"""

from __future__ import annotations

import re
from apsa.perturbations.base_perturbation import BasePerturbation, PerturbationConfig


class PunctuationPerturbation(BasePerturbation):
    """Adds or removes punctuation marks without changing any words."""

    @property
    def perturbation_type(self) -> str:
        return "punctuation"

    def _apply_transform(self, prompt: str, config: PerturbationConfig) -> str | None:
        raw_mode: str = config.params.get("mode", "add_trailing_period")

        mode_map = {
            "add_period": "add_trailing_period",
            "remove_period": "remove_trailing_period",
        }
        mode = mode_map.get(raw_mode, raw_mode)

        if mode == "add_trailing_period":
            if prompt and prompt[-1] not in ".?!":
                return prompt + "."
            return None

        elif mode == "remove_trailing_period":
            if prompt and prompt[-1] in ".?!":
                return prompt[:-1].rstrip()
            return None

        elif mode == "add_trailing_question":
            if prompt and prompt[-1] == ".":
                return prompt[:-1] + "?"
            elif prompt and prompt[-1] not in "?!":
                return prompt + "?"
            return None

        elif mode == "add_comma":
            words = prompt.split()
            if len(words) >= 4 and "," not in prompt[:len(" ".join(words[:3]))]:
                insert_at = len(words[0]) + 1 + len(words[1]) + 1 + len(words[2])
                result = prompt[:insert_at] + "," + prompt[insert_at:]
                return result if result != prompt else None
            return None

        elif mode == "remove_comma":
            if "," in prompt:
                idx = prompt.index(",")
                result = prompt[:idx] + prompt[idx + 1:]
                return result.replace("  ", " ")
            return None

        elif mode == "add_exclamation":
            if prompt and prompt[-1] in ".?":
                return prompt[:-1] + "!"
            elif prompt and prompt[-1] != "!":
                return prompt + "!"
            return None

        else:
            raise ValueError(f"Unknown punctuation mode: {raw_mode!r}")
