"""APSA Phases 11-15 analysis of a main-study run produced by ``run_study.py``.

Pipeline: raw generations (read-only) -> scored generations -> anchor-paired analysis
dataset (with exclusions and reconciliation) -> descriptive statistics, prompt-clustered
bootstrap CIs, Wilcoxon / Kruskal-Wallis / Friedman tests with Holm correction, effect
sizes, a linear mixed model, robustness re-analyses, budgeted maxima, a held-out
operator-selection check, an output-change taxonomy, case studies and figures.

Usage:
  .\\.venv\\Scripts\\python.exe experiments\\analyze_study.py --study-dir results\\study\\main_v1
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import re
import sys
import warnings
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from apsa.analysis import study_statistics as st  # noqa: E402
from apsa.metrics.functional.answer_key import (  # noqa: E402
    ANSWER_KEY,
    answer_region,
    has_final_answer_marker,
    score_answer,
)
from apsa.metrics.functional.code_execution import CODE_TESTS, run_code_tests  # noqa: E402
from apsa.metrics.output_distance import OutputDeviationMetrics  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("apsa.analysis")
warnings.filterwarnings("ignore", category=FutureWarning)

SEMANTIC_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
OPERATOR_FAMILY = {
    "char_substitution": "surface", "capitalization": "surface", "punctuation": "surface",
    "whitespace": "surface", "word_insertion": "lexical", "word_deletion": "lexical",
    "synonym": "lexical", "word_substitution": "lexical",
    "instruction_reordering": "structural", "random_edit": "noise_control",
}
TRUNCATION_REASONS = {"length", "max_tokens", "finishreason.max_tokens"}
METRICS = {
    "d_out_sem": "Semantic output distance (1 - cosine, MiniLM)",
    "d_out_char": "Normalised character Levenshtein distance",
    "d_out_token": "Token Jaccard distance",
    "answer_changed": "Final answer changed (0/1)",
}
PRIMARY = "d_out_sem"


# ----------------------------------------------------------------------------- loading
def load_jsonl(path: Path) -> list[dict]:
    rows = []
    if not path.exists():
        return rows
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if line.strip():
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                logger.warning("Malformed JSON at %s:%d (counted, skipped)", path.name, i)
                rows.append({"_malformed": True, "_source": path.name, "_line": i})
    return rows


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# ----------------------------------------------------------------------------- scoring
def normalized_final_answer(prompt_id: str, output: str) -> str | None:
    if prompt_id.startswith("CODE") or not output:
        return None
    if not has_final_answer_marker(output):
        return None
    region = answer_region(output, "final")
    # Keep characters that can carry meaning in an answer (digits, '/', '%', '-', decimal
    # points), but drop sentence-final periods so "$7.20." and "$7.20" compare equal.
    region = re.sub(r"\.(?!\d)", " ", region)
    return re.sub(r"[^a-z0-9/.%-]+", "", region)[:200]


def score_generations(gens: pd.DataFrame, cache_path: Path) -> pd.DataFrame:
    cache = json.loads(cache_path.read_text(encoding="utf-8")) if cache_path.exists() else {}

    def code_key(pid, out):
        return pid + ":" + hashlib.sha256((out or "").encode("utf-8")).hexdigest()

    todo = {}
    for pid, out in zip(gens["prompt_id"], gens["output"]):
        if pid in CODE_TESTS:
            k = code_key(pid, out)
            if k not in cache:
                todo[k] = (pid, out)
    if todo:
        logger.info("Executing %d unique code outputs against unit tests", len(todo))
        with ThreadPoolExecutor(max_workers=8) as pool:
            results = pool.map(lambda item: (item[0], run_code_tests(*item[1])), todo.items())
            for k, res in results:
                cache[k] = {"passed": res.passed, "error": res.error,
                            "name_fallback": res.name_fallback}
        cache_path.write_text(json.dumps(cache), encoding="utf-8")

    correct, errors, fallback, method = [], [], [], []
    for pid, out in zip(gens["prompt_id"], gens["output"]):
        if pid in CODE_TESTS:
            r = cache[code_key(pid, out)]
            correct.append(r["passed"])
            errors.append(r["error"])
            fallback.append(r["name_fallback"])
            method.append("unit_tests")
        elif pid in ANSWER_KEY:
            correct.append(score_answer(pid, out))
            errors.append(None)
            fallback.append(False)
            method.append("answer_key")
        else:
            correct.append(None)
            errors.append(None)
            fallback.append(False)
            method.append("unscored")
    gens = gens.copy()
    gens["correct"] = correct
    gens["code_error"] = errors
    gens["code_name_fallback"] = fallback
    gens["scoring_method"] = method
    gens["has_final_marker"] = [
        has_final_answer_marker(o) if not p.startswith("CODE") else None
        for p, o in zip(gens["prompt_id"], gens["output"])
    ]
    gens["final_answer_norm"] = [normalized_final_answer(p, o)
                                 for p, o in zip(gens["prompt_id"], gens["output"])]
    gens["truncated"] = gens["finish_reason"].fillna("").str.casefold().isin(TRUNCATION_REASONS)
    gens["empty_output"] = gens["output"].fillna("").str.strip() == ""
    return gens


# ----------------------------------------------------------------------------- pairing
def build_pairs(gens: pd.DataFrame, candidates: pd.DataFrame) -> tuple[pd.DataFrame, list[dict]]:
    anchors = gens[gens["condition"] == "anchor"].set_index(["model", "prompt_id"])
    cand = candidates[candidates["status"] == "accepted"].set_index(["prompt_id", "operator"])
    rows, exclusions = [], []
    for g in gens[gens["condition"] != "anchor"].itertuples(index=False):
        key = (g.model, g.prompt_id)
        if key not in anchors.index:
            exclusions.append({"record_id": g.record_id, "model": g.model,
                               "prompt_id": g.prompt_id, "reason": "anchor_missing"})
            continue
        a = anchors.loc[key]
        row = {
            "pair_id": f"{g.model}|{g.prompt_id}|{g.condition}|{g.operator}|{g.repetition}",
            "anchor_record_id": a["record_id"], "comparison_record_id": g.record_id,
            "model": g.model, "provider": g.provider, "prompt_id": g.prompt_id,
            "task_category": g.task_category, "condition": g.condition,
            "operator": g.operator if g.condition == "treatment" else "control",
            "family": OPERATOR_FAMILY.get(g.operator, "control"), "repetition": g.repetition,
            "perturbation_id": g.perturbation_id,
            "anchor_output": a["output"], "comparison_output": g.output,
            "anchor_correct": a["correct"], "comparison_correct": g.correct,
            "anchor_final": a["final_answer_norm"], "comparison_final": g.final_answer_norm,
            "anchor_has_marker": a["has_final_marker"], "comparison_has_marker": g.has_final_marker,
            "any_truncated": bool(a["truncated"] or g.truncated),
            "any_empty": bool(a["empty_output"] or g.empty_output),
            "scoring_method": g.scoring_method,
            "code_name_fallback": bool(g.code_name_fallback),
        }
        if g.condition == "treatment":
            c = cand.loc[(g.prompt_id, g.operator)]
            d = c["input_distances"]
            row.update({
                "d_in_char": d["char_levenshtein_normalized"],
                "d_in_word": d["word_levenshtein"],
                "d_in_sem": d["semantic_cosine_distance"],
                "semantic_risk": c["semantic_risk_level"],
                "perturbed_prompt": c["perturbed_prompt"],
            })
        else:
            row.update({"d_in_char": 0.0, "d_in_word": 0, "d_in_sem": 0.0,
                        "semantic_risk": "none", "perturbed_prompt": None})
        rows.append(row)
    return pd.DataFrame(rows), exclusions


def add_output_metrics(pairs: pd.DataFrame) -> pd.DataFrame:
    from sentence_transformers import SentenceTransformer

    odm = OutputDeviationMetrics(use_semantic=False)
    pairs = pairs.copy()
    pairs["d_out_char"] = [odm.normalized_character_distance(a, b)
                           for a, b in zip(pairs["anchor_output"], pairs["comparison_output"])]
    pairs["d_out_token"] = [odm.token_level_distance(a, b)
                            for a, b in zip(pairs["anchor_output"], pairs["comparison_output"])]
    pairs["identical_output"] = [(a or "").strip() == (b or "").strip()
                                 for a, b in zip(pairs["anchor_output"], pairs["comparison_output"])]
    texts = sorted(set(pairs["anchor_output"].fillna("")) | set(pairs["comparison_output"].fillna("")))
    logger.info("Embedding %d unique outputs with %s", len(texts), SEMANTIC_MODEL)
    model = SentenceTransformer(SEMANTIC_MODEL)
    emb = model.encode(texts, batch_size=64, normalize_embeddings=True, show_progress_bar=False)
    index = {t: i for i, t in enumerate(texts)}
    sem = []
    for a, b, same in zip(pairs["anchor_output"].fillna(""), pairs["comparison_output"].fillna(""),
                          pairs["identical_output"]):
        if same:
            sem.append(0.0)
        elif not a.strip() or not b.strip():
            sem.append(1.0)
        else:
            sim = float(np.dot(emb[index[a]], emb[index[b]]))
            sem.append(float(min(1.0, max(0.0, 1.0 - sim))))
    pairs["d_out_sem"] = sem

    def missing(v) -> bool:
        return v is None or (isinstance(v, float) and np.isnan(v)) or v is pd.NA

    def answer_changed(r):
        # pandas may store missing values as NaN, and NaN != NaN, so test explicitly.
        if r.prompt_id.startswith("CODE"):
            if missing(r.anchor_correct) or missing(r.comparison_correct):
                return np.nan
            return float(bool(r.anchor_correct) != bool(r.comparison_correct))
        a_missing, c_missing = missing(r.anchor_final), missing(r.comparison_final)
        if a_missing and c_missing:
            return np.nan
        if a_missing or c_missing:
            return 1.0  # one output gave a marked final answer and the other did not
        return float(r.anchor_final != r.comparison_final)

    pairs["answer_changed"] = [answer_changed(r) for r in pairs.itertuples()]
    pairs["scorable"] = pairs["anchor_correct"].notna() & pairs["comparison_correct"].notna()
    pairs["flip_c2i"] = (pairs["anchor_correct"] == True) & (pairs["comparison_correct"] == False)  # noqa: E712
    pairs["flip_i2c"] = (pairs["anchor_correct"] == False) & (pairs["comparison_correct"] == True)  # noqa: E712
    pairs["flip_any"] = pairs["flip_c2i"] | pairs["flip_i2c"]
    d_comp = 0.5 * pairs["d_in_char"] + 0.5 * pairs["d_in_sem"]
    pairs["d_in_composite"] = d_comp
    pairs["sensitivity_ratio"] = np.where(pairs["condition"] == "treatment",
                                          pairs["d_out_sem"] / (d_comp + 1e-4), np.nan)
    pairs["near_zero_denominator"] = (pairs["condition"] == "treatment") & (d_comp < 0.01)
    return pairs


def taxonomy(r) -> str:
    """Mutually exclusive primary label for an output pair (ordered by severity)."""
    if r.any_empty:
        return "empty_output"
    if r.any_truncated:
        return "truncation"
    if r.flip_c2i:
        return "correctness_flip_correct_to_incorrect"
    if r.flip_i2c:
        return "correctness_flip_incorrect_to_correct"
    if (not r.prompt_id.startswith("CODE")) and r.anchor_has_marker == True             and r.comparison_has_marker == False:  # noqa: E712 - may be numpy/pandas bools
        return "format_instruction_violation"
    if r.identical_output:
        return "identical"
    if r.answer_changed == 1.0:
        return "final_answer_change_same_correctness"
    if r.d_out_sem < 0.05:
        return "wording_change_only"
    return "content_change_same_answer"


# ----------------------------------------------------------------------------- statistics
def ci_row(values, clusters, **extra) -> dict:
    return {**extra, **st.cluster_bootstrap_mean(list(values), list(clusters))}


def prompt_level_diffs(pairs: pd.DataFrame, metric: str, operator: str | None = None,
                       by_model: bool = True) -> pd.DataFrame:
    """Per (model, prompt): mean treatment metric minus mean control metric."""
    t = pairs[pairs["condition"] == "treatment"]
    if operator is not None:
        t = t[t["operator"] == operator]
    c = pairs[pairs["condition"] == "control"]
    keys = ["model", "prompt_id"]
    tm = t.groupby(keys)[metric].mean().rename("treatment")
    cm = c.groupby(keys)[metric].mean().rename("control")
    df = pd.concat([tm, cm], axis=1).dropna().reset_index()
    df["diff"] = df["treatment"] - df["control"]
    return df


def treatment_vs_control(pairs: pd.DataFrame, metric: str) -> list[dict]:
    out = []
    diffs = prompt_level_diffs(pairs, metric)
    groups = [("ALL MODELS", diffs)] + [(m, d) for m, d in diffs.groupby("model")]
    for name, d in groups:
        if d.empty:
            continue
        w = st.wilcoxon_paired(d["diff"].to_numpy())
        boot = st.cluster_bootstrap_mean(d["diff"].to_numpy(), d["prompt_id"].to_numpy())
        out.append({
            "model": name, "metric": metric, "n_model_prompt_units": len(d),
            "mean_treatment": float(d["treatment"].mean()), "mean_control": float(d["control"].mean()),
            "mean_diff": boot["mean"], "diff_ci_low": boot["ci_low"], "diff_ci_high": boot["ci_high"],
            "wilcoxon_W": w["statistic"], "p_value": w["p_value"], "rank_biserial": w["rank_biserial"],
            "n_nonzero_diffs": w["n_nonzero"],
        })
    return out


def per_operator_vs_control(pairs: pd.DataFrame, metric: str) -> list[dict]:
    rows = []
    control_vals = pairs.loc[pairs["condition"] == "control", metric].dropna().to_numpy()
    for op in sorted(pairs.loc[pairs["condition"] == "treatment", "operator"].unique()):
        d = prompt_level_diffs(pairs, metric, operator=op)
        w = st.wilcoxon_paired(d["diff"].to_numpy())
        boot = st.cluster_bootstrap_mean(d["diff"].to_numpy(), d["prompt_id"].to_numpy())
        tv = pairs.loc[(pairs["operator"] == op), metric].dropna().to_numpy()
        delta = st.cliffs_delta(tv, control_vals)
        rows.append({
            "operator": op, "family": OPERATOR_FAMILY[op], "metric": metric, "n_pairs": len(d),
            "mean_treatment": float(d["treatment"].mean()) if len(d) else None,
            "mean_diff_vs_control": boot["mean"], "ci_low": boot["ci_low"], "ci_high": boot["ci_high"],
            "p_value": w["p_value"], "rank_biserial": w["rank_biserial"],
            "cliffs_delta_vs_control": delta, "cliffs_magnitude": st.cliffs_delta_magnitude(delta),
        })
    adj = st.holm_adjust([r["p_value"] if r["p_value"] is not None else 1.0 for r in rows])
    for r, p in zip(rows, adj):
        r["p_holm"] = p
    return rows


def correctness_tables(pairs: pd.DataFrame, gens: pd.DataFrame) -> dict:
    sc = pairs[pairs["scorable"]]
    out: dict = {}
    anchors = gens[(gens["condition"] == "anchor") & gens["correct"].notna()]
    out["anchor_accuracy_by_model"] = [
        ci_row(g["correct"].astype(float), g["prompt_id"], model=m)
        for m, g in anchors.groupby("model")
    ]
    out["anchor_accuracy_by_model_category"] = [
        {"model": m, "task_category": c, "n": len(g), "accuracy": float(g["correct"].astype(float).mean())}
        for (m, c), g in anchors.groupby(["model", "task_category"])
    ]
    rows = []
    for (model, cond), g in sc.groupby(["model", "condition"]):
        rows.append({
            "model": model, "condition": cond, "n_pairs": len(g),
            "comparison_accuracy": float(g["comparison_correct"].astype(float).mean()),
            **{f"c2i_{k}": v for k, v in st.cluster_bootstrap_mean(
                g["flip_c2i"].astype(float), g["prompt_id"]).items() if k in ("mean", "ci_low", "ci_high")},
            "i2c_rate": float(g["flip_i2c"].mean()), "any_flip_rate": float(g["flip_any"].mean()),
        })
    for cond, g in sc.groupby("condition"):
        rows.append({
            "model": "ALL MODELS", "condition": cond, "n_pairs": len(g),
            "comparison_accuracy": float(g["comparison_correct"].astype(float).mean()),
            **{f"c2i_{k}": v for k, v in st.cluster_bootstrap_mean(
                g["flip_c2i"].astype(float), g["prompt_id"]).items() if k in ("mean", "ci_low", "ci_high")},
            "i2c_rate": float(g["flip_i2c"].mean()), "any_flip_rate": float(g["flip_any"].mean()),
        })
    out["flip_rates_by_model_condition"] = rows
    op_rows = []
    for op, g in sc[sc["condition"] == "treatment"].groupby("operator"):
        b = int(g["flip_c2i"].sum())
        c = int(g["flip_i2c"].sum())
        boot = st.cluster_bootstrap_mean(g["flip_any"].astype(float), g["prompt_id"])
        op_rows.append({"operator": op, "family": OPERATOR_FAMILY[op], "n_pairs": len(g),
                        "c2i": b, "i2c": c, "any_flip_rate": boot["mean"],
                        "ci_low": boot["ci_low"], "ci_high": boot["ci_high"],
                        "net_accuracy_change": (c - b) / len(g), "mcnemar_p": st.mcnemar_exact(b, c)})
    adj = st.holm_adjust([r["mcnemar_p"] for r in op_rows])
    for r, p in zip(op_rows, adj):
        r["mcnemar_p_holm"] = p
    out["flips_by_operator"] = op_rows
    out["flips_by_category"] = [
        {"task_category": cat, "condition": cond, "n_pairs": len(g),
         "any_flip_rate": float(g["flip_any"].mean()), "c2i_rate": float(g["flip_c2i"].mean())}
        for (cat, cond), g in sc.groupby(["task_category", "condition"])
    ]
    return out


def mixed_model(pairs: pd.DataFrame, metric: str) -> dict:
    import statsmodels.formula.api as smf

    t = pairs[pairs["condition"] == "treatment"].dropna(subset=[metric]).copy()
    if t["model"].nunique() < 2 or len(t) < 50:
        return {"status": "skipped_insufficient_data"}
    formula = (f"{metric} ~ C(operator, Treatment('capitalization')) + C(task_category) + "
               "C(model) + d_in_char + d_in_sem")
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            # lbfgs can stop at a degenerate boundary (zero random-intercept variance with an
            # exploding intercept SE) on this data; Powell and Nelder-Mead agree, so try those first.
            fit = None
            for method in ("powell", "nm", "lbfgs"):
                candidate = smf.mixedlm(formula, t.reset_index(drop=True),
                                        groups=t["prompt_id"].to_numpy()).fit(method=method, reml=True)
                if candidate.converged and np.isfinite(candidate.bse).all() and candidate.bse.max() < 10:
                    fit, used_method = candidate, method
                    break
            if fit is None:
                return {"status": "failed: no optimizer gave a non-degenerate fit"}
        coefs = []
        ci = fit.conf_int()
        for name in fit.fe_params.index:
            coefs.append({"term": name, "estimate": float(fit.fe_params[name]),
                          "ci_low": float(ci.loc[name, 0]), "ci_high": float(ci.loc[name, 1]),
                          "p_value": float(fit.pvalues[name])})
        return {"status": "ok", "formula": formula + " + (1 | prompt_id)", "n": int(len(t)),
                "n_groups": int(t["prompt_id"].nunique()),
                "random_intercept_variance": float(fit.cov_re.iloc[0, 0]),
                "residual_variance": float(fit.scale), "converged": bool(fit.converged),
                "optimizer": used_method,
                "coefficients": coefs}
    except Exception as e:  # noqa: BLE001
        return {"status": f"failed: {e}"}


def budget_maxima(pairs: pd.DataFrame) -> list[dict]:
    t = pairs[pairs["condition"] == "treatment"]
    rows = []
    for metric_in, budgets in (("d_in_char", [0.01, 0.02, 0.05, 0.10, 1.0]),
                               ("d_in_sem", [0.01, 0.02, 0.05, 0.10, 1.0])):
        for eps in budgets:
            sub = t[t[metric_in] <= eps]
            if sub.empty:
                rows.append({"budget_metric": metric_in, "epsilon": eps, "n_candidates_evaluated": 0})
                continue
            top = sub.sort_values(PRIMARY, ascending=False).iloc[0]
            rows.append({
                "budget_metric": metric_in, "epsilon": eps, "n_candidates_evaluated": len(sub),
                "mean_d_out_sem": float(sub[PRIMARY].mean()),
                "max_observed_d_out_sem": float(top[PRIMARY]),
                "argmax_pair": top["pair_id"], "argmax_d_in": float(top[metric_in]),
                "c2i_flips_within_budget": int(sub["flip_c2i"].sum()),
                "c2i_rate_within_budget": float(sub.loc[sub["scorable"], "flip_c2i"].mean())
                if sub["scorable"].any() else None,
            })
    return rows


def adversarial_selection(pairs: pd.DataFrame) -> dict:
    """RQ5 proxy: best-of-operators vs random edits; held-out operator selection."""
    t = pairs[pairs["condition"] == "treatment"]
    targeted = t[t["operator"] != "random_edit"]
    rnd = t[t["operator"] == "random_edit"].set_index(["model", "prompt_id"])
    best = targeted.groupby(["model", "prompt_id"])[PRIMARY].max().rename("best_of_operators")
    df = pd.concat([best, rnd[PRIMARY].rename("random_edit"),
                    rnd["d_in_char"].rename("random_d_in_char")], axis=1).dropna().reset_index()
    out: dict = {"n_units": len(df)}
    if df.empty:
        return out
    diff = df["best_of_operators"] - df["random_edit"]
    w = st.wilcoxon_paired(diff.to_numpy())
    out["oracle_best_of_9_vs_random"] = {
        "mean_best": float(df["best_of_operators"].mean()), "mean_random": float(df["random_edit"].mean()),
        "ratio_of_means": float(df["best_of_operators"].mean() / max(df["random_edit"].mean(), 1e-9)),
        "p_value": w["p_value"], "rank_biserial": w["rank_biserial"],
        "note": "Selection uses observed outputs (oracle maximum of 9 candidates vs 1 random "
                "candidate); inflated by the winner's curse and an unequal candidate budget.",
    }
    # Held-out: choose the operator with the highest mean deviation on discovery prompts.
    prompts = sorted(t["prompt_id"].unique())
    discovery = set(prompts[0::2])
    validation = set(prompts[1::2])
    rows = []
    for model, g in targeted.groupby("model"):
        disc = g[g["prompt_id"].isin(discovery)].groupby("operator")[PRIMARY].mean()
        if disc.empty:
            continue
        chosen = disc.idxmax()
        val = g[(g["prompt_id"].isin(validation)) & (g["operator"] == chosen)].set_index("prompt_id")[PRIMARY]
        rv = rnd.loc[model][PRIMARY] if model in rnd.index.get_level_values(0) else pd.Series(dtype=float)
        rv = rv[rv.index.isin(validation)]
        common = val.index.intersection(rv.index)
        d = (val.loc[common] - rv.loc[common]).to_numpy()
        w = st.wilcoxon_paired(d)
        rows.append({"model": model, "chosen_operator": chosen,
                     "discovery_mean": float(disc.max()),
                     "validation_mean_chosen": float(val.loc[common].mean()) if len(common) else None,
                     "validation_mean_random_edit": float(rv.loc[common].mean()) if len(common) else None,
                     "n_validation_prompts": int(len(common)), "p_value": w["p_value"],
                     "rank_biserial": w["rank_biserial"]})
    out["held_out_operator_selection"] = rows
    return out


def robustness(pairs: pd.DataFrame) -> dict:
    out: dict = {}
    c = pairs[pairs["condition"] == "control"]
    out["control_repeatability"] = [
        {"model": m, "n_control_pairs": len(g), "share_identical": float(g["identical_output"].mean()),
         "mean_d_out_sem": float(g["d_out_sem"].mean()), "max_d_out_sem": float(g["d_out_sem"].max()),
         "control_answer_change_rate": float(g["answer_changed"].mean())
         if g["answer_changed"].notna().any() else None,
         "control_flip_rate": float(g.loc[g["scorable"], "flip_any"].mean()) if g["scorable"].any() else None}
        for m, g in c.groupby("model")
    ]
    specs = {
        "primary (all pairs)": pairs,
        "exclude truncated/empty pairs": pairs[~pairs["any_truncated"] & ~pairs["any_empty"]],
        "exclude high-risk operators (random_edit, char_substitution)":
            pairs[~pairs["operator"].isin(["random_edit", "char_substitution"])],
        "exclude allam-2-7b (weakest instruction follower)": pairs[pairs["model"] != "allam-2-7b"],
        "audit-valid only (exclude audited meaning-altering candidates and random_edit)":
            pairs[~pairs["audit_meaning_altering"] & (pairs["operator"] != "random_edit")],
    }
    rows = []
    for spec, df in specs.items():
        for metric in METRICS:
            r = [x for x in treatment_vs_control(df, metric) if x["model"] == "ALL MODELS"]
            if r:
                rows.append({"specification": spec, **r[0]})
    out["specification_curve"] = rows
    return out


# ----------------------------------------------------------------------------- figures
SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e4e3df"


def _style(ax, title, xlabel=None, ylabel=None, width=62):
    import textwrap

    ax.set_title("\n".join(textwrap.wrap(title, width)), loc="left", fontsize=10.5, color=INK, pad=10)
    if xlabel:
        ax.set_xlabel(xlabel, color=INK2, fontsize=9)
    if ylabel:
        ax.set_ylabel(ylabel, color=INK2, fontsize=9)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(GRID)
    ax.tick_params(colors=INK2, labelsize=8)
    ax.grid(axis="x", color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)


def make_figures(pairs: pd.DataFrame, results: dict, fig_dir: Path) -> list[str]:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig_dir.mkdir(parents=True, exist_ok=True)
    made = []
    models = sorted(pairs["model"].unique())
    color = {m: SERIES[i % len(SERIES)] for i, m in enumerate(models)}

    # F1 treatment vs control by model (dot + 95% cluster CI).
    fig, ax = plt.subplots(figsize=(7.5, 4.0))
    ys = np.arange(len(models))
    for j, (cond, marker, off) in enumerate((("control", "o", 0.17), ("treatment", "D", -0.17))):
        for i, m in enumerate(models):
            g = pairs[(pairs["model"] == m) & (pairs["condition"] == cond)]
            b = st.cluster_bootstrap_mean(g[PRIMARY], g["prompt_id"])
            if b["mean"] is None:
                continue
            col = "#8a8984" if cond == "control" else SERIES[0]
            ax.errorbar(b["mean"], i + off, xerr=[[b["mean"] - (b["ci_low"] or b["mean"])],
                                                   [(b["ci_high"] or b["mean"]) - b["mean"]]],
                        fmt=marker, color=col, ms=6, capsize=0, lw=2,
                        label=("Unchanged-prompt control" if cond == "control" else "Perturbed prompt")
                        if i == 0 else None)
            ax.text((b["ci_high"] or b["mean"]) + 0.004, i + off, f"{b['mean']:.3f}", va="center",
                    fontsize=7, color=INK2)
    ax.set_yticks(ys, models)
    _style(ax, "Output semantic distance from the anchor output, by model (mean, 95% prompt-cluster CI)",
           "1 - cosine similarity of output embeddings")
    ax.legend(frameon=False, fontsize=8, loc="upper left", bbox_to_anchor=(0, -0.2), ncol=2)
    fig.tight_layout()
    fig.savefig(fig_dir / "fig1_treatment_vs_control_by_model.png", dpi=200)
    plt.close(fig)
    made.append("fig1_treatment_vs_control_by_model.png")

    # F2 per-operator mean primary metric with CI and control reference.
    ops = results["per_operator_primary"]
    ops = sorted(ops, key=lambda r: r["mean_treatment"] or 0)
    ctrl = pairs.loc[pairs["condition"] == "control", PRIMARY].mean()
    fig, ax = plt.subplots(figsize=(7.5, 4.2))
    for i, r in enumerate(ops):
        g = pairs[pairs["operator"] == r["operator"]]
        b = st.cluster_bootstrap_mean(g[PRIMARY], g["prompt_id"])
        ax.errorbar(b["mean"], i, xerr=[[b["mean"] - b["ci_low"]], [b["ci_high"] - b["mean"]]],
                    fmt="o", color=SERIES[0], ms=6, lw=2)
        star = "*" if (r["p_holm"] or 1) < 0.05 else ""
        ax.text(b["ci_high"] + 0.004, i, f"{b['mean']:.3f}{star}", va="center", fontsize=7, color=INK2)
    ax.axvline(ctrl, color="#8a8984", lw=1, ls="--")
    ax.text(ctrl, len(ops) - 0.4, f" control mean {ctrl:.3f}", fontsize=7, color=INK2)
    ax.set_yticks(range(len(ops)), [f"{r['operator']} ({r['family']})" for r in ops])
    _style(ax, "Output semantic distance by perturbation operator (all models; * Holm p<0.05 vs control)",
           "1 - cosine similarity of output embeddings")
    fig.tight_layout()
    fig.savefig(fig_dir / "fig2_operator_effects.png", dpi=200)
    plt.close(fig)
    made.append("fig2_operator_effects.png")

    # F3 correctness flip rate by operator.
    fl = sorted(results["correctness"]["flips_by_operator"], key=lambda r: r["any_flip_rate"])
    ctrl_flip = [r for r in results["correctness"]["flip_rates_by_model_condition"]
                 if r["model"] == "ALL MODELS" and r["condition"] == "control"]
    fig, ax = plt.subplots(figsize=(7.5, 4.2))
    for i, r in enumerate(fl):
        ax.barh(i, r["any_flip_rate"], color=SERIES[1], height=0.6)
        ax.text(r["any_flip_rate"] + 0.003, i, f"{r['any_flip_rate']:.1%} (C->I {r['c2i']}, I->C {r['i2c']})",
                va="center", fontsize=7, color=INK2)
    if ctrl_flip:
        cf = ctrl_flip[0]["any_flip_rate"]
        ax.axvline(cf, color="#8a8984", lw=1, ls="--")
        ax.text(cf, len(fl) - 0.4, f" control {cf:.1%}", fontsize=7, color=INK2)
    ax.set_yticks(range(len(fl)), [r["operator"] for r in fl])
    _style(ax, "Share of pairs whose correctness flipped, by operator (all models)", "flip rate")
    fig.tight_layout()
    fig.savefig(fig_dir / "fig3_correctness_flips_by_operator.png", dpi=200)
    plt.close(fig)
    made.append("fig3_correctness_flips_by_operator.png")

    # F4 heatmap model x operator (sequential single hue).
    t = pairs[pairs["condition"] == "treatment"]
    piv = t.pivot_table(index="model", columns="operator", values=PRIMARY, aggfunc="mean")
    from matplotlib.colors import LinearSegmentedColormap

    cmap = LinearSegmentedColormap.from_list("blue", ["#f3f7fd", "#9ec3ef", "#2a78d6", "#0d3f7f"])
    fig, ax = plt.subplots(figsize=(8.5, 3.4))
    im = ax.imshow(piv.to_numpy(), cmap=cmap, aspect="auto")
    ax.set_xticks(range(piv.shape[1]), piv.columns, rotation=35, ha="right", fontsize=7)
    ax.set_yticks(range(piv.shape[0]), piv.index, fontsize=8)
    vmax = np.nanmax(piv.to_numpy())
    for i in range(piv.shape[0]):
        for j in range(piv.shape[1]):
            v = piv.iat[i, j]
            if not np.isnan(v):
                ax.text(j, i, f"{v:.2f}", ha="center", va="center", fontsize=7,
                        color="white" if v > 0.55 * vmax else INK)
    ax.set_title("Mean output semantic distance, model x operator (treatment pairs)", loc="left",
                 fontsize=10.5, color=INK)
    fig.colorbar(im, ax=ax, fraction=0.025, pad=0.02)
    fig.tight_layout()
    fig.savefig(fig_dir / "fig4_model_operator_heatmap.png", dpi=200)
    plt.close(fig)
    made.append("fig4_model_operator_heatmap.png")

    # F5 input distance vs output distance (dose-response) with binned means.
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.6), sharey=True)
    for ax, col, label in ((axes[0], "d_in_char", "input character distance (normalised)"),
                           (axes[1], "d_in_sem", "input semantic distance (1 - cosine)")):
        x = t[col].to_numpy()
        y = t[PRIMARY].to_numpy()
        ax.scatter(x, y, s=8, alpha=0.25, color=SERIES[0], edgecolors="none")
        bins = np.quantile(x, np.linspace(0, 1, 9))
        bins = np.unique(bins)
        if len(bins) > 2:
            idx = np.clip(np.digitize(x, bins[1:-1]), 0, len(bins) - 2)
            bx = [x[idx == k].mean() for k in range(len(bins) - 1) if (idx == k).any()]
            by = [y[idx == k].mean() for k in range(len(bins) - 1) if (idx == k).any()]
            ax.plot(bx, by, color=SERIES[1], lw=2, marker="o", ms=4, label="binned mean (octiles)")
        rho = st.spearman(x, y)
        _style(ax, f"Spearman rho = {rho['rho']:.2f}" if rho["rho"] is not None else "", label,
               "output semantic distance" if col == "d_in_char" else None)
        ax.grid(axis="y", color=GRID, linewidth=0.6)
    axes[0].legend(frameon=False, fontsize=7)
    fig.suptitle("Input change vs output change (treatment pairs, all models)", x=0.01, ha="left",
                 fontsize=11, color=INK)
    fig.tight_layout()
    fig.savefig(fig_dir / "fig5_input_vs_output_distance.png", dpi=200)
    plt.close(fig)
    made.append("fig5_input_vs_output_distance.png")

    # F6 by task category: treatment vs control, plus flip rate.
    cats = sorted(pairs["task_category"].unique())
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.4))
    for k, cond in enumerate(("control", "treatment")):
        vals = [pairs[(pairs["task_category"] == c) & (pairs["condition"] == cond)][PRIMARY].mean()
                for c in cats]
        axes[0].barh(np.arange(len(cats)) + (0.2 if cond == "control" else -0.2), vals, height=0.38,
                     color="#b9b8b3" if cond == "control" else SERIES[0], label=cond)
    axes[0].set_yticks(range(len(cats)), cats)
    _style(axes[0], "Mean output semantic distance", "1 - cosine")
    axes[0].legend(frameon=False, fontsize=7)
    fc = {r["task_category"]: r for r in results["correctness"]["flips_by_category"]
          if r["condition"] == "treatment"}
    axes[1].barh(range(len(cats)), [fc.get(c, {}).get("any_flip_rate", np.nan) for c in cats],
                 color=SERIES[1], height=0.6)
    axes[1].set_yticks(range(len(cats)), [""] * len(cats))
    _style(axes[1], "Correctness flip rate (treatment)", "share of pairs")
    fig.suptitle("Sensitivity by task category (all models)", x=0.01, ha="left", fontsize=11, color=INK)
    fig.tight_layout()
    fig.savefig(fig_dir / "fig6_task_category.png", dpi=200)
    plt.close(fig)
    made.append("fig6_task_category.png")

    # F7 anchor accuracy by model.
    acc = results["correctness"]["anchor_accuracy_by_model"]
    fig, ax = plt.subplots(figsize=(7, 3.0))
    for i, r in enumerate(acc):
        ax.barh(i, r["mean"], color=color[r["model"]], height=0.6)
        ax.text(r["mean"] + 0.01, i, f"{r['mean']:.0%} (n={r['n']})", va="center", fontsize=8, color=INK2)
    ax.set_yticks(range(len(acc)), [r["model"] for r in acc])
    ax.set_xlim(0, 1.1)
    _style(ax, "Baseline (unperturbed) accuracy on the 50 scored items", "accuracy")
    fig.tight_layout()
    fig.savefig(fig_dir / "fig7_anchor_accuracy.png", dpi=200)
    plt.close(fig)
    made.append("fig7_anchor_accuracy.png")
    return made


# ----------------------------------------------------------------------------- main
def to_jsonable(obj):
    if isinstance(obj, dict):
        return {str(k): to_jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [to_jsonable(v) for v in obj]
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return None if np.isnan(obj) else float(obj)
    if isinstance(obj, float) and np.isnan(obj):
        return None
    if isinstance(obj, (np.bool_,)):
        return bool(obj)
    return obj


def md_table(rows: list[dict], cols: list[str], fmt: dict | None = None) -> str:
    fmt = fmt or {}
    lines = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for r in rows:
        cells = []
        for c in cols:
            v = r.get(c)
            if v is None or (isinstance(v, float) and np.isnan(v)):
                cells.append("–")
            elif c in fmt:
                cells.append(fmt[c].format(v))
            elif isinstance(v, float):
                cells.append(f"{v:.4f}" if abs(v) < 1000 else f"{v:.1f}")
            else:
                cells.append(str(v))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--study-dir", type=Path, required=True)
    args = parser.parse_args()
    study_dir = args.study_dir if args.study_dir.is_absolute() else ROOT / args.study_dir
    raw_dir = study_dir / "raw"
    out_dir = study_dir / "analysis"
    proc_dir = study_dir / "processed"
    out_dir.mkdir(exist_ok=True)
    proc_dir.mkdir(exist_ok=True)
    manifest = json.loads((study_dir / "study_manifest.json").read_text(encoding="utf-8"))

    # ---- CP11.1 raw-data integrity
    raw_manifest = {p.name: {"sha256": file_sha256(p), "lines": sum(1 for _ in p.open(encoding="utf-8"))}
                    for p in sorted(raw_dir.glob("*.jsonl"))}
    gen_rows, fail_rows = [], []
    for p in sorted(raw_dir.glob("generations__*.jsonl")):
        gen_rows += load_jsonl(p)
    for p in sorted(raw_dir.glob("failures__*.jsonl")):
        fail_rows += load_jsonl(p)
    malformed = sum(1 for r in gen_rows if r.get("_malformed"))
    gen_rows = [r for r in gen_rows if not r.get("_malformed")]
    gens = pd.DataFrame(gen_rows)
    if gens.empty:
        raise SystemExit("No generations found")
    gens = gens[gens["execution_mode"] == "live"] if "execution_mode" in gens else gens
    key = ["model", "prompt_id", "condition", "operator", "repetition"]
    gens["operator"] = gens["operator"].astype(object).where(gens["operator"].notna(), None)
    dup_mask = gens.duplicated(subset=key, keep="first")
    duplicate_count = int(dup_mask.sum())
    dup_ids = gens.loc[dup_mask, "record_id"].tolist()
    gens = gens[~dup_mask].reset_index(drop=True)
    record_id_dupes = int(gens["record_id"].duplicated().sum())
    candidates = pd.DataFrame(load_jsonl(study_dir / "candidates.jsonl"))
    accepted = candidates[candidates["status"] == "accepted"]
    n_prompts = len(manifest["selected_prompt_ids"])
    ctrl_reps = manifest["config"]["control_repetitions"]
    scheduled_per_model = n_prompts * (1 + ctrl_reps) + len(accepted)
    fail_df = pd.DataFrame(fail_rows)
    reconciliation = []
    for m in [x["name"] for x in manifest["config"]["models"]]:
        g = gens[gens["model"] == m]
        f = fail_df[fail_df["model"] == m] if not fail_df.empty else fail_df
        reconciliation.append({
            "model": m, "scheduled_generations": scheduled_per_model, "recorded_successes": len(g),
            "recorded_failures": len(f),
            "rate_limit_stops": int((f["error_type"] == "RateLimitError").sum()) if len(f) else 0,
            "not_attempted": scheduled_per_model - len(g),
            "truncated": int(g["finish_reason"].fillna("").str.casefold().isin(TRUNCATION_REASONS).sum()),
            "empty_outputs": int((g["output"].fillna("").str.strip() == "").sum()),
            "prompts_with_anchor": int((g["condition"] == "anchor").sum()),
        })

    # ---- scoring and pairing (CP11.3)
    gens = score_generations(gens, proc_dir / "code_test_cache.json")
    pairs, exclusions = build_pairs(gens, candidates)
    pairs = add_output_metrics(pairs)
    pairs["taxonomy"] = [taxonomy(r) for r in pairs.itertuples()]
    audit_path = ROOT / "config/experiments/main_study_semantic_audit.yaml"
    audit = yaml.safe_load(audit_path.read_text(encoding="utf-8")) if audit_path.exists() else {}
    flagged = {(a["prompt_id"], a["operator"]): a["kind"] for a in audit.get("meaning_altering", [])}
    pairs["audit_meaning_altering"] = [
        (pid, op) in flagged for pid, op in zip(pairs["prompt_id"], pairs["operator"])]
    pairs["audit_kind"] = [flagged.get((pid, op)) for pid, op in zip(pairs["prompt_id"], pairs["operator"])]
    pairs["audit_status"] = np.select(
        [pairs["condition"] == "control", pairs["audit_meaning_altering"], pairs["operator"] == "random_edit"],
        ["control", "meaning_altering", "noise_control_unaudited"], default="audit_valid")
    ident = pairs["identical_output"]
    consistency = {
        "identical_outputs_with_answer_change": int((ident & (pairs["answer_changed"] == 1)).sum()),
        "identical_outputs_with_nonzero_d_out_sem": int((ident & (pairs["d_out_sem"] > 0)).sum()),
        "identical_outputs_with_correctness_flip": int((ident & pairs["flip_any"]).sum()),
        "metric_values_outside_0_1": int(sum(((pairs[m] < 0) | (pairs[m] > 1)).sum()
                                             for m in ("d_out_sem", "d_out_char", "d_out_token"))),
        "nan_in_primary_metric": int(pairs["d_out_sem"].isna().sum()),
        "control_pairs_with_nonzero_input_distance": int(
            ((pairs["condition"] == "control") & (pairs["d_in_char"] != 0)).sum()),
    }
    if any(consistency.values()):
        raise SystemExit(f"Analysis-dataset consistency check failed: {consistency}")
    gens.drop(columns=["prompt_text"]).to_csv(proc_dir / "generations_scored.csv", index=False)
    pairs.to_csv(proc_dir / "analysis_pairs.csv", index=False)
    pd.DataFrame(exclusions).to_csv(proc_dir / "exclusions.csv", index=False)

    results: dict = {
        "generated_at": datetime.now(UTC).isoformat(),
        "study_id": manifest["study_id"],
        "primary_outcome": PRIMARY,
        "metric_definitions": METRICS,
        "data_integrity": {
            "raw_files": raw_manifest, "malformed_lines": malformed,
            "duplicate_generation_keys_dropped": duplicate_count, "duplicate_record_ids": dup_ids,
            "record_id_collisions_after_dedupe": record_id_dupes,
            "exclusions": len(exclusions), "reconciliation": reconciliation,
            "consistency_checks_all_zero": consistency,
            "n_generations_live": len(gens), "n_pairs": len(pairs),
            "n_treatment_pairs": int((pairs["condition"] == "treatment").sum()),
            "n_control_pairs": int((pairs["condition"] == "control").sum()),
            "candidates_total": len(candidates), "candidates_accepted": len(accepted),
            "candidates_rejected_by_operator": candidates[candidates["status"] != "accepted"]
            .groupby("operator").size().to_dict(),
        },
    }
    logger.info("Pairs: %d (%d treatment)", len(pairs), results["data_integrity"]["n_treatment_pairs"])

    # ---- descriptive (CP11.5)
    desc = []
    for (m, cond), g in pairs.groupby(["model", "condition"]):
        for metric in METRICS:
            desc.append({"model": m, "condition": cond, "metric": metric, **st.describe(g[metric].dropna())})
    for cond, g in pairs.groupby("condition"):
        for metric in METRICS:
            desc.append({"model": "ALL MODELS", "condition": cond, "metric": metric,
                         **st.describe(g[metric].dropna())})
    results["descriptive"] = desc
    results["input_distance_by_operator"] = [
        {"operator": op, "n_candidates": len(g), **{f"char_{k}": v for k, v in st.describe(g["d_in_char"]).items()
                                                  if k in ("mean", "min", "max")},
         **{f"sem_{k}": v for k, v in st.describe(g["d_in_sem"]).items() if k in ("mean", "min", "max")},
         "risk_levels": g["semantic_risk"].value_counts().to_dict()}
        for op, g in pairs[pairs["condition"] == "treatment"].drop_duplicates(["prompt_id", "operator"])
        .groupby("operator")
    ]

    # ---- inferential (CP11.6-11.8)
    results["treatment_vs_control"] = {m: treatment_vs_control(pairs, m) for m in METRICS}
    results["per_operator_primary"] = per_operator_vs_control(pairs, PRIMARY)
    results["per_operator_answer_change"] = per_operator_vs_control(pairs, "answer_changed")
    family_rows = []
    for fam, g in pairs[pairs["condition"] == "treatment"].groupby("family"):
        b = st.cluster_bootstrap_mean(g[PRIMARY], g["prompt_id"])
        family_rows.append({"family": fam, **b, "flip_rate": float(g.loc[g["scorable"], "flip_any"].mean())})
    results["per_family"] = family_rows
    fam_groups = {f: g[PRIMARY].to_numpy() for f, g in pairs[pairs["condition"] == "treatment"].groupby("family")}
    results["kruskal_family"] = st.kruskal_epsilon_squared(list(fam_groups.values()))
    op_groups = [g[PRIMARY].to_numpy() for _, g in pairs[pairs["condition"] == "treatment"].groupby("operator")]
    results["kruskal_operator"] = st.kruskal_epsilon_squared(op_groups)

    t = pairs[pairs["condition"] == "treatment"]
    pm = t.groupby(["prompt_id", "task_category"])[PRIMARY].mean().reset_index()
    results["kruskal_task_category_prompt_level"] = st.kruskal_epsilon_squared(
        [g[PRIMARY].to_numpy() for _, g in pm.groupby("task_category")])
    results["task_category_summary"] = [
        {"task_category": c, **st.cluster_bootstrap_mean(g[PRIMARY], g["prompt_id"]),
         "flip_rate": float(g.loc[g["scorable"], "flip_any"].mean()),
         "answer_change_rate": float(g["answer_changed"].mean()) if g["answer_changed"].notna().any() else None}
        for c, g in t.groupby("task_category")
    ]
    mp = t.groupby(["prompt_id", "model"])[PRIMARY].mean().unstack()
    complete = mp.dropna()
    results["friedman_models"] = {**st.friedman_kendall_w(complete.to_numpy()),
                                  "models": list(complete.columns)}
    pairwise = []
    cols = list(complete.columns)
    for i in range(len(cols)):
        for j in range(i + 1, len(cols)):
            w = st.wilcoxon_paired((complete[cols[i]] - complete[cols[j]]).to_numpy())
            pairwise.append({"model_a": cols[i], "model_b": cols[j],
                             "mean_a": float(complete[cols[i]].mean()), "mean_b": float(complete[cols[j]].mean()),
                             "p_value": w["p_value"], "rank_biserial": w["rank_biserial"]})
    for r, p in zip(pairwise, st.holm_adjust([r["p_value"] or 1.0 for r in pairwise])):
        r["p_holm"] = p
    results["model_pairwise"] = pairwise
    results["model_summary"] = [
        {"model": m, **st.cluster_bootstrap_mean(g[PRIMARY], g["prompt_id"]),
         "answer_change_rate": float(g["answer_changed"].mean()),
         "flip_rate": float(g.loc[g["scorable"], "flip_any"].mean()),
         "c2i_rate": float(g.loc[g["scorable"], "flip_c2i"].mean()),
         "share_identical": float(g["identical_output"].mean())}
        for m, g in t.groupby("model")
    ]
    results["correctness"] = correctness_tables(pairs, gens)
    tsc = pairs[(pairs["condition"] == "treatment") & pairs["scorable"]]
    results["correctness"]["flips_by_audit_status"] = [
        {"audit_status": s_, "n_pairs": len(g), "c2i": int(g["flip_c2i"].sum()), "i2c": int(g["flip_i2c"].sum()),
         "c2i_rate": float(g["flip_c2i"].mean()), "i2c_rate": float(g["flip_i2c"].mean()),
         **{f"any_flip_{k}": v for k, v in st.cluster_bootstrap_mean(
             g["flip_any"].astype(float), g["prompt_id"]).items() if k in ("mean", "ci_low", "ci_high")}}
        for s_, g in tsc.groupby("audit_status")
    ]
    results["semantic_audit"] = {"file": str(audit_path.relative_to(ROOT)), "n_flagged_candidates": len(flagged),
                                 "n_flagged_treatment_pairs": int(pairs["audit_meaning_altering"].sum())}
    results["mixed_model_primary"] = mixed_model(pairs, PRIMARY)
    results["dose_response"] = [
        {"model": m, "spearman_char": st.spearman(g["d_in_char"], g[PRIMARY]),
         "spearman_sem": st.spearman(g["d_in_sem"], g[PRIMARY])}
        for m, g in [("ALL MODELS", t)] + list(t.groupby("model"))
    ]
    sens = t["sensitivity_ratio"]
    results["sensitivity_ratio"] = {
        "definition": "d_out_sem / (0.5*d_in_char + 0.5*d_in_sem + 1e-4)",
        **st.describe(sens), "near_zero_denominator_pairs": int(t["near_zero_denominator"].sum()),
        "share_of_top_decile_with_near_zero_denominator": float(
            t.loc[sens >= sens.quantile(0.9), "near_zero_denominator"].mean()),
        "tail_q95": float(sens.quantile(0.95)), "tail_q99": float(sens.quantile(0.99)),
    }
    try:
        from apsa.analysis.extreme_value import ExtremeValueAnalyzer

        evt = ExtremeValueAnalyzer().fit(list(sens.dropna()))
        results["sensitivity_ratio"]["evt_gev_fit_top5pct"] = evt.__dict__
    except Exception as e:  # noqa: BLE001 - report instead of failing
        results["sensitivity_ratio"]["evt_gev_fit_top5pct"] = {"status": f"not fitted: {e}"}
    results["budget_maxima"] = budget_maxima(pairs)
    results["adversarial_selection"] = adversarial_selection(pairs)
    results["robustness"] = robustness(pairs)
    tax = pairs.groupby(["condition", "taxonomy"]).size().unstack(fill_value=0)
    results["taxonomy_by_condition"] = tax.to_dict(orient="index")
    results["taxonomy_by_operator"] = (
        t.groupby(["operator", "taxonomy"]).size().unstack(fill_value=0).to_dict(orient="index"))
    results["taxonomy_by_model"] = (
        t.groupby(["model", "taxonomy"]).size().unstack(fill_value=0).to_dict(orient="index"))

    # ---- case studies (CP15.2): systematic selection rules
    cases = []
    flips = t[t["flip_c2i"]].sort_values(["d_in_char", PRIMARY], ascending=[True, False])
    valid_flips = flips[flips["audit_status"] == "audit_valid"]
    cases += [("smallest-input C->I flips, audit-valid perturbations", r)
              for _, r in valid_flips.head(8).iterrows()]
    cases += [("C->I flips caused by meaning-altering perturbations (audit)", r)
              for _, r in flips[flips["audit_status"] == "meaning_altering"].head(3).iterrows()]
    big = t[~t["flip_any"] & ~t["any_truncated"]].sort_values(PRIMARY, ascending=False)
    cases += [("largest semantic change without correctness change", r) for _, r in big.head(3).iterrows()]
    ctrl_nz = pairs[(pairs["condition"] == "control") & ~pairs["identical_output"]].sort_values(
        PRIMARY, ascending=False)
    cases += [("unchanged-prompt control with output change", r) for _, r in ctrl_nz.head(3).iterrows()]
    imp = t[t["flip_i2c"]].sort_values("d_in_char")
    cases += [("perturbation fixed an incorrect answer (I->C)", r) for _, r in imp.head(2).iterrows()]
    prompts = {r["prompt_id"]: r for r in pd.read_csv(ROOT / manifest["dataset_path"]).to_dict("records")}
    case_records = []
    for rule, r in cases:
        case_records.append({
            "selection_rule": rule, "pair_id": r["pair_id"], "model": r["model"],
            "prompt_id": r["prompt_id"], "task_category": r["task_category"], "operator": r["operator"],
            "original_prompt": prompts[r["prompt_id"]]["original_prompt"],
            "perturbed_prompt": r["perturbed_prompt"],
            "expected_answer": prompts[r["prompt_id"]]["expected_answer"],
            "d_in_char": r["d_in_char"], "d_in_sem": r["d_in_sem"], "d_out_sem": r[PRIMARY],
            "d_out_char": r["d_out_char"], "anchor_correct": r["anchor_correct"],
            "comparison_correct": r["comparison_correct"], "taxonomy": r["taxonomy"],
            "audit_status": r["audit_status"], "audit_kind": r["audit_kind"],
            "anchor_output": r["anchor_output"], "comparison_output": r["comparison_output"],
            "anchor_record_id": r["anchor_record_id"], "comparison_record_id": r["comparison_record_id"],
        })
    (out_dir / "case_studies.json").write_text(json.dumps(to_jsonable(case_records), indent=2),
                                               encoding="utf-8")

    results["figures"] = make_figures(pairs, results, out_dir / "figures")
    (out_dir / "results.json").write_text(json.dumps(to_jsonable(results), indent=2), encoding="utf-8")

    # ---- compact markdown tables for the report
    md = [f"# APSA study results tables - {manifest['study_id']}",
          f"Generated {results['generated_at']} from `processed/analysis_pairs.csv`.\n",
          "## Data reconciliation", md_table(reconciliation, list(reconciliation[0].keys())),
          "\n## Treatment vs control (prompt-level paired differences)",
          md_table([r for m in METRICS for r in results["treatment_vs_control"][m]],
                   ["model", "metric", "n_model_prompt_units", "mean_treatment", "mean_control",
                    "mean_diff", "diff_ci_low", "diff_ci_high", "p_value", "rank_biserial"],
                   {"p_value": "{:.2e}"}),
          "\n## Per-operator effect on primary outcome (vs control)",
          md_table(results["per_operator_primary"],
                   ["operator", "family", "n_pairs", "mean_treatment", "mean_diff_vs_control", "ci_low",
                    "ci_high", "p_holm", "rank_biserial", "cliffs_delta_vs_control", "cliffs_magnitude"],
                   {"p_holm": "{:.2e}"}),
          "\n## Correctness flips by operator",
          md_table(results["correctness"]["flips_by_operator"],
                   ["operator", "n_pairs", "c2i", "i2c", "any_flip_rate", "ci_low", "ci_high",
                    "net_accuracy_change", "mcnemar_p_holm"]),
          "\n## Flip rates by model and condition",
          md_table(results["correctness"]["flip_rates_by_model_condition"],
                   ["model", "condition", "n_pairs", "comparison_accuracy", "c2i_mean", "c2i_ci_low",
                    "c2i_ci_high", "i2c_rate", "any_flip_rate"]),
          "\n## Model summary (treatment pairs)",
          md_table(results["model_summary"], ["model", "n", "mean", "ci_low", "ci_high", "answer_change_rate",
                                              "flip_rate", "c2i_rate", "share_identical"]),
          "\n## Anchor accuracy", md_table(results["correctness"]["anchor_accuracy_by_model"],
                                           ["model", "n", "mean", "ci_low", "ci_high"]),
          "\n## Task category summary (treatment)",
          md_table(results["task_category_summary"], ["task_category", "n", "mean", "ci_low", "ci_high",
                                                      "flip_rate", "answer_change_rate"]),
          "\n## Model pairwise (Wilcoxon, Holm)",
          md_table(pairwise, ["model_a", "model_b", "mean_a", "mean_b", "p_holm", "rank_biserial"]),
          "\n## Control repeatability",
          md_table(results["robustness"]["control_repeatability"],
                   ["model", "n_control_pairs", "share_identical", "mean_d_out_sem", "max_d_out_sem",
                    "control_answer_change_rate", "control_flip_rate"]),
          "\n## Specification curve (ALL MODELS, treatment minus control)",
          md_table(results["robustness"]["specification_curve"],
                   ["specification", "metric", "mean_diff", "diff_ci_low", "diff_ci_high", "p_value"],
                   {"p_value": "{:.2e}"}),
          "\n## Budgeted maxima", md_table(results["budget_maxima"],
                                           ["budget_metric", "epsilon", "n_candidates_evaluated",
                                            "mean_d_out_sem", "max_observed_d_out_sem", "argmax_pair",
                                            "c2i_flips_within_budget"]),
          "\n## Held-out operator selection (RQ5 proxy)",
          md_table(results["adversarial_selection"].get("held_out_operator_selection", []),
                   ["model", "chosen_operator", "discovery_mean", "validation_mean_chosen",
                    "validation_mean_random_edit", "n_validation_prompts", "p_value"]),
          ]
    (out_dir / "results_tables.md").write_text("\n".join(md), encoding="utf-8")
    logger.info("Analysis written to %s", out_dir)


if __name__ == "__main__":
    main()
