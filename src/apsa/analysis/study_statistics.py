"""Statistical helpers for the APSA main study (Phase 11).

All functions are pure and deterministic for a fixed seed so they can be unit-tested
against hand-computed fixtures. Observations that share an original prompt are not
independent, so uncertainty is estimated with a prompt-level cluster bootstrap.
"""

from __future__ import annotations

import math
from collections.abc import Sequence

import numpy as np
from scipy import stats


def holm_adjust(pvalues: Sequence[float]) -> list[float]:
    """Holm-Bonferroni step-down adjusted p-values (monotone, capped at 1)."""
    p = np.asarray(pvalues, dtype=float)
    m = len(p)
    if m == 0:
        return []
    order = np.argsort(p)
    adjusted = np.empty(m)
    running = 0.0
    for rank, idx in enumerate(order):
        running = max(running, (m - rank) * p[idx])
        adjusted[idx] = min(1.0, running)
    return adjusted.tolist()


def bh_adjust(pvalues: Sequence[float]) -> list[float]:
    """Benjamini-Hochberg false-discovery-rate adjusted p-values."""
    p = np.asarray(pvalues, dtype=float)
    m = len(p)
    if m == 0:
        return []
    order = np.argsort(p)[::-1]
    adjusted = np.empty(m)
    running = 1.0
    for i, idx in enumerate(order):
        rank = m - i
        running = min(running, p[idx] * m / rank)
        adjusted[idx] = min(1.0, running)
    return adjusted.tolist()


def cliffs_delta(x: Sequence[float], y: Sequence[float]) -> float | None:
    """Cliff's delta = P(X > Y) - P(X < Y); None if either group is empty."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if len(x) == 0 or len(y) == 0:
        return None
    greater = (x[:, None] > y[None, :]).sum()
    less = (x[:, None] < y[None, :]).sum()
    return float((greater - less) / (len(x) * len(y)))


def cliffs_delta_magnitude(delta: float | None) -> str:
    """Conventional thresholds (Romano et al., 2006)."""
    if delta is None:
        return "n/a"
    a = abs(delta)
    if a < 0.147:
        return "negligible"
    if a < 0.33:
        return "small"
    if a < 0.474:
        return "medium"
    return "large"


def paired_rank_biserial(differences: Sequence[float]) -> float | None:
    """Matched-pairs rank-biserial correlation (Kerby, 2014); zero differences dropped."""
    d = np.asarray(differences, dtype=float)
    d = d[d != 0]
    if len(d) == 0:
        return 0.0 if len(differences) else None
    ranks = stats.rankdata(np.abs(d))
    total = ranks.sum()
    return float((ranks[d > 0].sum() - ranks[d < 0].sum()) / total)


def wilcoxon_paired(differences: Sequence[float]) -> dict:
    """Two-sided Wilcoxon signed-rank test on paired differences (Pratt zero handling)."""
    d = np.asarray(differences, dtype=float)
    n = int(len(d))
    nonzero = int((d != 0).sum())
    result = {"n_pairs": n, "n_nonzero": nonzero, "statistic": None, "p_value": None,
              "rank_biserial": paired_rank_biserial(d) if n else None}
    if n == 0:
        return result
    if nonzero == 0:
        result.update(statistic=0.0, p_value=1.0)
        return result
    res = stats.wilcoxon(d, zero_method="pratt", alternative="two-sided")
    result.update(statistic=float(res.statistic), p_value=float(res.pvalue))
    return result


def cluster_bootstrap_mean(
    values: Sequence[float],
    clusters: Sequence,
    n_boot: int = 4000,
    confidence: float = 0.95,
    seed: int = 20261119,
) -> dict:
    """Mean with a percentile CI from resampling whole clusters with replacement."""
    v = np.asarray(values, dtype=float)
    c = np.asarray(clusters)
    if len(v) == 0:
        return {"n": 0, "n_clusters": 0, "mean": None, "ci_low": None, "ci_high": None}
    labels, inverse = np.unique(c, return_inverse=True)
    k = len(labels)
    sums = np.bincount(inverse, weights=v, minlength=k)
    counts = np.bincount(inverse, minlength=k).astype(float)
    estimate = float(v.mean())
    if k < 2:
        return {"n": int(len(v)), "n_clusters": int(k), "mean": estimate,
                "ci_low": None, "ci_high": None}
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, k, size=(n_boot, k))
    boot = sums[idx].sum(axis=1) / counts[idx].sum(axis=1)
    alpha = (1 - confidence) / 2
    return {
        "n": int(len(v)),
        "n_clusters": int(k),
        "mean": estimate,
        "ci_low": float(np.quantile(boot, alpha)),
        "ci_high": float(np.quantile(boot, 1 - alpha)),
    }


def describe(values: Sequence[float]) -> dict:
    """Count, mean, SD, quartiles, IQR, min, max, skewness for a numeric sample."""
    v = np.asarray([x for x in values if x is not None and not math.isnan(x)], dtype=float)
    if len(v) == 0:
        return {"n": 0}
    q1, med, q3 = np.quantile(v, [0.25, 0.5, 0.75])
    return {
        "n": int(len(v)),
        "mean": float(v.mean()),
        "sd": float(v.std(ddof=1)) if len(v) > 1 else 0.0,
        "min": float(v.min()),
        "q1": float(q1),
        "median": float(med),
        "q3": float(q3),
        "iqr": float(q3 - q1),
        "max": float(v.max()),
        "skewness": float(stats.skew(v)) if len(v) > 2 and v.std() > 0 else None,
        "share_zero": float((v == 0).mean()),
    }


def kruskal_epsilon_squared(groups: Sequence[Sequence[float]]) -> dict:
    """Kruskal-Wallis H test with epsilon-squared effect size."""
    groups = [np.asarray(g, dtype=float) for g in groups if len(g) > 0]
    n = sum(len(g) for g in groups)
    if len(groups) < 2:
        return {"H": None, "p_value": None, "epsilon_squared": None, "n": n}
    pooled = np.concatenate(groups)
    if np.all(pooled == pooled[0]):
        return {"H": 0.0, "p_value": 1.0, "epsilon_squared": 0.0, "n": n}
    h, p = stats.kruskal(*groups)
    return {"H": float(h), "p_value": float(p), "epsilon_squared": float(h / (n - 1)), "n": n}


def friedman_kendall_w(matrix: np.ndarray) -> dict:
    """Friedman test over complete blocks (rows) x conditions (columns) with Kendall's W."""
    m = np.asarray(matrix, dtype=float)
    n, k = m.shape if m.ndim == 2 else (0, 0)
    if n < 2 or k < 3:
        return {"chi2": None, "p_value": None, "kendall_w": None, "n_blocks": n}
    if np.all(m == m[0, 0]):
        return {"chi2": 0.0, "p_value": 1.0, "kendall_w": 0.0, "n_blocks": n}
    chi2, p = stats.friedmanchisquare(*[m[:, j] for j in range(k)])
    return {"chi2": float(chi2), "p_value": float(p),
            "kendall_w": float(chi2 / (n * (k - 1))), "n_blocks": n}


def mcnemar_exact(b: int, c: int) -> float:
    """Exact two-sided McNemar p-value from discordant counts b and c."""
    n = b + c
    if n == 0:
        return 1.0
    return float(min(1.0, 2 * stats.binom.cdf(min(b, c), n, 0.5)))


def spearman(x: Sequence[float], y: Sequence[float]) -> dict:
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if len(x) < 3 or np.all(x == x[0]) or np.all(y == y[0]):
        return {"rho": None, "p_value": None, "n": int(len(x))}
    rho, p = stats.spearmanr(x, y)
    return {"rho": float(rho), "p_value": float(p), "n": int(len(x))}
