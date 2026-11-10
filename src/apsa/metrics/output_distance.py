"""Output Distance Metrics.

Implements multiple measures of output change between original and perturbed outputs.
"""
import Levenshtein
from typing import Optional, List, Tuple
try:
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity
    HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    HAS_SENTENCE_TRANSFORMERS = False

class OutputDeviationMetrics:
    def __init__(self, use_semantic: bool = True, model_name: str = 'all-MiniLM-L6-v2'):
        self.use_semantic = use_semantic and HAS_SENTENCE_TRANSFORMERS
        if self.use_semantic:
            self.encoder = SentenceTransformer(model_name)
        else:
            self.encoder = None

    def exact_match(self, o1: Optional[str], o2: Optional[str]) -> bool:
        if o1 is None or o2 is None:
            return False
        return o1.strip() == o2.strip()

    def normalized_string_similarity(self, o1: Optional[str], o2: Optional[str]) -> float:
        if o1 is None or o2 is None:
            return 0.0
        if not o1 and not o2:
            return 1.0
        dist = Levenshtein.distance(o1, o2)
        max_len = max(len(o1), len(o2))
        if max_len == 0:
            return 1.0
        return max(0.0, min(1.0, 1.0 - (dist / max_len)))

    def normalized_character_distance(self, o1: Optional[str], o2: Optional[str]) -> float:
        """D_char_norm = 1.0 - normalized_string_similarity."""
        if o1 is None or o2 is None:
            return 1.0
        return max(0.0, min(1.0, 1.0 - self.normalized_string_similarity(o1, o2)))

    def character_level_distance(self, o1: Optional[str], o2: Optional[str]) -> int:
        if o1 is None or o2 is None:
            return -1
        return Levenshtein.distance(o1, o2)

    def token_level_distance(self, o1: Optional[str], o2: Optional[str]) -> float:
        """Calculates token-level Jaccard distance."""
        if o1 is None or o2 is None:
            return 1.0
        tokens1 = set(o1.split())
        tokens2 = set(o2.split())
        
        intersection = tokens1.intersection(tokens2)
        union = tokens1.union(tokens2)
        
        if not union:
            return 0.0
            
        jaccard_sim = len(intersection) / len(union)
        return max(0.0, min(1.0, 1.0 - jaccard_sim))

    def semantic_similarity(self, o1: Optional[str], o2: Optional[str]) -> float:
        """Returns semantic similarity using Sentence Transformers if available, else falls back to normalized string similarity."""
        if o1 is None or o2 is None:
            return 0.0
        if not self.use_semantic:
            return self.normalized_string_similarity(o1, o2)
            
        if not o1.strip() and not o2.strip():
            return 1.0
        if not o1.strip() or not o2.strip():
            return 0.0
            
        embeddings = self.encoder.encode([o1, o2])
        sim = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
        # Clip to [0, 1] bounds in case of slight floating point inaccuracies
        return float(max(0.0, min(1.0, sim)))

    def semantic_output_distance(self, o1: Optional[str], o2: Optional[str]) -> float:
        """D_output = 1 - semantic_similarity(O, O')"""
        if o1 is None or o2 is None:
            return 1.0
        return max(0.0, min(1.0, 1.0 - self.semantic_similarity(o1, o2)))

    def compute_all(self, o1: Optional[str], o2: Optional[str]) -> dict:
        is_valid = o1 is not None and o2 is not None
        if not is_valid:
            return {
                "is_valid": False,
                "exact_match": False,
                "normalized_string_similarity": 0.0,
                "normalized_character_distance": 1.0,
                "character_level_distance": -1,
                "token_level_distance": 1.0,
                "semantic_similarity": 0.0,
                "semantic_output_distance": 1.0,
                "error": "One or both outputs are None / failed model responses"
            }
        is_empty_pair = (not o1.strip() and not o2.strip())
        return {
            "is_valid": True,
            "is_empty_pair": is_empty_pair,
            "exact_match": self.exact_match(o1, o2),
            "normalized_string_similarity": self.normalized_string_similarity(o1, o2),
            "normalized_character_distance": self.normalized_character_distance(o1, o2),
            "character_level_distance": self.character_level_distance(o1, o2),
            "token_level_distance": self.token_level_distance(o1, o2),
            "semantic_similarity": self.semantic_similarity(o1, o2),
            "semantic_output_distance": self.semantic_output_distance(o1, o2)
        }

class CorrectnessEvaluator:
    @staticmethod
    def evaluate_classification(is_correct_before: Optional[bool], is_correct_after: Optional[bool]) -> str:
        if is_correct_before is None or is_correct_after is None:
            return "unknown / unevaluated"
        if is_correct_before and not is_correct_after:
            return "correct -> incorrect"
        elif not is_correct_before and is_correct_after:
            return "incorrect -> correct"
        else:
            return "same class"

    @staticmethod
    def evaluate_reasoning(is_correct_before: Optional[bool], is_correct_after: Optional[bool]) -> str:
        if is_correct_before is None or is_correct_after is None:
            return "unknown / unevaluated"
        if is_correct_before and not is_correct_after:
            return "correct -> incorrect"
        elif not is_correct_before and is_correct_after:
            return "incorrect -> correct"
        else:
            return "same answer"
