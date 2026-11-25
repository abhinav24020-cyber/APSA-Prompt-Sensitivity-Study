"""Analysis and reporting for blinded APSA judgments."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from statistics import mean

from . import research_judging as rj
from .study_statistics import cluster_bootstrap_mean


def read_package(package):
    manifest = json.loads((package / "manifest.json").read_text(encoding="utf-8"))
    if manifest["rubric"] != rj.RUBRIC_VERSION:
        raise ValueError("unsupported research rubric version")
    items = {row["item_id"]: row for row in rj.read_jsonl(package / "blinded_items.jsonl")}
    key = json.loads((package / "private_key.json").read_text(encoding="utf-8"))
    if items.keys() != key.keys():
        raise ValueError("blinded items and private key differ")
    return manifest, items, key


def predict(kind, verdict):
    if verdict is None or verdict["verdict"] == "uncertain":
        return None
    return int(verdict["verdict"] == rj.LABELS[kind][1])


def read_reviews(path, items):
    judgments = {}
    seen = set()
    with path.open(encoding="utf-8-sig", newline="") as stream:
        for row in csv.DictReader(stream):
            item_id = row["item_id"]
            if item_id not in items or item_id in seen:
                raise ValueError(f"{path}: unknown or duplicate item {item_id}")
            seen.add(item_id)
            if not row["verdict"].strip():
                continue
            item = items[item_id]
            raw = {"verdict": row["verdict"].strip().lower(), "rationale": row["rationale"],
                   "evidence": [{"side": side, "excerpt": row[f"evidence_{side.lower()}"]}
                                for side in ("A", "B") if row[f"evidence_{side.lower()}"]]}
            if item["kind"] == "output":
                for field in rj.FIELDS:
                    value = row[field].strip().lower()
                    if value not in {"true", "false", ""}:
                        raise ValueError(f"{path}: {item_id}/{field} must be true, false, or blank")
                    raw[field] = None if not value else value == "true"
            try:
                judgments[item_id] = rj.validate_verdict(item["kind"], rj.judge_payload(item), raw)
            except ValueError as error:
                raise ValueError(f"{path}: {item_id}: {error}") from error
    return judgments


def adjudicate(items, reviews):
    first, second, adjudicator = reviews
    final = {}
    for item_id, item in items.items():
        if item_id not in first or item_id not in second:
            continue
        a, b = first[item_id], second[item_id]
        fields = ("verdict", *rj.FIELDS) if item["kind"] == "output" else ("verdict",)
        if item_id in adjudicator:
            final[item_id] = adjudicator[item_id]
        elif all(a[k] == b[k] for k in fields):
            final[item_id] = a
    return final


def agreement(pairs, labels):
    counts = Counter(pairs)
    n = len(pairs)
    row = {a: sum(counts[a, b] for b in labels) for a in labels}
    col = {b: sum(counts[a, b] for a in labels) for b in labels}
    agree = sum(counts[label, label] for label in labels) / n if n else None
    expected = sum(row[label] * col[label] for label in labels) / n**2 if n else None
    return {"n": n, "agreement": agree, "cohens_kappa": (agree - expected) / (1 - expected)
            if expected is not None and expected < 1 else None,
            "confusion": {a: {b: counts[a, b] for b in labels} for a in labels},
            "classes": {label: {"precision": counts[label, label] / col[label] if col[label] else None,
                                "recall": counts[label, label] / row[label] if row[label] else None}
                        for label in labels}}


def fit_threshold(points):
    """Select a >= cutoff by calibration-only balanced accuracy; prefer the largest tied cutoff."""
    points = [(x, y) for x, y in points if x is not None and y is not None]
    counts = Counter(y for _, y in points)
    if set(counts) != {0, 1}:
        return None
    candidates = sorted({x for x, _ in points} | {max(x for x, _ in points) + 1e-9})
    return max(candidates, key=lambda t: (
        sum(int(x >= t) == y for x, y in points if y == 0) / counts[0]
        + sum(int(x >= t) == y for x, y in points if y == 1) / counts[1], t))


def run_judge(package, out, *, generator, provider, model, version, mode, limit, kind=None,
              split=None, price=None):
    manifest, items, key = read_package(package)
    if mode == "live" and (generator is None or not limit or manifest["study_evidence_mode"] == "mock"):
        raise ValueError("live judging requires a positive request limit and a non-mock source study")
    if out.exists() and any(out.iterdir()):
        raise ValueError("use an empty directory for the judge run")
    out.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256((package / "blinded_items.jsonl").read_bytes()).hexdigest()
    settings = {"temperature": 0.0, "max_tokens": 768}
    plan = [(item_id, reverse) for item_id, item in items.items()
            if (kind is None or item["kind"] == kind) and (split is None or key[item_id]["split"] == split)
            for reverse in ([False, True] if key[item_id].get("order_audit") else [False])]
    with (out / "judgments.jsonl").open("x", encoding="utf-8") as handle:
        for item_id, reverse in plan[:limit]:
            item = items[item_id]
            payload = rj.judge_payload(item, reverse)
            identity = {"item_id": item_id, "kind": item["kind"], "reversed": reverse,
                        "display_order": "B,A" if reverse else "A,B"}
            result = {}
            if mode == "mock":
                raw = {"verdict": "uncertain", "rationale": "Synthetic result for offline workflow verification.",
                       "evidence": [], **({f: None for f in rj.FIELDS} if item["kind"] == "output" else {})}
            else:
                prompt = rj.judge_instruction(item["kind"]) + "\n\nEvaluation data:\n" + json.dumps(
                    payload, ensure_ascii=False)
                try:
                    response = generator.generate(prompt, settings.copy())
                except Exception as error:
                    result = {"status": "request_failed", "error": type(error).__name__}
                else:
                    result = {"provider_model_id": response.model_name, "request_id": response.run_id,
                              "input_tokens": response.input_tokens, "output_tokens": response.output_tokens,
                              "finish_reason": response.finish_reason, "latency": response.latency,
                              "estimated_cost": (response.input_tokens * price[0] + response.output_tokens * price[1])
                              / 1_000_000 if price and response.input_tokens is not None
                              and response.output_tokens is not None else None}
                    try:
                        raw = json.loads(response.output)
                    except (TypeError, ValueError):
                        result.update(status="invalid", error="response is not a single JSON object")
            if "status" not in result:
                try:
                    result.update(status="ok", judgment=rj.validate_verdict(item["kind"], payload, raw))
                except ValueError as error:
                    result.update(status="invalid", error=str(error))
            handle.write(json.dumps({**identity, **result}, ensure_ascii=False, allow_nan=False) + "\n")
            handle.flush()
    rows = rj.read_jsonl(out / "judgments.jsonl")
    stats = Counter(row["status"] for row in rows)
    total_cost = [row.get("estimated_cost") for row in rows if row.get("estimated_cost") is not None]
    run = {"provider": provider, "model": model, "version": version, "mode": mode,
           "rubric": rj.RUBRIC_VERSION, "blinded_items_sha256": digest, "settings": settings,
           "price_usd_per_million_input_output": price, "estimated_cost_usd": sum(total_cost) if total_cost else None,
           "n_cost_estimates": len(total_cost), "planned": len(plan), "attempted": len(rows),
           "not_attempted": len(plan) - len(rows), "by_status": dict(stats)}
    rj.write_json(out / "run.json", run)
    return run


def load_judge_runs(package, runs, items):
    digest = hashlib.sha256((package / "blinded_items.jsonl").read_bytes()).hexdigest()
    live, profiles = {}, []
    for folder in runs:
        run = json.loads((folder / "run.json").read_text(encoding="utf-8"))
        if run["blinded_items_sha256"] != digest or run["rubric"] != rj.RUBRIC_VERSION:
            raise ValueError(f"judge run does not match blinded package: {folder}")
        labels, swapped_labels = {}, {}
        for row in rj.read_jsonl(folder / "judgments.jsonl"):
            if row["status"] != "ok":
                continue
            item_id = row["item_id"]
            item = items[item_id]
            destination = swapped_labels if row["reversed"] else labels
            if item_id in destination:
                raise ValueError(f"duplicate judge result for {item_id}")
            destination[item_id] = rj.validate_verdict(
                item["kind"], rj.judge_payload(item, row["reversed"]), row["judgment"])
        ordered = [(labels[i]["verdict"], v["verdict"]) for i, v in swapped_labels.items() if i in labels]
        run["order_audit"] = {"n": len(ordered), "verdict_disagreements": sum(a != b for a, b in ordered)}
        profiles.append(run)
        if run["mode"] == "live":
            name = f"{run['provider']}:{run['model']}@{run['version']}"
            if name in live:
                raise ValueError(f"supply one frozen run per judge: {name}")
            live[name] = labels
    return live, profiles


def matched_outcome(key, human, labels, manifest, category=None, operator=None, model=None, dimension=None):
    """Compare judge or human rates using the same eligible model–prompt blocks."""
    preserved = {key[i]["candidate_id"] for i, v in human.items()
                 if key[i]["kind"] == "input" and v["verdict"] == "preserved"}
    blocks = defaultdict(lambda: {"control": {}, "treatment": {}})
    for i, row in key.items():
        if (row["kind"] != "output" or row["split"] != "evaluation"
                or category is not None and row["category"] != category
                or model is not None and row["model"] != model):
            continue
        is_control = row["condition"] == "control"
        if not is_control and (row["candidate_id"] not in preserved or row["operator"] == "random_edit"
                               or not 0 < row["d_in_char"] <= manifest["budget"]
                               or operator is not None and row["operator"] != operator):
            continue
        verdict = labels.get(i)
        value = predict("output", verdict) if dimension is None else (verdict or {}).get(dimension)
        block_key = (row["group"], row["prompt_id"], row["model"])
        if value is not None:
            blocks[block_key][row["condition"]][row["repeat"] if is_control else i] = value
        else:
            blocks[block_key]
    values, groups, treatments, controls = [], [], [], []
    for (group, _, _), block in blocks.items():
        a, b = list(block["treatment"].values()), list(block["control"].values())
        if a and len(b) == manifest["control_repetitions"]:
            values.append(mean(a) - mean(b))
            groups.append(group)
            treatments.extend(a)
            controls.extend(b)
    return {**cluster_bootstrap_mean(values, groups), "candidate_blocks": len(blocks),
            "treatment_n": len(treatments), "control_n": len(controls),
            "treatment_rate": mean(treatments) if treatments else None,
            "control_rate": mean(controls) if controls else None}


def assess(package, out, runs=()):
    manifest, items, key = read_package(package)
    out.mkdir(parents=True, exist_ok=True)
    reviews = [read_reviews(package / f"{name}.csv", items)
               for name in ("reviewer_1", "reviewer_2", "adjudicator")]
    human = adjudicate(items, reviews)
    live, profiles = load_judge_runs(package, runs, items)
    input_reviews = []
    for item_id, verdict in human.items():
        info = key[item_id]
        if info["kind"] == "input":
            item = items[item_id]
            input_reviews.append({
                "prompt_id": info["prompt_id"], "operator": info["operator"],
                "perturbation_id": info["candidate_id"], "perturbed_prompt": item["a" if info["swapped"] else "b"],
                "reviewer_1": reviews[0][item_id]["verdict"], "reviewer_2": reviews[1][item_id]["verdict"],
                "final_verdict": verdict["verdict"], "notes": verdict["rationale"],
            })
    rj.write_csv(out / "preservation_verdicts.csv",
                 ["prompt_id", "operator", "perturbation_id", "perturbed_prompt", "reviewer_1", "reviewer_2",
                  "final_verdict", "notes"], input_reviews)
    scores = {"input": ("d_in_char", "d_in_sem"), "output": ("d_out_sem", "d_out_char", "d_out_token")}
    thresholds, metrics = {}, []
    for kind, columns in scores.items():
        split_ids = {split: [i for i, row in key.items() if row["kind"] == kind and row["split"] == split]
                     for split in ("calibration", "evaluation")}
        thresholds[kind] = {column: fit_threshold([(key[i][column], predict(kind, human.get(i)))
                                                     for i in split_ids["calibration"]]) for column in columns}
        predictors = {name: {i: predict(kind, labels.get(i)) for i in split_ids["evaluation"]}
                      for name, labels in live.items()}
        for column, threshold in thresholds[kind].items():
            predictors[column] = {i: int(key[i][column] >= threshold)
                                  if threshold is not None and key[i][column] is not None else None
                                  for i in split_ids["evaluation"]}
        human_ids = [i for i in split_ids["evaluation"] if predict(kind, human.get(i)) is not None]
        common = [i for i in human_ids if all(values[i] is not None for values in predictors.values())]
        for name, predictions in predictors.items():
            covered = [i for i in human_ids if predictions[i] is not None]
            for scope, ids in (("method_scorable", covered), ("common_scorable", common)):
                pairs = [(predict(kind, human[i]), predictions[i]) for i in ids]
                stats = agreement(pairs, (0, 1))
                ci = cluster_bootstrap_mean([a == b for a, b in pairs], [key[i]["group"] for i in ids])
                metrics.append({"kind": kind, "method": name, "scope": scope, "evaluation_n": len(split_ids["evaluation"]),
                                "human_scorable_n": len(human_ids), "method_missing_n": len(human_ids) - len(covered),
                                "agreement_ci_low": ci["ci_low"], "agreement_ci_high": ci["ci_high"], **stats})
    comparison, disagreements = [], []
    for i, row in key.items():
        direct = {name: values.get(i, {}).get("verdict") for name, values in live.items()}
        threshold_predictions = {k: (int(row[k] >= t) if t is not None and row[k] is not None else None)
                                 for k, t in thresholds[row["kind"]].items()}
        gold = predict(row["kind"], human.get(i))
        auto = {**threshold_predictions, **{name: predict(row["kind"], values.get(i)) for name, values in live.items()}}
        mismatches = [name for name, value in auto.items() if gold is not None and value is not None and value != gold]
        entry = {"item_id": i, **row, "human": human.get(i, {}).get("verdict"), "judge_labels": direct,
                 "math_predictions": threshold_predictions, "disagrees": mismatches}
        comparison.append(entry)
        if mismatches and row["split"] == "evaluation":
            disagreements.append({**entry, "human_evidence": human.get(i),
                                  "judge_evidence": {name: values.get(i) for name, values in live.items()}})

    comparisons_path = out / "comparison_table.csv"
    names = sorted({key for row in comparison for key in row})
    rj.write_csv(comparisons_path, names, [{k: json.dumps(v) if isinstance(v, (dict, list)) else v
                                           for k, v in row.items()} for row in comparison])
    metric_columns = ["kind", "method", "scope", "evaluation_n", "human_scorable_n", "method_missing_n", "n",
                      "agreement", "agreement_ci_low", "agreement_ci_high", "cohens_kappa", "classes", "confusion"]
    rj.write_csv(out / "method_comparison.csv", metric_columns,
                 [{k: json.dumps(row[k]) if k in {"classes", "confusion"} else row[k] for k in metric_columns}
                  for row in metrics])
    rj.write_json(out / "disagreements.json", disagreements)
    observed = [row for row in comparison if row["kind"] == "output" and row["condition"] == "treatment"]
    examples = {
        "large_distance_same_normalized_answer": sorted(
            (row for row in observed if row["answer_changed"] is False and row["d_out_sem"] >= 0.5),
            key=lambda row: -row["d_out_sem"])[:5],
        "small_distance_changed_normalized_answer": sorted(
            (row for row in observed if row["answer_changed"] is True and row["d_out_sem"] <= 0.05),
            key=lambda row: row["d_out_sem"])[:5],
    }
    rj.write_json(out / "observed_metric_examples.json", examples)
    reviewer_agreement = {kind: agreement([(reviews[0][i]["verdict"], reviews[1][i]["verdict"])
                                          for i, row in key.items() if row["kind"] == kind
                                          and row["split"] == "evaluation" and all(i in v for v in reviews[:2])],
                                         vocab) for kind, vocab in rj.LABELS.items()}
    joint_runs = {}
    names = list(live)
    for index, name in enumerate(names):
        primary = live[name]
        for other_name in names[index + 1:]:
            second = live[other_name]
            by_kind = {}
            for kind, choices in rj.LABELS.items():
                pairs = [(primary[i]["verdict"], second[i]["verdict"]) for i in primary.keys() & second.keys()
                         if key[i]["kind"] == kind and key[i]["split"] == "evaluation"]
                by_kind[kind] = agreement(pairs, choices)
            joint_runs[f"{name} vs {other_name}"] = by_kind

    evaluators = {"human": human, **live}
    matched = {name: matched_outcome(key, human, labels, manifest) for name, labels in evaluators.items()}
    dimensions = {name: {field: matched_outcome(key, human, labels, manifest, dimension=field)
                         for field in rj.FIELDS} for name, labels in evaluators.items()}
    breakdown = [{"method": name, "operator": op, "category": category, "model": model,
                  **matched_outcome(key, human, labels, manifest, category, op, model)}
                 for name, labels in evaluators.items() for op in [None, *sorted(
                     {row["operator"] for row in key.values() if row.get("role") == "candidate"})]
                 for category, model in [(c, None) for c in sorted({row["category"] for row in key.values()})]
                 + [(None, m) for m in manifest["models"]]]
    preservation = []
    for method, labels in evaluators.items():
        groups = defaultdict(list)
        for i, row in key.items():
            if row["kind"] == "input" and row["split"] == "evaluation" and 0 < row["d_in_char"] <= manifest["budget"]:
                groups[(row["category"], row["operator"])].append(labels.get(i, {}).get("verdict"))
        for (category, operator), values in sorted(groups.items()):
            counts = Counter(value or "missing" for value in values)
            resolved = counts["preserved"] + counts["changed"]
            preservation.append({"method": method, "category": category, "operator": operator,
                                 "n_candidates": len(values), "verdicts": dict(counts),
                                 "preserved_rate": counts["preserved"] / resolved if resolved else None})
    candidate_counts = Counter((row["category"], row["operator"], row["eligibility"])
                               for row in rj.read_jsonl(package / "candidate_evidence.jsonl"))
    summary = {"status": "exploratory" if live or human else "pending",
               "judge_runs": profiles, "human_review_counts": [len(reviewer) for reviewer in reviews],
               "adjudicated_n": len(human), "reviewer_agreement": reviewer_agreement,
               "judge_disagreements": joint_runs, "thresholds_from_calibration": thresholds,
               "comparison_metrics": metrics, "preservation_by_operator": preservation,
               "candidate_coverage": [{"category": cat, "operator": op, "state": state, "n": n}
                                      for (cat, op, state), n in sorted(candidate_counts.items())],
               "paired_substantive_rate_difference": matched, "paired_dimension_rate_differences": dimensions,
               "paired_breakdown": breakdown,
               "evaluation_disagreements": len(disagreements), "held_out_policy_claim": "pending",
               "template_groups_reviewed": manifest["template_groups_reviewed"]}
    rj.write_json(out / "summary.json", summary)
    return summary, human, live
