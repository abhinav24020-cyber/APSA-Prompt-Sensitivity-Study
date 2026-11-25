"""Prepare and assess blinded APSA research judgments without altering the source study."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from apsa.analysis import category_operator_reports as reports
from apsa.analysis import category_operators as co
from apsa.analysis import research_judging as judging
from apsa.analysis import research_policy as policy
from apsa.analysis import research_statistics as stats

DEFAULT_STUDY = ROOT / "results" / "study" / "main_v1"


def outside_study(out: Path, source: Path) -> None:
    if out.resolve().is_relative_to(source.resolve()):
        raise ValueError("research outputs must be outside the source study directory")


def write_report(data, pid, model, package, out, summary, human, live):
    manifest, _, key = stats.read_package(package)
    budget = manifest["budget"]
    ranking = co.rank_category(data, data.prompts[pid]["category"], budget)
    rankings = {(ranking.category, co.budget_label(budget)): ranking}
    panel = co.select_for_prompt(data, pid, budget=budget, rankings=rankings)
    scope = co.resolve_model(data.models, model)
    selected = panel if scope == data.models else co.select_for_prompt(
        data, pid, budget=budget, rankings=rankings, models=scope)
    record = reports.selection_record(data, selected, ranking=ranking, panel=panel)
    candidates = [row for row in judging.read_jsonl(package / "candidate_evidence.jsonl") if row["prompt_id"] == pid]
    cases = [{"item_id": item_id, **row, "human": human.get(item_id),
              "judges": {name: labels.get(item_id) for name, labels in live.items()}}
             for item_id, row in key.items() if row["prompt_id"] == pid
             and (row["kind"] == "input" or row["model"] in scope)]
    record["research"] = {"overall_status": summary["status"], "candidate_evidence": candidates,
                          "case_evaluations": cases, "rubric": judging.RUBRIC_VERSION}
    lines = [reports.render_markdown(record, selected).rstrip(), "", "## Research rationale and annotations", ""]
    protected, hypothesis = judging.TASKS[selected.category]
    lines += [f"**Protected requirements** {protected}.", "", f"**Hypothesis** {hypothesis}", ""]
    if selected.chosen:
        chosen = selected.chosen
        lines += [f"**Chosen edit** {co.OPERATOR_DESCRIPTIONS.get(chosen.operator, chosen.operator)}.", ""]
    lines += ["Each candidate’s exact character offsets and explanation are in the JSON report.", "",
              "| Item | Kind | Operator or control | Human verdict | LLM judge verdicts |",
              "|---|---|---|---|---|"]
    for row in cases:
        verdicts = ", ".join(f"{name} = {value['verdict']}" for name, value in row["judges"].items() if value)
        lines.append(f"| {row['item_id']} | {row['kind']} | {row['operator']} | "
                     f"{(row['human'] or {}).get('verdict', 'pending')} | {verdicts or 'pending'} |")
    if not cases:
        lines.extend(["", "No annotation items for this prompt are present in this sample."])
    selected_ids = {m.pair_id for r in selected.operators if r.operator in selected.winners for m in r.measurements}
    chosen_cases = [r for r in cases if r.get("pair_id") in selected_ids]
    for item in chosen_cases:
        for name, reviewer in {"Humans": item["human"], **item["judges"]}.items():
            if reviewer:
                rationale = reports.table_cell(reviewer["rationale"])
                lines += ["", f"**{item['item_id']} · {name}** {rationale}"]
    stem = f"{reports.report_stem(selected)}__research"
    judging.write_json(out / f"{stem}.json", record)
    (out / f"{stem}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Research report: {out / (stem + '.md')}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest="command", required=True)
    prep = subs.add_parser("prepare", help="Export blinded items, rubrics, and reviewer templates")
    prep.add_argument("--study-dir", type=Path, default=DEFAULT_STUDY)
    prep.add_argument("--out", type=Path, required=True)
    prep.add_argument("--budget", type=float, default=co.DEFAULT_BUDGET)
    prep.add_argument("--seed", type=int, default=20261125)
    prep.add_argument("--calibration", type=int, default=2, help="Calibration template groups per category")
    prep.add_argument("--evaluation", type=int, default=4, help="Evaluation template groups per category")
    prep.add_argument("--groups", type=Path, help="Reviewed CSV with prompt_id and template_group columns")
    prep.add_argument("--prompt-id", help="Prepare one prompt as a diagnostic, outside the inferential sample")
    prep.add_argument("--swap-fraction", type=float, default=0.20)
    prep.add_argument("--models-per-prompt", type=int, help="Randomly sample this many whole model–prompt blocks")

    judge = subs.add_parser("judge", help="Run a mock or explicitly authorized live judge")
    judge.add_argument("--package", type=Path, required=True)
    judge.add_argument("--out", type=Path, required=True)
    judge.add_argument("--mode", choices=("mock", "live"), required=True)
    judge.add_argument("--provider", choices=("openai", "groq", "gemini"))
    judge.add_argument("--model")
    judge.add_argument("--version", help="Judge revision identifier or 'provider-unreported'")
    judge.add_argument("--max-requests", type=int, help="Required upper bound for live requests")
    judge.add_argument("--kind", choices=("input", "output"))
    judge.add_argument("--split", choices=("calibration", "evaluation", "diagnostic"))
    judge.add_argument("--price-per-million", type=float, nargs=2, metavar=("INPUT_USD", "OUTPUT_USD"))

    assess = subs.add_parser("assess", help="Compare mathematical metrics, human reviews, and live judge labels")
    assess.add_argument("--package", type=Path, required=True)
    assess.add_argument("--out", type=Path, required=True)
    assess.add_argument("--judge-run", type=Path, action="append", default=[])
    assess.add_argument("--prompt-id", help="Also export a detailed Markdown/JSON prompt report")
    assess.add_argument("--model", help="Choose a single model for the prompt report")

    lock = subs.add_parser("lock-policy", help="Freeze category and global operators from discovery data")
    lock.add_argument("--study-dir", type=Path, default=DEFAULT_STUDY)
    lock.add_argument("--groups", type=Path, required=True)
    lock.add_argument("--out", type=Path, required=True, help="New JSON file")
    lock.add_argument("--budget", type=float, default=co.DEFAULT_BUDGET)
    lock.add_argument("--margin", type=float, default=0.0)

    validation = subs.add_parser("evaluate-policy", help="Compare frozen policies on a separate held-out study")
    validation.add_argument("--study-dir", type=Path, required=True)
    validation.add_argument("--groups", type=Path, required=True)
    validation.add_argument("--verdicts", type=Path, required=True)
    validation.add_argument("--lock", type=Path, required=True)
    validation.add_argument("--out", type=Path, required=True, help="New JSON file")

    args = parser.parse_args()
    try:
        if args.command in {"lock-policy", "evaluate-policy"}:
            outside_study(args.out, args.study_dir)
            if args.out.exists():
                raise ValueError("choose a new policy output file")
            data = co.load_study(args.study_dir, verdicts_path=getattr(args, "verdicts", None))
            groups = judging.template_groups(data, args.groups)
            if args.command == "lock-policy":
                if not 0 < args.budget <= 1 or not math.isfinite(args.margin) or args.margin < 0:
                    raise ValueError("use a budget in (0, 1] and a finite nonnegative margin")
                result = policy.lock_policies(data, groups, args.budget, args.margin)
            else:
                lock = json.loads(args.lock.read_text(encoding="utf-8"))
                result = policy.evaluate_policies(data, lock, groups)
            args.out.parent.mkdir(parents=True, exist_ok=True)
            judging.write_json(args.out, result)
            print(f"Policy artifact: {args.out}")
            return
        if args.command == "prepare":
            outside_study(args.out, args.study_dir)
            if not 0 < args.budget <= 1 or not 0 <= args.swap_fraction <= 1:
                raise ValueError("budget must be in (0, 1] and swap fraction in [0, 1]")
            if min(args.calibration, args.evaluation) < 1:
                raise ValueError("calibration and evaluation group counts must be positive")
            manifest = judging.prepare(co.load_study(args.study_dir), args.out, args.budget, args.seed,
                                       args.calibration, args.evaluation, args.groups, args.prompt_id,
                                       args.swap_fraction, args.models_per_prompt)
            print(f"Prepared {sum(row['n'] for row in manifest['coverage'])} blinded items at {args.out}.")
            return

        manifest, _, _ = stats.read_package(args.package)
        outside_study(args.out, Path(manifest["study_dir"]))
        if args.command == "judge":
            generator = None
            if args.max_requests is not None and args.max_requests < 1:
                raise ValueError("max requests must be positive")
            if args.price_per_million and any(not math.isfinite(p) or p < 0 for p in args.price_per_million):
                raise ValueError("prices must be finite and nonnegative")
            if args.mode == "live":
                if not all((args.provider, args.model, args.version, args.max_requests)):
                    raise ValueError("live judging requires provider, model, version, and a positive request limit")
                from apsa.llm_providers.factory import LLMProviderFactory

                generator = LLMProviderFactory.create(args.provider, args.model)
            run = stats.run_judge(args.package, args.out, generator=generator,
                                  provider=args.provider or "mock", model=args.model or "fixture",
                                  version=args.version or "synthetic", mode=args.mode, limit=args.max_requests,
                                  kind=args.kind, split=args.split, price=args.price_per_million)
            print(f"{run['mode']} run: {run['attempted']} requests, status counts {run['by_status']}")
        else:
            if args.out.resolve() == args.package.resolve():
                raise ValueError("use a separate output directory for research results")
            summary, human, live = stats.assess(args.package, args.out, args.judge_run)
            print(f"Research comparison: {args.out / 'summary.json'} ({summary['status']})")
            if args.prompt_id:
                data = co.load_study(manifest["study_dir"])
                if data.source_hashes != manifest["source_hashes"]:
                    raise ValueError("source evidence changed since the annotation package was prepared")
                write_report(data, args.prompt_id, args.model, args.package, args.out, summary, human, live)
    except (ValueError, FileNotFoundError, KeyError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
