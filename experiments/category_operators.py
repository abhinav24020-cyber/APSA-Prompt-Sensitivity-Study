"""Category-based perturbation-operator selection (offline; no provider calls).

Implements docs/roadmap/category_operator_implementation_plan.md on a finished study.

Commands (PowerShell, from the repository root):

  # Everything for main_v1: rankings at all budgets, maxima, figures, nominees, per-prompt reports
  .\\.venv\\Scripts\\python.exe experiments\\category_operators.py all

  # Category rankings only
  .\\.venv\\Scripts\\python.exe experiments\\category_operators.py rank --budgets 0.01 0.02 0.05 0.10 none

  # One stored prompt: budget mode (default 0.10), five-model panel or a single model
  .\\.venv\\Scripts\\python.exe experiments\\category_operators.py prompt --prompt-id LOGIC-010 --model gpt-oss-120b

  # Target mode: smallest eligible edit whose control-adjusted change reaches 0.10
  .\\.venv\\Scripts\\python.exe experiments\\category_operators.py prompt --prompt-id CLASS-002 --target 0.10

  # A new prompt (unmeasured): recommendation + audited candidates + verdict template
  .\\.venv\\Scripts\\python.exe experiments\\category_operators.py prompt --text "..." --category logical_reasoning

  # Held-out claim rule on a separate validation study (after run_study + analyze_study)
  .\\.venv\\Scripts\\python.exe experiments\\category_operators.py validate --study-dir results\\study\\cat_val_v1 ^
      --verdicts path\\to\\verdicts.csv --nominees results\\study\\main_v1\\analysis\\category_operator_nominees.json
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))

from apsa.analysis import category_operator_reports as rep  # noqa: E402
from apsa.analysis import category_operators as co  # noqa: E402
from apsa.analysis.prompt_categories import suggest_category  # noqa: E402

DEFAULT_STUDY = ROOT / "results" / "study" / "main_v1"


def _show(path: Path) -> str:
    """Repository-relative path when possible, absolute otherwise."""
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def _study_dir(path: str | None) -> Path:
    return (ROOT / path).resolve() if path and not Path(path).is_absolute() else Path(path or DEFAULT_STUDY)


def _budget(text: str | None, default: float | None = co.DEFAULT_BUDGET) -> float | None:
    return default if text is None else co.parse_budget(text)


def cmd_rank(args) -> dict:
    data = co.load_study(_study_dir(args.study_dir), verdicts_path=args.verdicts)
    budgets = [co.parse_budget(b) for b in args.budgets]
    rankings = co.rank_all(data, budgets, bootstrap_draws=args.draws)
    out = data.study_dir / "analysis"
    out.mkdir(parents=True, exist_ok=True)
    rep.write_rankings(out / "category_operator_rankings.csv", rankings)
    rep.write_exclusions(out / "category_operator_exclusions.csv", rankings)
    rep.write_case_maxima(out / "category_operator_case_maxima.csv", data, rankings)
    rep.write_settings(out / "category_operator_settings.json", data, budgets, rankings)
    nominees = rep.write_nominees(out / "category_operator_nominees.json", data, rankings, co.DEFAULT_BUDGET)
    figs = rep.write_figures(out / "figures", rankings, co.DEFAULT_BUDGET, data.operators)
    print(f"Study {data.study_id} ({data.evidence_mode}); outputs in {out}")
    for b in budgets:
        print(f"\nBudget {co.budget_label(b)}")
        for cat in data.categories:
            r = rankings[(cat, co.budget_label(b))]
            if not r.rows:
                print(f"  {cat:24} no complete prompts")
                continue
            top = r.rows[0]
            excluded = [e["prompt_id"] for e in r.exclusions]
            interval = ("" if top["paired_gap"] is None else
                        f"  gap {top['paired_gap']:+.4f} [{top['gap_ci_low']:+.4f}, {top['gap_ci_high']:+.4f}] vs "
                        f"{top['contrast'].split(' - ')[1]}")
            print(f"  {cat:24} {'/'.join(r.leaders):24} {top['category_score']:.4f} "
                  f"({top['n_eligible_complete']}/{len(r.complete)}){interval}"
                  + (f"  excluded {excluded}" if excluded else ""))
    print(f"\nLocked nominees (budget {nominees['budget']}): {nominees['nominees']}"
          + (f"; unresolved ties {nominees['unresolved_ties']}" if nominees["unresolved_ties"] else ""))
    print("Figures:", ", ".join(_show(f) for f in figs))
    return {"data": data, "rankings": rankings}


def _recommendation_sources(data: co.StudyData, args, budget: float | None):
    """Category recommendations always come from the locked discovery ranking, never from validation data.

    A recommendation is labelled 'validated' only when this study's held-out claim rule
    (category_validation.json, written by the validate command) confirmed the nominee.
    """
    disc_dir = _study_dir(args.discovery_study_dir)
    discovery = data if data.study_dir == disc_dir.resolve() else co.load_study(disc_dir)
    rankings = co.rank_all(discovery, co.STANDARD_BUDGETS, bootstrap_draws=args.draws)
    validated = None
    decisions = data.study_dir / "analysis" / "category_validation.json"
    if decisions.exists() and data.study_dir != discovery.study_dir and data.evidence_mode != "mock":
        payload = json.loads(decisions.read_text(encoding="utf-8"))
        if payload.get("overlap_checked") and payload.get("budget") == co.budget_label(budget):
            validated = {c: d["nominee"] for c, d in payload["decisions"].items() if d["validated"]}
    return rankings, validated


def _print_selection(sel: co.PromptSelection) -> None:
    print(f"\n{sel.prompt_id} ({sel.category}) | {sel.mode} mode, budget {co.budget_label(sel.budget)}"
          + (f", target {sel.target}" if sel.target is not None else "")
          + f" | scope: {sel.scope_label} | evidence: {sel.evidence_mode}")
    rec = sel.recommendation
    print(f"Category recommendation: {', '.join(rec.get('operators') or ['none'])} [{rec.get('evidence_status')}]")
    print(f"Status: {sel.status}" + (f"  selected: {', '.join(sel.winners)} ({sel.tie_status})" if sel.winners else ""))
    print(sel.explanation)
    print(f"{'operator':24} {'status':28} {'edits':>5} {'d_in':>7} {'raw':>7} {'ctrl':>7} {'excess':>8}")
    for r in sel.operators:
        status = f"benchmark/{r.status}" if r.operator in co.NOISE_OPERATORS else r.status.split(" (")[0]
        f = lambda v: "" if v is None else f"{v:.4f}"
        print(f"{r.operator:24} {status[:28]:28} {'' if r.char_edits is None else r.char_edits:>5} "
              f"{f(r.d_in_char):>7} {f(r.raw):>7} {f(r.control):>7} {'' if r.excess is None else f'{r.excess:+.4f}':>8}")
        if r.status.startswith("incomplete ("):
            print(f"  {r.status}")
    if sel.pareto:
        print("Trade-off frontier (fewest edits -> largest change):", ", ".join(sel.pareto))


def cmd_prompt(args) -> None:
    if args.text:
        return cmd_new_prompt(args)
    data = co.load_study(_study_dir(args.study_dir), verdicts_path=args.verdicts)
    prompt_id = args.prompt_id
    if args.search is not None:
        needle = args.search.casefold().strip()
        matches = [pid for pid in data.prompt_ids if needle in pid.casefold()
                   or needle in (data.prompts[pid]["original_prompt"] or "").casefold()]
        if not matches:
            raise SystemExit(f"No stored prompts match {args.search!r}.")
        for pid in matches:
            info = data.prompts[pid]
            print(f"{pid} [{info['category']}] {' '.join((info['original_prompt'] or '').split())[:110]}")
        if len(matches) == 1:
            prompt_id = matches[0]
        elif sys.stdin.isatty():
            prompt_id = input("Select a prompt ID from the results: ").strip().upper()
            if prompt_id not in matches:
                raise SystemExit("Select one of the displayed prompt IDs.")
        else:
            print("Select a result by running prompt --prompt-id ID.")
            return
    if prompt_id not in data.prompts:
        raise SystemExit(f"No stored prompt {prompt_id!r} in {data.study_id}.")
    cat = data.prompts[prompt_id]["category_identification"]
    print(f"Category source: {cat['source']}. {cat['reason']}")
    budget = _budget(args.budget, default=None if args.target is not None else co.DEFAULT_BUDGET)
    models = co.resolve_model(data.models, args.model)
    rankings, validated = _recommendation_sources(data, args, budget)
    sel = co.select_for_prompt(data, prompt_id, budget=budget, target=args.target, models=models,
                               rankings=rankings, validated=validated)
    ranking = co.rank_category(data, sel.category, budget, bootstrap_draws=args.draws)
    _print_selection(sel)
    default_out = (ROOT / "results" / "category_operator_prompts" / "main_v1"
                   if data.study_dir == DEFAULT_STUDY else data.study_dir / "analysis" / "prompt_reports")
    md, js = rep.write_prompt_report(args.output_dir or default_out, data, sel, ranking=ranking)
    print(f"\nReport: {_show(md)}\nRecord: {_show(js)}")


def cmd_new_prompt(args) -> None:
    """Prepare a pasted prompt for review and a separate measurement run."""
    from run_study import build_candidates

    from apsa.metrics.input_distance.semantic import SemanticDistanceCalculator, SentenceTransformerEmbedder

    identification = suggest_category(args.text)
    proposed = identification["proposed_category"]
    category = args.category or proposed
    if category is None:
        print(identification["reason"])
        choices = ", ".join(co.CATEGORY_LABELS)
        if sys.stdin.isatty():
            category = input(f"Confirm a category ({choices}): ").strip()
        if category not in co.CATEGORY_LABELS:
            raise SystemExit(f"Confirm a category with --category. Choices: {choices}")
    source = ("manual_override" if args.category and proposed and category != proposed
              else "manual" if args.category or proposed is None else "inferred")
    identification.update(category=category, source=source)
    if source == "manual_override":
        identification["reason"] += f" The user chose {category} instead of {proposed}."
    print(f"{category} [{source}] {identification['reason']}")

    data = co.load_study(_study_dir(args.discovery_study_dir))
    budget = _budget(args.budget, default=None if args.target is not None else co.DEFAULT_BUDGET)
    pid = args.prompt_id or "NEW-" + hashlib.sha256(args.text.encode("utf-8")).hexdigest()[:8].upper()
    if not re.fullmatch(r"[A-Za-z0-9_-]+", pid) or pid in data.prompts:
        raise SystemExit("Use a new prompt ID containing only letters, digits, underscores, or hyphens.")
    out = args.output_dir or ROOT / "results" / "category_operator_prompts" / pid
    if (out / "record.json").exists():
        raise SystemExit(f"A preparation already exists at {out}. Use --output-dir for a separate preparation.")
    config = json.loads((data.study_dir / "study_manifest.json").read_text(encoding="utf-8"))["config"]
    seed = config.get("perturbation_seed", 42)
    models = co.resolve_model(data.models, args.model)
    rankings = co.rank_all(data, co.STANDARD_BUDGETS, bootstrap_draws=args.draws)
    rec = co.category_recommendation(category, budget, rankings, measured_prompt=False)
    semantic = SemanticDistanceCalculator(SentenceTransformerEmbedder(model_name=config["semantic_model"]))
    row = {"prompt_id": pid, "task_category": category, "original_prompt": args.text}
    candidates = build_candidates([row], [*data.operators, *data.noise_operators], seed, semantic)
    out.mkdir(parents=True, exist_ok=True)

    table = []
    for candidate in candidates:
        operator = candidate["operator"]
        distances = candidate.get("input_distances", {})
        distance = distances.get("char_levenshtein_normalized")
        edit = candidate.get("perturbed_prompt")
        benchmark = operator in co.NOISE_OPERATORS
        if candidate["status"] != "accepted":
            detail = candidate["reason"]
            status = "generator_error" if detail.startswith("error") else "inapplicable"
        elif budget is not None and distance > budget:
            status, detail = "over_budget", f"d_in_char {distance:.4f} exceeds budget {co.budget_label(budget)}."
        else:
            flags = co.protected_content_changes(args.text, edit)
            status = "screen_flagged" if flags else "uncertain"
            detail = "Automatic screen: " + ", ".join(flags) if flags else "Awaiting a final preservation verdict."
        if benchmark:
            detail += " Noise benchmark only. Preservation unaudited."
        table.append({"operator": operator, "status": status, "detail": detail, "measurement_status": "unmeasured",
                      "role": "noise_benchmark" if benchmark else "candidate",
                      "perturbation_id": candidate.get("perturbation_id"), "perturbed_prompt": edit,
                      "exact_edit": rep.exact_edits(args.text, edit) if edit is not None else [],
                      "char_edits": distances.get("char_levenshtein"), "d_in_char": distance,
                      "d_in_sem": distances.get("semantic_cosine_distance")})

    with (out / "verdicts_template.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["prompt_id", "operator", "perturbation_id", "perturbed_prompt",
                         "reviewer_1", "reviewer_2", "final_verdict", "notes"])
        for candidate in table:
            if candidate["status"] in {"uncertain", "screen_flagged"}:
                writer.writerow([pid, candidate["operator"], candidate["perturbation_id"],
                                 candidate["perturbed_prompt"], "", "", "uncertain", candidate["detail"]])
    with (out / "prompt_row.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["prompt_id", "task_category", "task_description", "original_prompt", "expected_answer",
                         "difficulty_level", "metadata"])
        metric = "explicit_reference_exact_match" if args.reference and category != "code_generation" else "unscored"
        writer.writerow([pid, category, "", args.text, args.reference or "", "",
                         json.dumps({"eval_metric": metric, "category_identification": identification})])

    lines = [f"# New prompt {pid} · {co.CATEGORY_LABELS[category]} (unmeasured)", "",
             f"**Category source:** {source}. {rep.table_cell(identification['reason'])}", "",
             f"**Original prompt:** {rep.table_cell(args.text)}", "",
             f"**Category recommendation:** {', '.join(rec['operators'])} ({rec['evidence_status']})", "",
             rec["rationale"], "", "Output effects are unmeasured.",
             f"**Correctness evaluator** {metric}.", "",
             "| Operator | Status | Char edits | d_in_char | Exact edit and review notes |",
             "|---|---|---:|---:|---|"]
    for candidate in table:
        edits, distance = candidate["char_edits"], candidate["d_in_char"]
        lines.append(f"| {candidate['operator']} | {candidate['status']}, unmeasured | "
                     f"{'' if edits is None else edits} | {'' if distance is None else f'{distance:.4f}'} | "
                     f"{rep.diff_text(candidate['exact_edit'])} {rep.table_cell(candidate['detail'])} |")

    def quote(path: Path | str) -> str:
        return "'" + str(path).replace("'", "''") + "'"

    review = quote((out / "verdicts_template.csv").resolve())
    dataset = quote((out / "prompt_row.csv").resolve())
    run_key = hashlib.sha256(str(out.resolve()).encode("utf-8")).hexdigest()[:8]
    study_id = f"prompt-{pid}-{run_key}"
    study_path = quote(f"results/study/{study_id}")
    budget_arg = f" --max-input-distance {budget}" if budget is not None else ""
    scope_arg = f" --model {quote(models[0])}" if len(models) == 1 else ""
    target_arg = f" --target {args.target}" if args.target is not None else ""
    discovery_arg = f" --discovery-study-dir {quote(data.study_dir)}"
    config_arg = f" --config {quote(data.config_path)}"
    python = r".\.venv\Scripts\python.exe"
    lines += ["", "## Measure after review", "",
              "Have two reviewers inspect the edits in the verdict CSV. Enter final verdicts of "
              "preserved, changed, or uncertain. The first command below explicitly calls the models.",
              "", "```powershell",
              f"{python} experiments/run_study.py --study-id {study_id}{config_arg} --dataset {dataset} --prompt-ids {pid} "
              f"--verdicts {review} --models {' '.join(quote(m) for m in models)}{budget_arg}",
              f"{python} experiments/analyze_study.py --study-dir {study_path} --pairs-only",
              f"{python} experiments/category_operators.py prompt --study-dir {study_path} --prompt-id {pid} "
              f"--verdicts {review} --budget {co.budget_label(budget)}{scope_arg}{target_arg}{discovery_arg}", "```", ""]
    has_reviewable_edit = any(o["role"] == "candidate" and o["status"] in {"uncertain", "screen_flagged"}
                              for o in table)
    status = "unmeasured" if has_reviewable_edit else "no_eligible_edit"
    if not has_reviewable_edit:
        start = lines.index("## Measure after review")
        lines[start:] = ["No candidate for the primary comparison fits the current input edit budget.", ""]
    record = {"prompt_id": pid, "category": category, "category_identification": identification,
              "original_prompt": args.text, "reference_answer": args.reference, "target": args.target,
              "models": models, "budget": co.budget_label(budget), "status": status,
              "recommendation": rec, "candidates": table, "candidate_seed": seed, "planned_study_id": study_id}
    (out / "report.md").write_text("\n".join(lines), encoding="utf-8")
    (out / "record.json").write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"{pid}: recommendation {rec['operators']} [{rec['evidence_status']}], status {status}")
    for candidate in table:
        print(f"  {candidate['operator']:24} {candidate['status']:18} {candidate['detail']}")
    print(f"Outputs: {_show(out)}")


def cmd_all(args) -> None:
    result = cmd_rank(args)
    data, rankings = result["data"], result["rankings"]
    budget = _budget(args.budget)
    out = data.study_dir / "analysis"
    selections = []
    for pid in data.prompt_ids:
        for scope in [None] + data.models:
            models = data.models if scope is None else [scope]
            selections.append(co.select_for_prompt(data, pid, budget=budget, models=models, rankings=rankings))
    rep.write_prompt_maxima(out / "prompt_operator_maxima.csv", data, selections)
    report_dir = out / "prompt_reports"
    for sel in selections:
        if len(sel.models) > 1:
            rep.write_prompt_report(report_dir, data, sel, ranking=rankings.get((sel.category, co.budget_label(budget))))
    example = co.select_for_prompt(data, "LOGIC-010", budget=budget, models=co.resolve_model(data.models, "gpt-oss-120b"),
                                   rankings=rankings) if "LOGIC-010" in data.prompts else None
    if example is not None:
        rep.write_prompt_report(report_dir, data, example,
                                ranking=rankings.get((example.category, co.budget_label(budget))))
    counts: dict[str, int] = {}
    for sel in selections:
        counts[sel.status] = counts.get(sel.status, 0) + 1
    print(f"\nPrompt results at budget {co.budget_label(budget)} (50 prompts x panel + {len(data.models)} models): {counts}")
    print(f"Wrote {_show(out / 'prompt_operator_maxima.csv')} and {_show(report_dir)}")


def cmd_validate(args) -> None:
    data = co.load_study(_study_dir(args.study_dir), verdicts_path=args.verdicts)
    discovery = co.load_study(_study_dir(args.discovery_study_dir))
    locked = json.loads(Path(args.nominees).read_text(encoding="utf-8"))
    budget = co.parse_budget(locked.get("budget", "0.10"))
    if locked.get("unresolved_ties"):
        raise SystemExit(f"Resolve and lock the tied categories first: {locked['unresolved_ties']}")
    result = co.held_out_validation(data, locked["nominees"], budget=budget, margin=args.margin, discovery=discovery)
    out = data.study_dir / "analysis"
    out.mkdir(parents=True, exist_ok=True)
    rep._write_csv(out / "category_validation.csv",
                   ["category", "nominee", "alternative", "n_prompts", "mean_gap", "sd_gap", "lower_bound",
                    "ci_low", "ci_high", "family_size", "margin", "note"], result["contrasts"])
    (out / "category_validation.json").write_text(json.dumps(result, indent=2, default=str), encoding="utf-8")
    print(f"Family of {result['family_size']} one-sided contrasts, alpha {result['alpha']}, margin {result['margin']}")
    for cat, d in result["decisions"].items():
        print(f"  {cat:24} nominee {d['nominee']:20} {d['status']} (n={d['n_complete_prompts']}, "
              f"held-out leader {d['held_out_leader']})")
    print(f"Wrote {out / 'category_validation.csv'}")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--study-dir", default=None, help="Finished study (default results/study/main_v1)")
    common.add_argument("--draws", type=int, default=co.BOOTSTRAP_DRAWS, help="Bootstrap draws (default 10000)")
    common.add_argument("--verdicts", default=None,
                        help="Final preservation verdicts CSV (validation runs); required by 'validate'")
    common.add_argument("--discovery-study-dir", default=str(DEFAULT_STUDY),
                        help="Study whose locked ranking supplies category recommendations")

    p = sub.add_parser("rank", parents=[common], help="Category rankings, exclusions, case maxima, nominees, figures")
    p.add_argument("--budgets", nargs="+", default=["0.01", "0.02", "0.05", "0.10", "none"])
    p.set_defaults(func=cmd_rank)

    p = sub.add_parser("all", parents=[common], help="rank + prompt_operator_maxima.csv + per-prompt reports")
    p.add_argument("--budgets", nargs="+", default=["0.01", "0.02", "0.05", "0.10", "none"])
    p.add_argument("--budget", default=None, help="Budget for the prompt results (default 0.10)")
    p.set_defaults(func=cmd_all)

    p = sub.add_parser("prompt", parents=[common], help="Select and report the operator for one prompt")
    p.add_argument("--prompt-id", help="Stored prompt ID (e.g. LOGIC-010); optional ID for --text")
    p.add_argument("--text", help="A new prompt that is not in the study (unmeasured workflow)")
    p.add_argument("--search", help="Search stored prompts by ID or text (empty string lists all)")
    p.add_argument("--category", choices=co.CATEGORY_LABELS, help="Confirm or override category for --text")
    p.add_argument("--output-dir", type=Path, help="Directory for the prompt report and data")
    p.add_argument("--reference", help="Reference answer for --text")
    p.add_argument("--budget", default=None, help="Max normalised character edit distance; 'none' for no cap")
    p.add_argument("--target", type=float, default=None, help="Minimum control-adjusted change (target mode)")
    p.add_argument("--model", default=None, help="'panel' (default) or one model, e.g. gpt-oss-120b")
    p.set_defaults(func=cmd_prompt)

    p = sub.add_parser("validate", parents=[common], help="Held-out claim rule on a separate validation study")
    p.add_argument("--nominees", required=True, help="Locked nominees JSON written by 'rank'")
    p.add_argument("--margin", type=float, default=0.0)
    p.set_defaults(func=cmd_validate)

    args = parser.parse_args(argv)
    if args.command == "prompt":
        if args.text is not None and not args.text.strip():
            parser.error("--text cannot be blank")
        if not args.prompt_id and args.text is None and args.search is None:
            parser.error("prompt needs --prompt-id, --search, or --text")
        if args.search is not None and (args.text is not None or args.prompt_id):
            parser.error("use --search by itself to find a stored prompt")
        if args.category and args.text is None:
            parser.error("--category applies to --text")
        if args.target is not None and not math.isfinite(args.target):
            parser.error("--target must be finite")
    if args.command == "validate" and not args.verdicts:
        parser.error("validate needs --verdicts (final preservation verdicts for the held-out candidates)")
    args.func(args)


if __name__ == "__main__":
    main()
