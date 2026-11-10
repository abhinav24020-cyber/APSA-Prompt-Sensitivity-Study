"""T_cap: Capitalization alteration perturbation operator.

Supported modes (set via config.params['mode']):
    - 'uppercase_first_word'  : Capitalize the first word entirely (DEFAULT)
    - 'lowercase_first_word'  : Lowercase the first character of the prompt
    - 'title_case' / 'titlecase': Apply title-case to all words
    - 'all_uppercase' / 'uppercase': Uppercase every alphabetic character
    - 'all_lowercase' / 'lowercase': Lowercase every alphabetic character
"""

from __future__ import annotations

from apsa.perturbations.base_perturbation import BasePerturbation, PerturbationConfig


class CapitalizationPerturbation(BasePerturbation):
    """Alters casing of the prompt without changing any words or punctuation."""

    @property
    def perturbation_type(self) -> str:
        return "capitalization"

    def _apply_transform(self, prompt: str, config: PerturbationConfig) -> str | None:
        raw_mode: str = config.params.get("mode", "lowercase_first_word")

        # Normalize mode aliases
        mode_map = {
            "uppercase": "all_uppercase",
            "lowercase": "all_lowercase",
            "titlecase": "title_case",
        }
        mode = mode_map.get(raw_mode, raw_mode)

        if mode == "uppercase_first_word":
            words = prompt.split()
            if not words:
                return None
            result = words[0].upper() + (" " + " ".join(words[1:]) if len(words) > 1 else "")
            return result if result != prompt else None

        elif mode == "lowercase_first_word":
            if not prompt:
                return None
            result = prompt[0].lower() + prompt[1:]
            return result if result != prompt else None

        elif mode == "title_case":
            result = prompt.title()
            return result if result != prompt else None

        elif mode == "all_uppercase":
            result = prompt.upper()
            return result if result != prompt else None

        elif mode == "all_lowercase":
            result = prompt.lower()
            return result if result != prompt else None

        else:
            raise ValueError(f"Unknown capitalization mode: {raw_mode!r}")
