"""Composite output divergence D_out computation.

D_out(Y, Y') = w1 * d_text_out + w2 * d_sem_out + w3 * delta_f_task
"""

from apsa.config.schema import MetricWeights


class CompositeOutputDivergence:
    """Aggregate textual, semantic, and functional metrics into D_out."""

    def __init__(self, weights: MetricWeights) -> None:
        self._weights = weights

    def compute(
        self,
        d_text_out: float,
        d_sem_out: float,
        delta_f_task: float,
    ) -> float:
        """Return composite output divergence D_out."""
        w = self._weights
        return w.w1_textual * d_text_out + w.w2_semantic * d_sem_out + w.w3_functional * delta_f_task
