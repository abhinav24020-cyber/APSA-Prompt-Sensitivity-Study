"""Tests for the Phase 11-15 study additions: statistics helpers, answer key, code
execution scoring, rate-limit parsing, prompt selection and the mock study runner."""

import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest
from scipy import stats

from apsa.analysis import study_statistics as st
from apsa.llm_providers.exceptions import (
    RateLimitError,
    classify_rate_limit_scope,
    parse_retry_after_text,
)
from apsa.metrics.functional.answer_key import ANSWER_KEY, answer_region, score_answer
from apsa.metrics.functional.code_execution import (
    CODE_TESTS,
    CodeExecutionEvaluator,
    extract_code,
    run_code_tests,
)

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments"))


# ---------------------------------------------------------------- multiple comparisons
def test_holm_matches_hand_calculation():
    # p sorted: 0.01*3=0.03, 0.02*2=0.04, 0.04*1=0.04 (monotone)
    assert st.holm_adjust([0.04, 0.01, 0.02]) == pytest.approx([0.04, 0.03, 0.04])
    assert st.holm_adjust([]) == []
    assert st.holm_adjust([0.9, 0.8]) == pytest.approx([1.0, 1.0])


def test_bh_matches_hand_calculation():
    # m=4: sorted p 0.01,0.02,0.03,0.04 -> 0.04,0.04,0.04,0.04
    assert st.bh_adjust([0.01, 0.02, 0.03, 0.04]) == pytest.approx([0.04] * 4)


# ---------------------------------------------------------------- effect sizes
def test_cliffs_delta_extremes_and_empty():
    assert st.cliffs_delta([2, 3], [0, 1]) == 1.0
    assert st.cliffs_delta([0, 1], [2, 3]) == -1.0
    assert st.cliffs_delta([1, 1], [1, 1]) == 0.0
    assert st.cliffs_delta([], [1]) is None
    assert st.cliffs_delta_magnitude(0.5) == "large"
    assert st.cliffs_delta_magnitude(0.1) == "negligible"


def test_paired_rank_biserial():
    assert st.paired_rank_biserial([1, 2, 3]) == 1.0
    assert st.paired_rank_biserial([-1, -2]) == -1.0
    assert st.paired_rank_biserial([0, 0]) == 0.0
    # ranks of |d| = 1,2,3; positive ranks 2+3=5, negative 1 -> (5-1)/6
    assert st.paired_rank_biserial([-1, 2, 3]) == pytest.approx(4 / 6)


def test_wilcoxon_all_zero_and_matches_scipy():
    zero = st.wilcoxon_paired([0, 0, 0])
    assert zero["p_value"] == 1.0 and zero["n_nonzero"] == 0
    d = [0.3, 0.1, -0.05, 0.2, 0.4, 0.15, 0.0, 0.25]
    res = st.wilcoxon_paired(d)
    assert res["p_value"] == pytest.approx(stats.wilcoxon(d, zero_method="pratt").pvalue)
    assert st.wilcoxon_paired([])["p_value"] is None


# ---------------------------------------------------------------- bootstrap
def test_cluster_bootstrap_mean_point_estimate_and_ci_contains_it():
    values = [1, 1, 2, 2, 3, 3, 10, 10]
    clusters = ["a", "a", "b", "b", "c", "c", "d", "d"]
    res = st.cluster_bootstrap_mean(values, clusters, n_boot=2000)
    assert res["mean"] == pytest.approx(4.0)
    assert res["n_clusters"] == 4
    assert res["ci_low"] <= 4.0 <= res["ci_high"]


def test_cluster_bootstrap_is_wider_than_naive_when_clusters_are_correlated():
    rng = np.random.default_rng(0)
    cluster_means = rng.normal(0, 1, 20)
    values = np.repeat(cluster_means, 10) + rng.normal(0, 0.05, 200)
    clusters = np.repeat(np.arange(20), 10)
    clustered = st.cluster_bootstrap_mean(values, clusters)
    naive = st.cluster_bootstrap_mean(values, np.arange(200))
    assert (clustered["ci_high"] - clustered["ci_low"]) > 2 * (naive["ci_high"] - naive["ci_low"])


def test_cluster_bootstrap_small_and_empty():
    assert st.cluster_bootstrap_mean([], [])["mean"] is None
    single = st.cluster_bootstrap_mean([1.0, 3.0], ["x", "x"])
    assert single["mean"] == 2.0 and single["ci_low"] is None


def test_describe_and_group_tests():
    d = st.describe([0, 0, 1, 3])
    assert d["n"] == 4 and d["median"] == 0.5 and d["share_zero"] == 0.5
    assert st.describe([])["n"] == 0
    kw = st.kruskal_epsilon_squared([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
    assert kw["p_value"] < 0.05 and 0 < kw["epsilon_squared"] <= 1
    assert st.kruskal_epsilon_squared([[1, 1], [1, 1]])["p_value"] == 1.0
    fr = st.friedman_kendall_w(np.array([[1, 2, 3], [1, 2, 3], [1, 2, 3], [1, 2, 3]]))
    assert fr["kendall_w"] == pytest.approx(1.0)
    assert st.mcnemar_exact(0, 0) == 1.0
    assert st.mcnemar_exact(0, 6) == pytest.approx(2 * 0.5 ** 6)
    assert st.spearman([1, 2, 3, 4], [2, 4, 6, 8])["rho"] == pytest.approx(1.0)
    assert st.spearman([1, 1, 1], [1, 2, 3])["rho"] is None


# ---------------------------------------------------------------- answer key
def test_answer_key_accepts_every_reference_answer():
    import csv

    rows = {r["prompt_id"]: r for r in csv.DictReader(open(ROOT / "data/baseline_prompts.csv", encoding="utf-8"))}
    for pid in ANSWER_KEY:
        assert score_answer(pid, "Final answer: " + rows[pid]["expected_answer"]) is True, pid


@pytest.mark.parametrize("pid,output,expected", [
    ("CLASS-001", "Final answer: Positive", False),
    ("CLASS-001", "It is not positive.\nFinal answer: Negative", True),
    ("MATH-004", r"Final answer: \(\frac{10}{21}\)", True),
    ("MATH-003", "Final answer: 160π cm³", True),
    ("MATH-005", "Final answer: $1,125.51", True),
    ("MATH-009", "Final answer: 2.5 hours", False),
    ("LOGIC-002", "Final answer: Person A: Knave, Person B: Knight", False),
    ("LOGIC-010", "Final answer: True", True),
    ("QA-001", "", False),
    ("NOT-IN-KEY", "anything", None),
])
def test_answer_key_edge_cases(pid, output, expected):
    assert score_answer(pid, output) is expected


def test_answer_region_without_marker_uses_whole_output():
    text = "Yes, John qualifies. " + "x" * 500
    assert answer_region(text, "final").startswith("yes")
    # regression for the audit finding: a leading "Yes" must not be cut off
    assert score_answer("LOGIC-005", text) is True
    assert score_answer("CLASS-001", "Not positive or neutral overall: negative") is False


# ---------------------------------------------------------------- code execution
def test_reference_solutions_pass_their_tests():
    import csv

    rows = {r["prompt_id"]: r for r in csv.DictReader(open(ROOT / "data/baseline_prompts.csv", encoding="utf-8"))}
    for pid in CODE_TESTS:
        res = run_code_tests(pid, rows[pid]["expected_answer"])
        assert res.passed, (pid, res.error)


def test_code_tests_reject_wrong_and_missing_code():
    wrong = "```python\ndef reverse_string(s):\n    return s\n```"
    assert run_code_tests("CODE-001", wrong).passed is False
    assert run_code_tests("CODE-001", "I cannot help").error == "no_parseable_code"
    loop = "```python\ndef reverse_string(s):\n    while True:\n        pass\n```"
    assert run_code_tests("CODE-001", loop, timeout_seconds=2).error == "timeout"
    renamed = "```python\ndef rev(s):\n    return s[::-1]\n```"
    res = run_code_tests("CODE-001", renamed)
    assert res.passed and res.name_fallback
    assert run_code_tests("MATH-001", "x").applicable is False


def test_extract_code_prefers_parseable_fenced_block():
    out = "Here:\n```python\ndef f():\n    return 1\n```\nDone"
    assert extract_code(out).strip().startswith("def f")


def test_code_execution_evaluator_pairs():
    good = "```python\ndef reverse_string(s):\n    return ''.join(reversed(list(s)))\n```"
    bad = "```python\ndef reverse_string(s):\n    return s\n```"
    res = CodeExecutionEvaluator().evaluate(good, bad, "CODE-001")
    assert res.applicable and res.original_pass and not res.perturbed_pass and res.functional_failure


# ---------------------------------------------------------------- rate limits
def test_rate_limit_parsing_and_scope():
    assert parse_retry_after_text("Please try again in 7m12.48s.") == pytest.approx(432.48)
    assert parse_retry_after_text("Please try again in 2.5s") == 2.5
    assert parse_retry_after_text('"retryDelay": "38s"') == 38.0
    assert parse_retry_after_text("try again in 450ms") == pytest.approx(0.45)
    assert parse_retry_after_text("no hint") is None
    assert classify_rate_limit_scope("on tokens per day (TPD): Limit 200000") == "day"
    assert classify_rate_limit_scope("tokens per minute (TPM)") == "minute"
    assert classify_rate_limit_scope("slow down") is None
    err = RateLimitError("x", retry_after=3, scope="minute")
    assert err.retry_after == 3 and err.scope == "minute"


# ---------------------------------------------------------------- runner
def test_select_prompts_is_balanced_interleaved_and_scorable_first():
    import csv

    from run_study import select_prompts

    rows = list(csv.DictReader(open(ROOT / "data/baseline_prompts.csv", encoding="utf-8")))
    chosen = select_prompts(rows, 10, "scorable_first_file_order")
    assert len(chosen) == 50
    cats = [r["task_category"] for r in chosen]
    assert len(set(cats[:5])) == 5  # round-robin interleaving
    for r in chosen:
        assert json.loads(r["metadata"])["eval_metric"] in {"exact_match", "code_execution"}
    with pytest.raises(ValueError):
        select_prompts(rows, 1, "nonsense")


def test_worker_waits_out_short_rate_limits_and_stops_on_long(tmp_path, monkeypatch):
    from run_study import ModelWorker

    from apsa.llm_providers.base import GenerationResult

    class FlakyProvider:
        model_name = "flaky"

        def __init__(self, waits):
            self.waits = list(waits)

        def generate(self, prompt, cfg):
            if self.waits:
                raise RateLimitError("429", retry_after=self.waits.pop(0), scope="minute")
            return GenerationResult(model_name="flaky", prompt=prompt, output="ok", latency=0.0,
                                    generation_configuration=cfg)

    (tmp_path / "raw").mkdir()
    prompts = [{"prompt_id": "P1", "task_category": "c", "original_prompt": "hi"}]

    def worker(waits, max_wait):
        return ModelWorker(study_dir=tmp_path, study_id="t", model_cfg={"name": "flaky", "provider": "mock"},
                           provider=FlakyProvider(waits), generation={}, system_prompt="s",
                           prompts=prompts, candidates=[], control_repetitions=1, max_wait=max_wait,
                           is_mock=True, max_calls=None)

    import run_study
    monkeypatch.setattr(run_study.time, "sleep", lambda s: None)  # no real waiting
    w = worker([0.1, 0.1], max_wait=60)
    w.run()
    assert w.status == "completed" and w.successes == 2
    w2 = worker([5000], max_wait=60)
    w2.gen_path.unlink()
    w2.done = set()
    w2.run()
    assert w2.status == "stopped_quota"
    fail = [json.loads(l) for l in w2.fail_path.read_text().splitlines()]
    assert fail[-1]["error_type"] == "RateLimitError" and fail[-1]["model_stopped"]


@pytest.mark.slow
def test_mock_study_end_to_end(tmp_path):
    cmd = [sys.executable, str(ROOT / "experiments/run_study.py"), "--study-id", "t", "--mock",
           "--output-root", str(tmp_path), "--prompts-per-category", "1", "--models", "allam-2-7b"]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=600, cwd=ROOT)
    assert proc.returncode == 0, proc.stderr[-2000:]
    gens = (tmp_path / "t/raw/generations__allam-2-7b.jsonl").read_text().splitlines()
    rows = [json.loads(l) for l in gens]
    assert sum(r["condition"] == "anchor" for r in rows) == 5
    assert sum(r["condition"] == "control" for r in rows) == 10
    assert all(r["execution_mode"] == "mock" for r in rows)
    assert len({r["record_id"] for r in rows}) == len(rows)
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=600, cwd=ROOT)
    assert len((tmp_path / "t/raw/generations__allam-2-7b.jsonl").read_text().splitlines()) == len(gens)


# ---------------------------------------------------------------- formerly-stubbed modules
def test_effect_size_calculator():
    from apsa.analysis.effect_size import EffectSizeCalculator

    r = EffectSizeCalculator().compute([3, 4, 5], [0, 1, 2])
    assert r.cliffs_delta == 1.0 and r.magnitude == "large" and r.cohens_d == pytest.approx(3.0)
    with pytest.raises(ValueError):
        EffectSizeCalculator().compute([], [1])


def test_hypothesis_tester():
    from apsa.analysis.hypothesis_testing import HypothesisTester

    h = HypothesisTester()
    w = h.wilcoxon_signed_rank([0] * 10, [0.1 * i + 0.1 for i in range(10)])
    assert w.significant and w.rank_biserial == 1.0
    with pytest.raises(ValueError):
        h.wilcoxon_signed_rank([1], [1, 2])
    k = h.kruskal_wallis({"a": [1, 2, 3, 4], "b": [10, 11, 12, 13]})
    assert k.significant and k.epsilon_squared > 0


def test_glmm_regressor_recovers_effect():
    import pandas as pd

    from apsa.analysis.regression import GLMMRegressor

    rng = np.random.default_rng(1)
    rows = []
    for p in range(30):
        u = rng.normal(0, 0.05)
        for op in ("a", "b"):
            for m in ("m1", "m2"):
                y = 0.1 + (0.2 if op == "b" else 0) + u + rng.normal(0, 0.01)
                rows.append({"d_out_sem": y, "d_in_char": rng.uniform(0, 0.1),
                             "d_in_sem": rng.uniform(0, 0.1), "operator": op,
                             "task_category": "t" + str(p % 2), "model": m, "prompt_id": f"P{p}"})
    g = GLMMRegressor()
    g.fit(pd.DataFrame(rows))
    s = g.summary()
    assert s["coefficients"]["C(operator)[T.b]"]["estimate"] == pytest.approx(0.2, abs=0.02)
    with pytest.raises(RuntimeError):
        GLMMRegressor().summary()


def test_extreme_value_analyzer():
    from apsa.analysis.extreme_value import ExtremeValueAnalyzer

    data = list(np.random.default_rng(2).gumbel(1.0, 0.5, 1000))
    r = ExtremeValueAnalyzer().fit(data)
    assert r.n_tail >= 10 and r.scale > 0
    with pytest.raises(ValueError):
        ExtremeValueAnalyzer().fit([1.0] * 5)
