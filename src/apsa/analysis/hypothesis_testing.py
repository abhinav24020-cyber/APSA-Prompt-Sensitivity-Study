"""Non-parametric hypothesis tests for output divergence comparisons.

Tests:
- Wilcoxon Signed-Rank (paired baseline vs. treatment)
- Kruskal-Wallis H (multi-group: perturbation types, task domains)
"""

from dataclasses import dataclass
import numpy as np


@dataclass
class WilcoxonResult:
    statistic: float
    p_value: float
    significant: bool       # p < 0.05 by default


@dataclass
class KruskalWallisResult:
    statistic: float
    p_value: float
    significant: bool


class HypothesisTester:
    """Run paired and multi-group non-parametric significance tests."""

    def wilcoxon_signed_rank(
        self,
        baseline_scores: list[float],
        treatment_scores: list[float],
        alpha: float = 0.05,
    ) -> WilcoxonResult:
        # TODO: implement using scipy.stats.wilcoxon
        raise NotImplementedError

    def kruskal_wallis(
        self,
        groups: dict[str, list[float]],
        alpha: float = 0.05,
    ) -> KruskalWallisResult:
        # TODO: implement using scipy.stats.kruskal
        raise NotImplementedError
