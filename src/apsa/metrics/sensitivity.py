"""Sensitivity Coefficient computation.

S(X, X'; M) = D_out / max(eta, d_input_composite)

where d_input_composite = alpha * d_lex + beta * d_sem + gamma * d_syn
"""

from apsa.config.schema import MetricWeights, CompositeInputWeights


class SensitivityCalculator:
    """Compute the Sensitivity Coefficient S for a paired trial."""

    def __init__(
        self,
        weights: MetricWeights,
        input_weights: CompositeInputWeights,
    ) -> None:
        self._weights = weights
        self._input_weights = input_weights

    def compute(
        self,
        d_out_composite: float,
        d_lex_in: float,
        d_sem_in: float,
        d_syn_in: float,
    ) -> float:
        """Return S = D_out / max(eta, alpha*d_lex + beta*d_sem + gamma*d_syn)."""
        d_in = (
            self._input_weights.alpha_lexical * d_lex_in
            + self._input_weights.beta_semantic * d_sem_in
            + self._input_weights.gamma_syntactic * d_syn_in
        )
        denominator = max(self._weights.eta, d_in)
        return round(d_out_composite / denominator, 6)
