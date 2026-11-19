"""Extreme Value Theory (EVT) tail-risk analysis.

Fits a Generalized Extreme Value (GEV) distribution to the values at or above the 95th
percentile of the Sensitivity Coefficient S (methodology section 12.4). With small tails
the fit is unstable, so callers must report the tail size alongside the parameters.
"""

from dataclasses import dataclass

import numpy as np


@dataclass
class EVTResult:
    shape: float      # GEV shape parameter in scipy's convention (c = -xi)
    loc: float        # GEV location parameter (mu)
    scale: float      # GEV scale parameter (sigma)
    threshold: float  # percentile threshold used
    n_tail: int = 0


class ExtremeValueAnalyzer:
    """Fit a GEV distribution to upper-tail sensitivity coefficients."""

    def __init__(self, quantile: float = 0.95, min_tail: int = 10) -> None:
        self.quantile = quantile
        self.min_tail = min_tail

    def fit(self, sensitivity_coefficients: list[float]) -> EVTResult:
        from scipy.stats import genextreme

        values = np.asarray([v for v in sensitivity_coefficients if np.isfinite(v)], dtype=float)
        if len(values) == 0:
            raise ValueError("No finite sensitivity coefficients")
        threshold = float(np.quantile(values, self.quantile))
        tail = values[values >= threshold]
        if len(tail) < self.min_tail:
            raise ValueError(f"Tail has {len(tail)} values; at least {self.min_tail} required")
        if np.all(tail == tail[0]):
            raise ValueError("Tail values are constant; the GEV is not identifiable")
        c, loc, scale = genextreme.fit(tail)
        return EVTResult(shape=float(c), loc=float(loc), scale=float(scale),
                         threshold=threshold, n_tail=int(len(tail)))
