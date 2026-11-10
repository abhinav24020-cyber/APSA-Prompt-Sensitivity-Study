"""T_format: Formatting modification perturbation operator.

Applies surface-level presentational changes without altering word content:
  - Adding/removing a 'Please' prefix
  - Converting numbered list items to prose connectors ('1.' -> 'First,')
  - Converting prose connectors to numbered list ('First,' -> '1.')
  - Adding/removing markdown bold markers around the first noun phrase

Supported modes (set via config.params['mode']):
    - 'add_please_prefix'       : Prepend 'Please ' to the prompt (DEFAULT)
    - 'remove_please_prefix'    : Remove a leading 'Please ' if present
    - 'numbered_to_prose'       : '1. ... 2. ...' -> 'First, ... Second, ...'
    - 'prose_to_numbered'       : 'First, ...' -> '1. ...'
"""

from __future__ import annotations

import re

from apsa.perturbations.base_perturbation import BasePerturbation, PerturbationConfig

_ORDINAL_MAP: dict[str, str] = {
    "First": "1", "Second": "2", "Third": "3", "Fourth": "4",
    "Fifth": "5", "Sixth": "6", "Seventh": "7", "Eighth": "8",
}
_NUMBER_MAP: dict[str, str] = {v: k for k, v in _ORDINAL_MAP.items()}


class RephrasingPerturbation(BasePerturbation):
    """Apply formatting modifications to the prompt without changing word content."""

    @property
    def perturbation_type(self) -> str:
        return "formatting_modification"

    def _apply_transform(self, prompt: str, config: PerturbationConfig) -> str | None:
        mode: str = config.params.get("mode", "add_please_prefix")

        if mode == "add_please_prefix":
            if not re.match(r"^[Pp]lease\b", prompt):
                result = "Please " + prompt
                return result if result != prompt else None
            return None

        elif mode == "remove_please_prefix":
            match = re.match(r"^[Pp]lease\s+(.+)$", prompt, re.DOTALL)
            if match:
                return match.group(1)
            return None

        elif mode == "numbered_to_prose":
            # Replace '1. ' with 'First, ', '2. ' with 'Second, ', etc.
            result = prompt
            for num, word in _NUMBER_MAP.items():
                result = re.sub(rf"\b{re.escape(num)}\.\s+", f"{word}, ", result)
            return result if result != prompt else None

        elif mode == "prose_to_numbered":
            # Replace 'First, ' with '1. ', etc.
            result = prompt
            for word, num in _ORDINAL_MAP.items():
                result = re.sub(rf"\b{re.escape(word)},?\s+", f"{num}. ", result)
            return result if result != prompt else None

        else:
            raise ValueError(f"Unknown formatting mode: {mode!r}")
