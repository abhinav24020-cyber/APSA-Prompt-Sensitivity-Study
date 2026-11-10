"""PerturbationEngine: orchestrates all 10 perturbation operators.

Usage
-----
>>> from apsa.perturbations.engine import PerturbationEngine
>>> engine = PerturbationEngine()
>>> records = engine.apply_all("What is the capital of France?", seed=42)
>>> for r in records:
...     print(r.perturbation_type, "|", r.perturbed_prompt)
"""

from __future__ import annotations

from apsa.perturbations.base_perturbation import PerturbationConfig
from apsa.perturbations.perturbation_record import PerturbationRecord
from apsa.perturbations.registry import get_perturbation

# Default mode selection per perturbation type.
# Each key maps to (perturbation_name, default_params).
_DEFAULT_CONFIGS: list[tuple[str, dict]] = [
    ("char_substitution",      {}),
    ("capitalization",         {"mode": "lowercase_first_word"}),
    ("punctuation",            {"mode": "add_trailing_period"}),
    ("whitespace",             {"mode": "double_space"}),
    ("word_insertion",         {}),
    ("word_deletion",          {}),
    ("word_substitution",      {}),
    ("synonym_replacement",    {}),
    ("instruction_reordering", {}),
    ("formatting_modification",{"mode": "add_please_prefix"}),
]


class PerturbationEngine:
    """Apply all registered perturbation operators to a single prompt.

    Parameters
    ----------
    custom_configs : list of (perturbation_name, params_dict), optional
        Override the default per-operator parameter maps.
    """

    def __init__(
        self,
        custom_configs: list[tuple[str, dict]] | None = None,
    ) -> None:
        source_configs = custom_configs if custom_configs is not None else _DEFAULT_CONFIGS
        self._configs = [(name, dict(params)) for name, params in source_configs]

    def apply_all(
        self,
        prompt: str,
        prompt_id: str = "prompt",
        seed: int = 42,
    ) -> list[PerturbationRecord]:
        """Apply every configured perturbation operator to *prompt*.

        Parameters
        ----------
        prompt : str
            The original baseline prompt string.
        prompt_id : str
            Identifier used for building ``PerturbationRecord.perturbation_id``.
        seed : int
            Global random seed passed to every operator.

        Returns
        -------
        list[PerturbationRecord]
            One record per applicable perturbation. Operators that return ``None``
            because no valid change applies are omitted. Unknown operator names and
            operator errors are surfaced to the caller.
        """
        records: list[PerturbationRecord] = []
        for p_name, params in self._configs:
            operator = get_perturbation(p_name)
            config = PerturbationConfig(params=dict(params), seed=seed)
            record = operator.perturb(prompt, prompt_id=prompt_id, config=config)
            if record is not None:
                records.append(record)
        return records

    def apply_single(
        self,
        prompt: str,
        perturbation_type: str,
        prompt_id: str = "prompt",
        seed: int = 42,
        params: dict | None = None,
    ) -> PerturbationRecord | None:
        """Apply a single named perturbation operator.

        Parameters
        ----------
        perturbation_type : str
            The canonical perturbation name (e.g. ``"capitalization"``).
        params : dict, optional
            Operator-specific parameter overrides.
        """
        operator = get_perturbation(perturbation_type)
        config = PerturbationConfig(params=params or {}, seed=seed)
        return operator.perturb(prompt, prompt_id=prompt_id, config=config)
