from typing import Optional, Union, Dict, Any
from apsa.config.schema import EpsilonBudget
from apsa.metrics.input_distance.lexical import LexicalDistanceResult
from apsa.metrics.input_distance.semantic import SemanticDistanceResult
from apsa.logging_.structured_logger import get_logger

logger = get_logger(__name__)


class BudgetEnforcer:
    """Validates that a perturbed prompt does not exceed the epsilon budget.

    Returns ``True`` if the perturbation is within budget, ``False``
    otherwise.  Violations are logged at WARNING level.
    """

    def __init__(self, budget: EpsilonBudget) -> None:
        self._budget = budget

    def is_within_budget(
        self,
        lexical_result: Optional[Union[LexicalDistanceResult, Dict[str, Any]]] = None,
        semantic_result: Optional[Union[SemanticDistanceResult, Dict[str, Any]]] = None,
        syntactic_ted: Optional[float] = None,
        original_prompt: Optional[str] = None,
        perturbed_prompt: Optional[str] = None,
        run_id: str = "unknown",
    ) -> bool:
        """Return True if all provided distance dimensions are within epsilon limits."""
        within_budget = True

        if lexical_result is not None:
            if isinstance(lexical_result, LexicalDistanceResult):
                char_norm = lexical_result.char_levenshtein_normalized
                if original_prompt and perturbed_prompt:
                    denom = max(len(original_prompt.split()), len(perturbed_prompt.split()), 1)
                    word_norm = lexical_result.word_levenshtein / denom
                else:
                    word_norm = 0.0  # Cannot normalize without word count
            elif isinstance(lexical_result, dict):
                char_norm = lexical_result.get("char_levenshtein_normalized", 0.0)
                word_norm = lexical_result.get("word_levenshtein_normalized", 0.0)
            else:
                char_norm = getattr(lexical_result, "char_levenshtein_normalized", 0.0)
                word_norm = getattr(lexical_result, "word_levenshtein_normalized", 0.0)

            if char_norm > self._budget.lexical_char_normalized:
                logger.warning(
                    f"[{run_id}] Lexical char budget exceeded: {char_norm:.4f} > {self._budget.lexical_char_normalized}"
                )
                within_budget = False

            if word_norm > self._budget.lexical_word_normalized:
                logger.warning(
                    f"[{run_id}] Lexical word budget exceeded: {word_norm:.4f} > {self._budget.lexical_word_normalized}"
                )
                within_budget = False

        if semantic_result is not None:
            if isinstance(semantic_result, SemanticDistanceResult):
                sem_dist = semantic_result.cosine_distance
            elif isinstance(semantic_result, dict):
                sem_dist = semantic_result.get("cosine_distance", 0.0)
            else:
                sem_dist = getattr(semantic_result, "cosine_distance", 0.0)

            if sem_dist > self._budget.semantic_cosine:
                logger.warning(
                    f"[{run_id}] Semantic budget exceeded: {sem_dist:.4f} > {self._budget.semantic_cosine}"
                )
                within_budget = False

        if syntactic_ted is not None:
            if syntactic_ted > self._budget.syntactic_ted_normalized:
                logger.warning(
                    f"[{run_id}] Syntactic TED budget exceeded: {syntactic_ted:.4f} > {self._budget.syntactic_ted_normalized}"
                )
                within_budget = False

        return within_budget
