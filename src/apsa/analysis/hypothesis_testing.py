"""Non-parametric hypothesis tests for output divergence comparisons.

Tests:
- Wilcoxon Signed-Rank (paired baseline vs. treatment; Pratt handling of zero differences)
- Kruskal-Wallis H (multi-group: perturbation types, task domains)
"""

from dataclasses import dataclass

import numpy as np

from .study_statistics import kruskal_epsilon_squared, wilcoxon_paired


@dataclass
class WilcoxonResult:
    statistic: float
    p_value: float
    significant: bool       # p < alpha
    rank_biserial: float | None = None
    n_pairs: int = 0


@dataclass
class KruskalWallisResult:
    statistic: float
    p_value: float
    significant: bool
    epsilon_squared: float | None = None


class HypothesisTester:
    """Run paired and multi-group non-parametric significance tests."""

    def wilcoxon_signed_rank(
        self,
        baseline_scores: list[float],
        treatment_scores: list[float],
        alpha: float = 0.05,
    ) -> WilcoxonResult:
        if len(baseline_scores) != len(treatment_scores):
            raise ValueError("Paired samples must have equal length")
        if len(baseline_scores) == 0:
            raise ValueError("At least one pair is required")
        diffs = np.asarray(treatment_scores, float) - np.asarray(baseline_scores, float)
        r = wilcoxon_paired(diffs)
        return WilcoxonResult(
            statistic=r["statistic"], p_value=r["p_value"], significant=r["p_value"] < alpha,
            rank_biserial=r["rank_biserial"], n_pairs=r["n_pairs"],
        )

    def kruskal_wallis(self, groups: dict[str, list[float]], alpha: float = 0.05) -> KruskalWallisResult:
        non_empty = [g for g in groups.values() if len(g) > 0]
        if len(non_empty) < 2:
            raise ValueError("At least two non-empty groups are required")
        r = kruskal_epsilon_squared(non_empty)
        return KruskalWallisResult(
            statistic=r["H"], p_value=r["p_value"], significant=r["p_value"] < alpha,
            epsilon_squared=r["epsilon_squared"],
        )
