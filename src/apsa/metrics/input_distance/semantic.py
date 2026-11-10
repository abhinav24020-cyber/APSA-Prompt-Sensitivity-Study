"""Semantic input distance via a pluggable sentence-embedding interface.

Mathematical definition
-----------------------
Let E: str -> R^d  be an embedding model that maps a text string to a d-dimensional
real-valued vector.

    D_semantic(P, P') = 1 - semantic_similarity(P, P')

where the default similarity function is the cosine similarity:

    semantic_similarity(P, P') = cos(E(P), E(P'))
                                = (E(P) · E(P')) / (‖E(P)‖ · ‖E(P')‖)

Therefore:

    D_semantic(P, P') = 1 - (E(P) · E(P')) / (‖E(P)‖ · ‖E(P')‖)

Range:
  D_semantic ∈ [0, 2]  for general real-valued embeddings.
  D_semantic ∈ [0, 1]  for normalized embeddings (‖E(P)‖ = 1), which is the
  case for most sentence-transformer models (e.g. all-mpnet-base-v2).

Interpretation:
  D_semantic = 0  →  P and P' are semantically identical.
  D_semantic ≈ 0.05  →  Minor paraphrase; meaning largely preserved.
  D_semantic ≈ 0.20  →  Noticeable semantic drift.
  D_semantic = 1  →  Orthogonal embeddings; completely unrelated meaning.

Design: Modular Embedding Interface
------------------------------------
The embedding model is injected via the ``EmbeddingModel`` abstract interface.
This allows the embedding backend to be replaced without modifying any calling
code.  See ``EmbeddingModel`` for the contract and ``SentenceTransformerEmbedder``
for the default implementation.

Threshold note
--------------
No fixed semantic threshold (e.g., D_semantic < 0.05 → "minimal") is applied
in this module.  Any threshold is a research parameter belonging to the
experiment configuration (``EpsilonBudget.semantic_cosine`` in
``apsa.config.schema``).  The raw distance value is always returned so that
callers can apply their own documented thresholds.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Sequence
import math


# ---------------------------------------------------------------------------
# Abstract embedding interface
# ---------------------------------------------------------------------------

class EmbeddingModel(ABC):
    """Interface for a sentence embedding backend.

    Implementors must provide :meth:`encode`, which maps a batch of strings to
    a list of floating-point vectors.  The interface is intentionally minimal so
    that any embedding library (``sentence-transformers``, ``openai``,
    ``cohere``, local GGUF, etc.) can be adapted with a thin wrapper.

    Invariants expected by ``SemanticDistanceCalculator``
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    1. All returned vectors must have the same dimensionality.
    2. Vectors need NOT be pre-normalized; normalization is applied internally.
    3. ``encode`` must be deterministic for the same input text.

    Example — wrapping a custom REST endpoint
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    >>> class MyAPIEmbedder(EmbeddingModel):
    ...     @property
    ...     def model_name(self) -> str:
    ...         return "my-api-v1"
    ...     def encode(self, texts: list[str]) -> list[list[float]]:
    ...         return my_api_client.embed(texts)
    """

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Human-readable identifier of the embedding model.

        Used for experiment tracking and documentation.
        Example: ``"all-mpnet-base-v2"`` or ``"text-embedding-3-small"``.
        """

    @abstractmethod
    def encode(self, texts: list[str]) -> list[list[float]]:
        """Encode a batch of texts and return a list of embedding vectors.

        Parameters
        ----------
        texts:
            Non-empty list of input strings to embed.

        Returns
        -------
        list[list[float]]
            One embedding vector per input string.  All vectors must have
            the same length (embedding dimensionality).
        """


class SentenceTransformerEmbedder(EmbeddingModel):
    """Concrete ``EmbeddingModel`` backed by the ``sentence-transformers`` library.

    Default model: ``all-mpnet-base-v2``
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    - 768-dimensional normalized embeddings.
    - Trained on 1B+ sentence pairs with multiple negative ranking loss.
    - Achieves strong performance on STS benchmarks (Spearman ρ ≈ 0.86 on STS-B).
    - Reference: https://huggingface.co/sentence-transformers/all-mpnet-base-v2

    Alternative models
    ~~~~~~~~~~~~~~~~~~~
    Pass any ``sentence-transformers``-compatible model name to ``__init__``:
      - ``"all-MiniLM-L6-v2"``  — faster (384-d), slightly lower quality.
      - ``"paraphrase-multilingual-mpnet-base-v2"``  — multilingual support.
      - Any HuggingFace model identifier that follows the ST interface.

    Parameters
    ----------
    model_name:
        Sentence-Transformers model identifier.
    device:
        PyTorch device string (``"cpu"``, ``"cuda"``, ``"mps"``).
        Defaults to ``"cpu"`` for reproducibility in unit tests.
    """

    _DEFAULT_MODEL = "all-mpnet-base-v2"

    def __init__(
        self,
        model_name: str = _DEFAULT_MODEL,
        device: str = "cpu",
    ) -> None:
        self._model_name = model_name
        self._device = device
        self._model = None  # lazy-loaded on first encode() call

    @property
    def model_name(self) -> str:
        return self._model_name

    def _load(self) -> None:
        """Lazy-load the SentenceTransformer model on first use."""
        try:
            from sentence_transformers import SentenceTransformer  # type: ignore
        except ModuleNotFoundError as exc:
            raise ImportError(
                "sentence-transformers is required for SemanticDistanceCalculator. "
                "Install it with:  pip install sentence-transformers"
            ) from exc
        self._model = SentenceTransformer(self._model_name, device=self._device)

    def encode(self, texts: list[str]) -> list[list[float]]:
        """Encode texts using the underlying SentenceTransformer model."""
        if self._model is None:
            self._load()
        # show_progress_bar=False keeps output clean during batch processing
        embeddings = self._model.encode(
            texts,
            convert_to_numpy=True,
            show_progress_bar=False,
            normalize_embeddings=True,   # unit-norm → cosine = dot product
        )
        return [vec.tolist() for vec in embeddings]


# ---------------------------------------------------------------------------
# Internal math helpers
# ---------------------------------------------------------------------------

def _dot(a: Sequence[float], b: Sequence[float]) -> float:
    """Dot product of two equal-length sequences."""
    return sum(x * y for x, y in zip(a, b))


def _norm(v: Sequence[float]) -> float:
    """Euclidean norm."""
    return math.sqrt(sum(x * x for x in v))


def _cosine_similarity(a: Sequence[float], b: Sequence[float]) -> float:
    """Cosine similarity ∈ [-1, 1].  Returns 1.0 for identical zero-vectors."""
    na, nb = _norm(a), _norm(b)
    if na == 0.0 or nb == 0.0:
        # Both zero vectors → identical; one zero vector → undefined (return 0 similarity)
        return 1.0 if (na == 0.0 and nb == 0.0) else 0.0
    return _dot(a, b) / (na * nb)


# ---------------------------------------------------------------------------
# Public result type
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class SemanticDistanceResult:
    """Semantic distance metrics for a single (P, P') pair.

    Attributes
    ----------
    cosine_distance : float
        D_semantic(P, P') = 1 - cos(E(P), E(P'))  ∈ [0, 2].
        For unit-norm embeddings (standard sentence-transformers), range is [0, 1].
    cosine_similarity : float
        cos(E(P), E(P'))  ∈ [-1, 1]  (complement of cosine_distance).
    embedding_model : str
        Identifier of the embedding model used, for reproducibility tracking.
    """

    cosine_distance: float
    cosine_similarity: float
    embedding_model: str


# ---------------------------------------------------------------------------
# Public calculator
# ---------------------------------------------------------------------------

class SemanticDistanceCalculator:
    """Compute semantic distance between two prompts via pluggable embedding.

    The embedding model is injected at construction time and can be replaced
    without modifying this class.

    Parameters
    ----------
    embedder:
        Any object satisfying the :class:`EmbeddingModel` interface.
        Defaults to :class:`SentenceTransformerEmbedder` with
        ``all-mpnet-base-v2``.

    Examples
    --------
    Default usage (requires ``sentence-transformers`` installed):

    >>> calc = SemanticDistanceCalculator()
    >>> result = calc.compute("What is the capital of France?",
    ...                       "What is France's capital city?")
    >>> result.cosine_distance  # doctest: +SKIP
    0.043

    Custom embedder:

    >>> class IdentityEmbedder(EmbeddingModel):
    ...     @property
    ...     def model_name(self): return "identity"
    ...     def encode(self, texts): return [[ord(c) for c in t] for t in texts]
    >>> calc = SemanticDistanceCalculator(IdentityEmbedder())
    """

    def __init__(self, embedder: EmbeddingModel | None = None) -> None:
        if embedder is None:
            embedder = SentenceTransformerEmbedder()
        self._embedder = embedder

    @property
    def embedding_model_name(self) -> str:
        """Return the name of the active embedding model."""
        return self._embedder.model_name

    def compute(self, original: str, perturbed: str) -> SemanticDistanceResult:
        """Compute D_semantic(P, P') = 1 - cos(E(P), E(P')).

        Parameters
        ----------
        original:
            The unmodified baseline prompt P.
        perturbed:
            The perturbed prompt P'.

        Returns
        -------
        SemanticDistanceResult
            Frozen dataclass with ``cosine_distance``, ``cosine_similarity``,
            and ``embedding_model`` fields.
        """
        if original == perturbed:
            return SemanticDistanceResult(
                cosine_distance=0.0,
                cosine_similarity=1.0,
                embedding_model=self._embedder.model_name,
            )

        vecs = self._embedder.encode([original, perturbed])
        vec_orig, vec_pert = vecs[0], vecs[1]

        sim = _cosine_similarity(vec_orig, vec_pert)
        # Clamp to valid range to guard against floating-point overshoot
        sim = max(-1.0, min(1.0, sim))
        dist = 1.0 - sim

        return SemanticDistanceResult(
            cosine_distance=round(dist, 8),
            cosine_similarity=round(sim, 8),
            embedding_model=self._embedder.model_name,
        )

    def compute_batch(
        self,
        pairs: list[tuple[str, str]],
    ) -> list[SemanticDistanceResult]:
        """Compute semantic distance for a batch of (original, perturbed) pairs.

        Encodes all unique strings in a single forward pass for efficiency.

        Parameters
        ----------
        pairs:
            List of ``(original, perturbed)`` string tuples.

        Returns
        -------
        list[SemanticDistanceResult]
            One result per input pair, in the same order.
        """
        if not pairs:
            return []

        # Flatten all strings, deduplicate while preserving order
        seen: dict[str, int] = {}
        flat: list[str] = []
        for orig, pert in pairs:
            for s in (orig, pert):
                if s not in seen:
                    seen[s] = len(flat)
                    flat.append(s)

        all_vecs = self._embedder.encode(flat)

        results: list[SemanticDistanceResult] = []
        for orig, pert in pairs:
            if orig == pert:
                results.append(SemanticDistanceResult(
                    cosine_distance=0.0,
                    cosine_similarity=1.0,
                    embedding_model=self._embedder.model_name,
                ))
                continue
            vec_o = all_vecs[seen[orig]]
            vec_p = all_vecs[seen[pert]]
            sim = _cosine_similarity(vec_o, vec_p)
            sim = max(-1.0, min(1.0, sim))
            dist = 1.0 - sim
            results.append(SemanticDistanceResult(
                cosine_distance=round(dist, 8),
                cosine_similarity=round(sim, 8),
                embedding_model=self._embedder.model_name,
            ))
        return results
