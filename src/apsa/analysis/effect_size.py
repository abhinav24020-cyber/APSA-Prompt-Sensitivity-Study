"""Effect size estimators: Cliff's Delta and Cohen's d."""

from dataclasses import dataclass

import numpy as np

from .study_statistics import cliffs_delta, cliffs_delta_magnitude


@dataclass
class EffectSizeResult:
    cliffs_delta: float
    cohens_d: float
    magnitude: str   # "negligible" | "small" | "medium" | "large" (from Cliff's delta)


class EffectSizeCalculator:
    """Compute Cliff's Delta and Cohen's d (pooled SD) for two samples, a versus b."""

    def compute(self, group_a: list[float], group_b: list[float]) -> EffectSizeResult:
        if len(group_a) == 0 or len(group_b) == 0:
            raise ValueError("Both groups must be non-empty")
        a = np.asarray(group_a, dtype=float)
        b = np.asarray(group_b, dtype=float)
        delta = cliffs_delta(a, b)
        na, nb = len(a), len(b)
        if na + nb > 2:
            var_a = a.var(ddof=1) if na > 1 else 0.0
            var_b = b.var(ddof=1) if nb > 1 else 0.0
            pooled = float(np.sqrt(((na - 1) * var_a + (nb - 1) * var_b) / (na + nb - 2)))
        else:
            pooled = 0.0
        diff = float(a.mean() - b.mean())
        if diff == 0:
            d = 0.0
        elif pooled > 0:
            d = diff / pooled
        else:
            d = float(np.sign(diff) * np.inf)
        return EffectSizeResult(cliffs_delta=delta, cohens_d=d, magnitude=cliffs_delta_magnitude(delta))
