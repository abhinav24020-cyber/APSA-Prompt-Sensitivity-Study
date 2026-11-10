"""Perturbation operator registry — maps canonical names to operator classes."""

from .base_perturbation import BasePerturbation
from .surface.char_substitution import CharSubstitutionPerturbation
from .surface.capitalization import CapitalizationPerturbation
from .surface.punctuation import PunctuationPerturbation
from .surface.whitespace import WhitespacePerturbation
from .lexical.addition import AdditionPerturbation
from .lexical.deletion import DeletionPerturbation
from .lexical.substitution import SubstitutionPerturbation
from .lexical.synonym import SynonymPerturbation
from .structural.reordering import ReorderingPerturbation
from .syntactic.rephrasing import RephrasingPerturbation
from .random_edit import RandomEditPerturbation

_REGISTRY: dict[str, type[BasePerturbation]] = {
    # Surface (syntactically minimal by definition)
    "char_substitution":       CharSubstitutionPerturbation,
    "capitalization":          CapitalizationPerturbation,
    "punctuation":             PunctuationPerturbation,
    "whitespace":              WhitespacePerturbation,
    # Lexical
    "word_insertion":          AdditionPerturbation,
    "word_deletion":           DeletionPerturbation,
    "word_substitution":       SubstitutionPerturbation,
    "synonym_replacement":     SynonymPerturbation,
    "synonym":                 SynonymPerturbation,
    # Structural / Syntactic
    "instruction_reordering":  ReorderingPerturbation,
    "formatting_modification": RephrasingPerturbation,
    # Control condition
    "random_edit":             RandomEditPerturbation,
}

# Exported for engine iteration
REGISTRY_KEYS: list[str] = list(_REGISTRY.keys())


def get_perturbation(name: str) -> BasePerturbation:
    """Return an instantiated perturbation operator for the given canonical name."""
    if name not in _REGISTRY:
        raise KeyError(
            f"Unknown perturbation '{name}'. Available: {REGISTRY_KEYS}"
        )
    return _REGISTRY[name]()
