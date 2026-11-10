"""T_space: Whitespace and formatting modification operator.

Supported modes (set via config.params['mode']):
    - 'double_space'    : Replace all single spaces with double spaces (DEFAULT)
    - 'trailing_space'  : Append a single trailing space
    - 'leading_space'   : Prepend a single leading space
    - 'tab_indent'      : Prepend a tab character
    - 'add_newline'     : Append a newline character at the end
    - 'compress_spaces' : Collapse all multi-spaces to single spaces (normalise)
"""

from __future__ import annotations

import re
from apsa.perturbations.base_perturbation import BasePerturbation, PerturbationConfig


class WhitespacePerturbation(BasePerturbation):
    """Injects or removes whitespace without changing any word content."""

    @property
    def perturbation_type(self) -> str:
        return "whitespace"

    def _apply_transform(self, prompt: str, config: PerturbationConfig) -> str | None:
        mode: str = config.params.get("mode", "double_space")

        if mode == "double_space":
            if "  " not in prompt:
                result = prompt.replace(" ", "  ")
                return result if result != prompt else None
            return None

        elif mode == "trailing_space":
            if not prompt.endswith(" "):
                return prompt + " "
            return None

        elif mode == "leading_space":
            if not prompt.startswith(" "):
                return " " + prompt
            return None

        elif mode == "tab_indent":
            if not prompt.startswith("\t"):
                return "\t" + prompt
            return None

        elif mode == "add_newline":
            if not prompt.endswith("\n"):
                return prompt + "\n"
            return None

        elif mode == "compress_spaces":
            result = re.sub(r"  +", " ", prompt)
            return result if result != prompt else None

        else:
            raise ValueError(f"Unknown whitespace mode: {mode!r}")
