"""Writers for the category-operator workflow: CSVs, per-prompt reports, settings, figures."""

from __future__ import annotations

import csv
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .category_operators import (
    BOOTSTRAP_DRAWS, BOOTSTRAP_SEED, CATEGORY_LABELS, MEASURED, CategoryRanking, Measurement,
    PromptSelection, StudyData, _float_or_none, _truthy, budget_label, model_label,
    protected_content_changes, select_for_prompt,
)

RANKING_COLUMNS = [
    "category", "budget", "rank", "operator", "tied_with", "category_score", "n_prompts", "n_complete_prompts",
    "n_eligible_before_exclusions", "n_eligible_complete", "conditional_mean", "contrast", "paired_gap",
    "gap_ci_low", "gap_ci_high", "shared_eligible_n", "shared_eligible_gap", "c2i_flips", "i2c_flips",
    "n_scorable_pairs", "n_models", "evidence_status", "study_id",
]
MAXIMA_COLUMNS = [
    "budget", "prompt_id", "category", "model_scope", "n_models", "operator", "eligibility", "eligibility_detail",
    "measurement_status", "perturbation_id", "char_edits", "d_in_char", "d_in_sem", "auto_protected_changes",
    "raw_distance", "control_distance", "excess_distance", "rank_in_prompt", "is_selected", "prompt_status",
    "tie_status", "on_tradeoff_frontier", "correctness_before_after", "answer_changed_models", "pair_ids",
    "anchor_record_ids", "comparison_record_ids",
]
CASE_COLUMNS = [
    "category", "budget", "kind", "n_results_searched", "pair_id", "prompt_id", "model", "operator", "d_in_char",
    "char_edits", "raw_distance", "control_distance", "excess_distance", "anchor_correct", "comparison_correct",
    "answer_changed", "anchor_record_id", "comparison_record_id",
]


def _fmt(value: Any, digits: int = 4) -> Any:
    if isinstance(value, float):
        return round(value, 10)
    return value


def _write_csv(path: Path, columns: list[str], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({k: ("" if row.get(k) is None else _fmt(row.get(k))) for k in columns})


# --------------------------------------------------------------------------- category outputs
def write_rankings(path: Path, rankings: dict[tuple[str, str], CategoryRanking]) -> None:
    rows = [row for ranking in rankings.values() for row in ranking.rows]
    _write_csv(path, RANKING_COLUMNS, rows)


def write_exclusions(path: Path, rankings: dict[tuple[str, str], CategoryRanking]) -> None:
    rows = [e for ranking in rankings.values() for e in ranking.exclusions]
    _write_csv(path, ["category", "budget", "prompt_id", "reason"], rows)


def _case_row(data: StudyData, ranking: CategoryRanking, kind: str, m: Measurement) -> dict[str, Any]:
    cand = data.candidates[(m.prompt_id, m.operator)]
    row = m.row or {}
    return {"category": ranking.category, "budget": budget_label(ranking.budget), "kind": kind,
            "n_results_searched": len(ranking.observations), "pair_id": m.pair_id, "prompt_id": m.prompt_id,
            "model": m.model, "operator": m.operator,
            "d_in_char": cand["input_distances"]["char_levenshtein_normalized"],
            "char_edits": cand["input_distances"]["char_levenshtein"], "raw_distance": m.raw,
            "control_distance": m.control_mean, "excess_distance": m.excess,
            "anchor_correct": row.get("anchor_correct"), "comparison_correct": row.get("comparison_correct"),
            "answer_changed": row.get("answer_changed"), "anchor_record_id": row.get("anchor_record_id"),
            "comparison_record_id": row.get("comparison_record_id")}


def write_case_maxima(path: Path, data: StudyData, rankings: dict[tuple[str, str], CategoryRanking]) -> None:
    rows = []
    for ranking in rankings.values():
        rows += [_case_row(data, ranking, "max_raw_distance", m) for m in ranking.max_raw]
        rows += [_case_row(data, ranking, "max_excess_distance", m) for m in ranking.max_excess]
    _write_csv(path, CASE_COLUMNS, rows)


# --------------------------------------------------------------------------- prompt outputs
def _correctness(value: Any) -> str:
    flag = _truthy(value)
    return "unscored" if flag is None else ("correct" if flag else "incorrect")


def selection_rows(data: StudyData, sel: PromptSelection) -> list[dict[str, Any]]:
    measured = sorted((r for r in sel.operators if r.status == MEASURED), key=lambda r: -r.excess)
    ranks: dict[str, int] = {}
    for position, r in enumerate(measured, start=1):
        prev = measured[position - 2] if position > 1 else None
        ranks[r.operator] = ranks[prev.operator] if prev is not None and prev.excess == r.excess else position
    scope = "panel" if len(sel.models) > 1 else sel.models[0]
    rows = []
    for r in sel.operators:
        cand = r.candidate or {}
        protected = (protected_content_changes(sel.original_prompt, cand["perturbed_prompt"])
                     if sel.original_prompt and cand.get("perturbed_prompt") else [])
        before_after = [f"{model_label(m.model)}: {_correctness(m.row.get('anchor_correct'))}->"
                        f"{_correctness(m.row.get('comparison_correct'))}" for m in r.measurements if m.row]
        changed = [model_label(m.model) for m in r.measurements if m.row and _truthy(m.row.get("answer_changed"))]
        rows.append({
            "budget": budget_label(sel.budget), "prompt_id": sel.prompt_id, "category": sel.category,
            "model_scope": scope, "n_models": len(sel.models), "operator": r.operator,
            "eligibility": r.eligibility, "eligibility_detail": r.eligibility_detail,
            "measurement_status": r.status if r.eligibility == "eligible" else "not_measured",
            "perturbation_id": cand.get("perturbation_id"), "char_edits": r.char_edits,
            "d_in_char": r.d_in_char, "d_in_sem": r.d_in_sem, "auto_protected_changes": " | ".join(protected),
            "raw_distance": r.raw, "control_distance": r.control, "excess_distance": r.excess,
            "rank_in_prompt": ranks.get(r.operator), "is_selected": r.operator in sel.winners,
            "prompt_status": sel.status, "tie_status": sel.tie_status if r.operator in sel.winners else "",
            "on_tradeoff_frontier": r.operator in sel.pareto,
            "correctness_before_after": "; ".join(before_after),
            "answer_changed_models": "; ".join(changed),
            "pair_ids": ";".join(m.pair_id for m in r.measurements if m.pair_id),
            "anchor_record_ids": ";".join(m.row["anchor_record_id"] for m in r.measurements if m.row),
            "comparison_record_ids": ";".join(m.row["comparison_record_id"] for m in r.measurements if m.row),
        })
    return rows


def write_prompt_maxima(path: Path, data: StudyData, selections: list[PromptSelection]) -> None:
    rows = [row for sel in selections for row in selection_rows(data, sel)]
    _write_csv(path, MAXIMA_COLUMNS, rows)


def _measurement_record(m: Measurement) -> dict[str, Any]:
    row = m.row or {}
    return {
        "model": m.model, "model_label": model_label(m.model), "status": m.status, "pair_id": m.pair_id,
        "anchor_record_id": row.get("anchor_record_id"), "comparison_record_id": row.get("comparison_record_id"),
        "raw_distance": m.raw, "control_values": m.control_values, "control_distance": m.control_mean,
        "excess_distance": m.excess, "d_out_char": _float_or_none(row.get("d_out_char")),
        "d_out_token": _float_or_none(row.get("d_out_token")), "answer_changed": _truthy(row.get("answer_changed")),
        "anchor_correct": _truthy(row.get("anchor_correct")), "comparison_correct": _truthy(row.get("comparison_correct")),
        "anchor_final": row.get("anchor_final") or None, "comparison_final": row.get("comparison_final") or None,
        "scoring_method": row.get("scoring_method"),
        "code_signature_compliant": (None if row.get("scoring_method") != "unit_tests"
                                     else not _truthy(row.get("code_name_fallback"))),
        "taxonomy": row.get("taxonomy"), "anchor_output": row.get("anchor_output"),
        "comparison_output": row.get("comparison_output"),
    }


def selection_record(data: StudyData, sel: PromptSelection, *, ranking: CategoryRanking | None = None,
                     panel: PromptSelection | None = None) -> dict[str, Any]:
    """Machine-readable result for one prompt (Stage 7)."""
    operators = []
    for r in sel.operators:
        cand = r.candidate or {}
        operators.append({
            "operator": r.operator, "eligibility": r.eligibility, "eligibility_detail": r.eligibility_detail,
            "status": r.status, "perturbation_id": cand.get("perturbation_id"),
            "perturbed_prompt": cand.get("perturbed_prompt"), "char_edits": r.char_edits, "d_in_char": r.d_in_char,
            "d_in_sem": r.d_in_sem,
            "auto_protected_changes": (protected_content_changes(sel.original_prompt, cand["perturbed_prompt"])
                                       if sel.original_prompt and cand.get("perturbed_prompt") else []),
            "raw_distance": r.raw, "control_distance": r.control, "excess_distance": r.excess,
            "per_model": [_measurement_record(m) for m in r.measurements],
        })
    evidence = _evidence_notes(sel, ranking, panel)
    return {
        "prompt_id": sel.prompt_id, "category": sel.category, "original_prompt": sel.original_prompt,
        "reference_answer": sel.expected_answer, "study_id": sel.study_id, "evidence_mode": sel.evidence_mode,
        "selection_rule": {"mode": sel.mode, "budget": budget_label(sel.budget), "target": sel.target,
                           "tie_breaks": ["larger excess", "fewer character edits",
                                          "smaller normalised input distance"]
                           + (["larger excess among equal-size edits"] if sel.mode == "target" else [])},
        "model_scope": {"models": sel.models, "label": sel.scope_label},
        "status": sel.status, "selected": sel.winners, "tie_status": sel.tie_status,
        "explanation": sel.explanation, "provisional_best": sel.provisional_best,
        "best_achieved_excess": sel.best_achieved, "tradeoff_frontier": sel.pareto,
        "recommendation": sel.recommendation, "evidence_notes": evidence, "operators": operators,
        "generated_at": datetime.now(UTC).isoformat(),
    }


def _evidence_notes(sel: PromptSelection, ranking: CategoryRanking | None,
                    panel: PromptSelection | None) -> list[str]:
    notes = []
    if sel.evidence_mode == "retrospective":
        notes.append(f"Measured retrospectively from stored {sel.study_id} outputs; this prompt belongs to the "
                     "discovery set that produced the category ranking, so the result is exploratory.")
    chosen = sel.chosen
    if chosen and ranking is not None and len(sel.models) == 1:
        pair = next((m.pair_id for m in chosen.measurements), None)
        if any(m.pair_id == pair for m in ranking.max_raw):
            notes.append(f"Largest observed raw distance among the {len(ranking.observations)} eligible "
                         f"{CATEGORY_LABELS.get(sel.category, sel.category).lower()} results searched at budget "
                         f"{budget_label(sel.budget)}.")
        if any(m.pair_id == pair for m in ranking.max_excess):
            notes.append("It is also the largest observed excess distance in the category at this budget.")
    if panel is not None and panel is not sel and panel.chosen is not None:
        notes.append(f"Separate {len(panel.models)}-model panel result for {sel.prompt_id}: "
                     f"{', '.join(panel.winners)} led with mean excess {panel.chosen.excess:+.4f}. "
                     "The single-model case and the panel average are different quantities.")
    return notes


def _diff_text(original: str, perturbed: str) -> str:
    import difflib
    a, b = original.split(" "), perturbed.split(" ")
    parts = []
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if tag == "equal":
            continue
        parts.append(f"`{' '.join(a[i1:i2]) or '∅'}` → `{' '.join(b[j1:j2]) or '∅'}`")
    if not parts and original != perturbed:
        parts.append("whitespace or punctuation only")
    return "; ".join(parts)


def _functional_summary(m: Measurement) -> str:
    row = m.row or {}
    before, after = _correctness(row.get("anchor_correct")), _correctness(row.get("comparison_correct"))
    text = f"{before} → {after}"
    if row.get("scoring_method") == "unit_tests":
        text += " (unit tests" + ("; renamed entry point tested via fallback" if _truthy(row.get("code_name_fallback")) else "") + ")"
    if _truthy(row.get("answer_changed")):
        text += "; final answer text changed"
    elif row.get("anchor_final"):
        text += "; same final answer"
    a_len, c_len = len(row.get("anchor_output") or ""), len(row.get("comparison_output") or "")
    return f"{text}; response length {a_len} → {c_len} characters"


def render_markdown(record: dict[str, Any], sel: PromptSelection) -> str:
    cat = CATEGORY_LABELS.get(sel.category, sel.category)
    lines = [f"# Perturbation operator result: {sel.prompt_id} · {cat}", ""]
    rule = (f"budget mode, d_in_char ≤ {budget_label(sel.budget)}" if sel.mode == "budget"
            else f"target mode, excess ≥ {sel.target:.4f}, budget {budget_label(sel.budget)}")
    lines += [f"**Status:** `{sel.status}` · **Rule:** {rule} · **Model scope:** {sel.scope_label} · "
              f"**Evidence:** {sel.evidence_mode}", ""]
    rec = sel.recommendation
    lines += ["## 1. Category recommendation", "",
              f"- Recommended: **{', '.join(rec.get('operators') or ['none'])}** "
              f"({rec.get('evidence_status')}; source: {rec.get('source')})"]
    if rec.get("category_score") is not None:
        lines.append(f"- Category score {rec['category_score']:.4f}, coverage {rec.get('coverage')}")
    if rec.get("rationale"):
        lines.append(f"- Why: {rec['rationale']}")
    if rec.get("note"):
        lines.append(f"- Note: {rec['note']}")
    lines += ["- A category recommendation is not a measurement of this prompt; the measured result follows.", ""]

    chosen = sel.chosen
    lines += ["## 2. Measured result for this prompt", "", sel.explanation, ""]
    if chosen is not None:
        cand = chosen.candidate
        best = max(chosen.measurements, key=lambda m: m.excess)
        lines += ["| Field | Result |", "|---|---|",
                  f"| Prompt and category | `{sel.prompt_id}` · {cat} |",
                  f"| Original prompt | {sel.original_prompt} |",
                  f"| Perturbed prompt | {cand['perturbed_prompt']} |",
                  f"| Operator | `{chosen.operator}`: {_diff_text(sel.original_prompt or '', cand['perturbed_prompt'])} |",
                  f"| Input change | **{chosen.char_edits} character edit(s)**, normalised distance "
                  f"**{chosen.d_in_char:.4f}**, semantic input distance {chosen.d_in_sem:.4f} |",
                  f"| Model and comparison | {sel.scope_label}; {len(chosen.measurements)} matched model–prompt "
                  f"pair(s) from `{sel.study_id}` |",
                  f"| Output change | Semantic distance **{chosen.raw:.4f}**, mean unchanged control distance "
                  f"**{chosen.control:.4f}**, excess distance **{chosen.excess:+.4f}** |",
                  f"| Functional result | " + "; ".join(
                      f"{model_label(m.model)}: {_functional_summary(m)}" for m in chosen.measurements) + " |",
                  f"| Tie status | {sel.tie_status} |",
                  f"| Evidence status | {' '.join(record['evidence_notes'])} |", ""]
        label = "Response" if len(sel.models) == 1 else f"Responses of {model_label(best.model)} (largest effect in the panel)"
        lines += [f"### {label}", "", "**Original prompt response**", "", "```text",
                  (best.row.get("anchor_output") or "").strip(), "```", "",
                  "**Perturbed prompt response**", "", "```text", (best.row.get("comparison_output") or "").strip(),
                  "```", ""]
    lines += ["## 3. All operators", "",
              "| Operator | Status | Char edits | d_in_char | Raw | Control | Excess | Correctness (before → after) |",
              "|---|---|---:|---:|---:|---:|---:|---|"]
    for r in sorted(sel.operators, key=lambda r: (r.excess is None, -(r.excess or 0), r.operator)):
        corr = "; ".join(f"{model_label(m.model)} {_correctness(m.row.get('anchor_correct'))}→"
                         f"{_correctness(m.row.get('comparison_correct'))}" for m in r.measurements if m.row)
        status = r.status if r.eligibility == "eligible" else f"{r.eligibility}: {r.eligibility_detail}"
        mark = " **(selected)**" if r.operator in sel.winners else ""
        fmt = lambda v: "" if v is None else f"{v:.4f}"
        lines.append(f"| `{r.operator}`{mark} | {status} | {'' if r.char_edits is None else r.char_edits} | "
                     f"{fmt(r.d_in_char)} | {fmt(r.raw)} | {fmt(r.control)} | "
                     f"{'' if r.excess is None else f'{r.excess:+.4f}'} | {corr} |")
    lines.append("")
    if sel.pareto:
        lines += ["## 4. Input–output trade-off", "",
                  "Eligible edits not dominated by another edit with no more character edits and at least as much "
                  "excess change:", ""]
        for op in sel.pareto:
            r = sel.result(op)
            lines.append(f"- `{op}`: {r.char_edits} character edit(s) → excess {r.excess:+.4f}")
        lines.append("")
    lines += ["## 5. Source records", "",
              "Full responses, per-model scores and record IDs are in the JSON file next to this report.", ""]
    for r in sel.operators:
        for m in r.measurements:
            if m.row and r.operator in sel.winners:
                lines.append(f"- `{m.pair_id}`: anchor record `{m.row.get('anchor_record_id')}`, "
                             f"comparison record `{m.row.get('comparison_record_id')}`")
    lines.append("")
    return "\n".join(lines)


def report_stem(sel: PromptSelection) -> str:
    scope = "panel" if len(sel.models) > 1 else sel.models[0].replace("/", "_")
    suffix = f"target-{sel.target:g}_" if sel.target is not None else ""
    return f"{sel.prompt_id}__{scope}__{suffix}budget-{budget_label(sel.budget)}"


def write_prompt_report(out_dir: Path, data: StudyData, sel: PromptSelection, *,
                        ranking: CategoryRanking | None = None) -> tuple[Path, Path]:
    panel = None
    if len(sel.models) == 1:
        panel = select_for_prompt(data, sel.prompt_id, budget=sel.budget, target=sel.target)
    record = selection_record(data, sel, ranking=ranking, panel=panel)
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = report_stem(sel)
    json_path, md_path = out_dir / f"{stem}.json", out_dir / f"{stem}.md"
    json_path.write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")
    md_path.write_text(render_markdown(record, sel), encoding="utf-8")
    return md_path, json_path


def write_settings(path: Path, data: StudyData, budgets: list[float | None],
                   rankings: dict[tuple[str, str], CategoryRanking], extra: dict[str, Any] | None = None) -> None:
    payload = {
        "generated_at": datetime.now(UTC).isoformat(), "study_id": data.study_id,
        "evidence_mode": data.evidence_mode, "models": data.models, "operators": data.operators,
        "noise_operators_excluded": ["random_edit"], "control_repetitions": data.control_repetitions,
        "budgets": [budget_label(b) for b in budgets], "eligibility": "0 < d_in_char <= budget, accepted, "
        "not flagged (retrospective) or final verdict 'preserved' (validation)",
        "bootstrap": {"seed": BOOTSTRAP_SEED, "draws": BOOTSTRAP_DRAWS, "interval": "percentile 2.5-97.5"},
        "source_sha256": data.source_hashes, "verdict_agreement": data.verdict_agreement,
        "complete_cohorts": {f"{c}@{b}": r.complete for (c, b), r in rankings.items()},
        **(extra or {}),
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def write_nominees(path: Path, data: StudyData, rankings: dict[tuple[str, str], CategoryRanking],
                   budget: float | None) -> dict[str, Any]:
    """Lock the discovery leaders (plan Section 4, step 1). Ties are recorded, not resolved."""
    nominees, ties = {}, {}
    for (cat, label), ranking in rankings.items():
        if label != budget_label(budget):
            continue
        if len(ranking.leaders) == 1:
            nominees[cat] = ranking.leaders[0]
        else:
            ties[cat] = ranking.leaders
    payload = {"locked_at": datetime.now(UTC).isoformat(), "discovery_study_id": data.study_id,
               "budget": budget_label(budget), "nominees": nominees, "unresolved_ties": ties,
               "operators": data.operators, "models": data.models, "control_repetitions": data.control_repetitions,
               "discovery_source_sha256": data.source_hashes,
               "note": "Exploratory discovery leaders. A category winner is confirmed only by the held-out "
                       "protocol (validate command) on new prompts."}
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


# --------------------------------------------------------------------------- figures
def write_figures(fig_dir: Path, rankings: dict[tuple[str, str], CategoryRanking], budget: float | None,
                  operators: list[str]) -> list[Path]:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    label = budget_label(budget)
    cats = sorted(c for c, b in rankings if b == label)
    if not cats:
        return []
    fig_dir.mkdir(parents=True, exist_ok=True)
    grid = np.full((len(operators), len(cats)), np.nan)
    notes = [["" for _ in cats] for _ in operators]
    for j, cat in enumerate(cats):
        r = rankings[(cat, label)]
        for row in r.rows:
            i = operators.index(row["operator"])
            grid[i, j] = row["category_score"]
            notes[i][j] = (f"{row['category_score']:.3f}\n({row['n_eligible_complete']}/{row['n_complete_prompts']})"
                           if row["n_eligible_complete"] else "—")
    fig, ax = plt.subplots(figsize=(9, 6.2))
    im = ax.imshow(grid, cmap="Blues", aspect="auto", vmin=0)
    for i in range(len(operators)):
        for j in range(len(cats)):
            leader = notes[i][j] and rankings[(cats[j], label)].rows and operators[i] in rankings[(cats[j], label)].leaders
            ax.text(j, i, notes[i][j], ha="center", va="center", fontsize=8.5,
                    fontweight="bold" if leader else "normal",
                    color="white" if np.nan_to_num(grid[i, j]) > np.nanmax(grid) * 0.6 else "#1f2633")
    ax.set_xticks(range(len(cats)), [CATEGORY_LABELS.get(c, c) for c in cats], rotation=20, ha="right")
    ax.set_yticks(range(len(operators)), operators)
    ax.set_title(f"Mean excess semantic distance by category and operator (budget {label})\n"
                 "cell: score (eligible/complete prompts); bold = category leader", fontsize=10, loc="left")
    fig.colorbar(im, ax=ax, fraction=0.03, label="mean excess d_out_sem")
    fig.tight_layout()
    heat = fig_dir / f"category_operator_heatmap_budget-{label}.png"
    fig.savefig(heat, dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8.5, 3.8))
    ys, labels = [], []
    for k, cat in enumerate(cats):
        top = rankings[(cat, label)].rows[0] if rankings[(cat, label)].rows else None
        if top is None or top["paired_gap"] is None:
            continue
        ax.errorbar(top["paired_gap"], k, xerr=[[top["paired_gap"] - top["gap_ci_low"]],
                                                 [top["gap_ci_high"] - top["paired_gap"]]],
                    fmt="o", color="#2A78D6", capsize=4)
        ys.append(k)
        labels.append(f"{CATEGORY_LABELS.get(cat, cat)}\n{top['contrast']}")
    ax.axvline(0, color="#888", ls="--", lw=1)
    ax.set_yticks(ys, labels, fontsize=8)
    ax.set_xlabel("paired gap in mean excess d_out_sem (leader − runner-up), 95% bootstrap interval")
    ax.set_title(f"Leader vs runner-up by category (budget {label}; exploratory)", fontsize=10, loc="left")
    fig.tight_layout()
    gap = fig_dir / f"category_operator_gaps_budget-{label}.png"
    fig.savefig(gap, dpi=180)
    plt.close(fig)
    return [heat, gap]
