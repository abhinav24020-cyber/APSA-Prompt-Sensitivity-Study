"""Syntactic input distance via dependency-tree edit distance (not implemented).

Mathematical definition
-----------------------
Let T(P)  = dependency parse tree of prompt P  (produced by spaCy).
Let T(P') = dependency parse tree of perturbed prompt P'.

The APTED (All-Path Tree Edit Distance) algorithm computes the minimum-cost
sequence of node insertions, deletions, and relabellings to transform T(P)
into T(P'):

    TED(P, P') = APTED(T(P), T(P'))

Normalized tree edit distance:

    d_syn(P, P') = TED(P, P') / max(|T(P)|, |T(P')|)

where |T| is the number of nodes (tokens) in the dependency tree.

Range: d_syn ∈ [0, 1].  d_syn = 0 iff the dependency structures are identical.

Implementation status
---------------------
This module is a typed stub. Calling ``compute()`` raises
``NotImplementedError`` with a descriptive message. The metric is not included
in empirically computed composite input distances.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SyntacticDistanceMetrics:
    """Syntactic distance metrics for a single (P, P') pair.

    Attributes
    ----------
    tree_edit_distance : float
        Normalized TED ∈ [0, 1] between the spaCy dependency parse trees.
    """

    tree_edit_distance: float


class SyntacticDistanceCalculator:
    """Compute normalized dependency-tree edit distance between two prompts.

    Parameters
    ----------
    spacy_model:
        spaCy model name to use for dependency parsing (e.g. ``en_core_web_sm``).

    Notes
    -----
    Requires ``spacy`` and a model to be installed::

        pip install spacy
        python -m spacy download en_core_web_sm

    APTED algorithm reference:
        Pawlik & Augsten (2016). "Efficient Computation of the Tree Edit Distance."
        ACM Transactions on Database Systems (TODS).
    """

    def __init__(self, spacy_model: str = "en_core_web_sm") -> None:
        self._spacy_model = spacy_model
        # spaCy model loaded lazily on first compute() call
        self._nlp = None

    def compute(self, original: str, perturbed: str) -> SyntacticDistanceMetrics:
        """Compute normalized TED between dependency parse trees.

        .. note::
            Not yet implemented. A future implementation would load a spaCy
            dependency parser and apply the APTED algorithm.

        Raises
        ------
        NotImplementedError
            Always raised until Phase 6 implementation is complete.
        """
        raise NotImplementedError(
            "SyntacticDistanceCalculator.compute() is not yet implemented. "
            "Syntactic tree edit distance is not implemented; no value was computed."
        )
