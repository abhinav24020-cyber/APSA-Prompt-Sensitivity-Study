"""Input distance sub-package.

Public API
----------
Lexical metrics (character- and word-level edit distances):

    from apsa.metrics.input_distance import (
        LexicalDistanceCalculator,
        LexicalDistanceResult,
    )

Semantic metrics (cosine distance via pluggable embedding model):

    from apsa.metrics.input_distance import (
        SemanticDistanceCalculator,
        SemanticDistanceResult,
        EmbeddingModel,
        SentenceTransformerEmbedder,
    )

Syntactic metrics (dependency-tree edit distance — placeholder for Phase 6+):

    from apsa.metrics.input_distance import (
        SyntacticDistanceCalculator,
        SyntacticDistanceMetrics,
    )
"""

from apsa.metrics.input_distance.lexical import (
    LexicalDistanceCalculator,
    LexicalDistanceResult,
)
from apsa.metrics.input_distance.semantic import (
    EmbeddingModel,
    SemanticDistanceCalculator,
    SemanticDistanceResult,
    SentenceTransformerEmbedder,
)
from apsa.metrics.input_distance.syntactic import (
    SyntacticDistanceCalculator,
    SyntacticDistanceMetrics,
)

__all__ = [
    # Lexical
    "LexicalDistanceCalculator",
    "LexicalDistanceResult",
    # Semantic
    "EmbeddingModel",
    "SemanticDistanceCalculator",
    "SemanticDistanceResult",
    "SentenceTransformerEmbedder",
    # Syntactic (stub)
    "SyntacticDistanceCalculator",
    "SyntacticDistanceMetrics",
]
