"""Discovery-only policy lock and paired evaluation on independent prompts."""

from __future__ import annotations

import hashlib
from statistics import mean

from . import category_operators as co
from . import research_judging as judging
from .study_statistics import cluster_bootstrap_mean


def lock_policies(data, groups, budget, margin):
    if data.evidence_mode == "mock" or not data.models or not data.categories:
        raise ValueError("policy selection requires a non-mock discovery study")
    rankings = [co.rank_category(data, category, budget, bootstrap_draws=1) for category in data.categories]
    if any(not r.rows or len(r.leaders) != 1 for r in rankings):
        raise ValueError("resolve missing or tied discovery nominees before locking policies")
    width = {op: [] for op in data.operators}
    for ranking in rankings:
        for row in ranking.rows:
            width[row["operator"]].append(row["category_score"])
    scores = {op: mean(values) for op, values in width.items() if len(values) == len(rankings)}
    if not scores:
        raise ValueError("no complete discovery score for a global operator")
    leaders = [op for op in scores if scores[op] == max(scores.values())]
    if len(leaders) != 1:
        raise ValueError(f"resolve the global discovery tie before locking: {leaders}")
    return {
        "protocol": "apsa-policy-comparison-v1", "source_hashes": data.source_hashes,
        "study_id": data.study_id, "budget": budget, "margin": margin, "models": data.models,
        "category_policies": {ranking.category: ranking.leaders[0] for ranking in rankings},
        "global_policy": leaders[0], "global_scores": scores,
        "discovery_groups": sorted(set(groups.values())),
        "discovery_prompt_hashes": {
            pid: hashlib.sha256(co._norm_text(values["original_prompt"]).encode()).hexdigest()
            for pid, values in data.prompts.items()},
    }


def evaluate_policies(data, lock, groups):
    if lock.get("protocol") != "apsa-policy-comparison-v1":
        raise ValueError("unsupported policy lock")
    if data.verdicts is None or data.evidence_mode == "mock":
        raise ValueError("held-out comparison requires preservation verdicts and a non-mock study")
    normalized = {hashlib.sha256(co._norm_text(values["original_prompt"]).encode()).hexdigest()
                  for values in data.prompts.values()}
    if (data.study_id == lock["study_id"] or set(data.prompt_ids) & lock["discovery_prompt_hashes"].keys()
            or normalized & set(lock["discovery_prompt_hashes"].values())
            or set(groups.values()) & set(lock["discovery_groups"])):
        raise ValueError("validation overlaps discovery in study, prompt ID, prompt text, or template group")
    if set(data.models) != set(lock["models"]) or set(data.categories) != set(lock["category_policies"]):
        raise ValueError("the held-out study must cover the locked model panel and all locked categories")
    policies = set(lock["category_policies"].values()) | {lock["global_policy"]}
    if not policies <= set(data.operators):
        raise ValueError("the held-out study did not schedule the locked operators")

    comparisons = []
    for pid in data.prompt_ids:
        category = data.prompts[pid]["category"]
        local, global_op = lock["category_policies"][category], lock["global_policy"]
        entry = {"prompt_id": pid, "category": category, "template_group": groups[pid],
                 "category_operator": local, "global_operator": global_op, "exclusions": []}
        controls = {m: data.control_state(pid, m) for m in lock["models"]}
        for model, (values, reason) in controls.items():
            if values is None:
                entry["exclusions"].append(f"{model}: {reason}")
        for label, operator in (("category", local), ("global", global_op)):
            status, detail = data.eligibility(pid, operator, lock["budget"])
            entry[f"{label}_eligibility"] = status
            entry[f"{label}_eligibility_detail"] = detail
            if status in {"generator_error", "not_generated"}:
                entry["exclusions"].append(f"{operator}: {detail}")
            elif status == co.ELIGIBLE:
                results = [co.measure(data, pid, m, operator) for m in lock["models"]]
                entry["exclusions"].extend(f"{operator}/{m.model}: {m.status}" for m in results
                                           if m.status != co.MEASURED)
                if all(m.status == co.MEASURED for m in results):
                    entry[f"{label}_score"] = mean(m.excess for m in results)
            else:
                entry[f"{label}_score"] = 0.0  # Prespecified unchanged-prompt fallback.
        entry["paired_gap"] = None if entry["exclusions"] else entry["category_score"] - entry["global_score"]
        comparisons.append(entry)

    def summarize(rows):
        usable = [row for row in rows if row["paired_gap"] is not None]
        return {**cluster_bootstrap_mean([row["paired_gap"] for row in usable],
                                        [row["template_group"] for row in usable]),
                "n_total_prompts": len(rows),
                "category_eligible_n": sum(row["category_eligibility"] == co.ELIGIBLE for row in usable),
                "global_eligible_n": sum(row["global_eligibility"] == co.ELIGIBLE for row in usable)}

    overall = summarize(comparisons)
    categories = {category: summarize([r for r in comparisons if r["category"] == category])
                  for category in data.categories}
    return {"study_id": data.study_id, "source_hashes": data.source_hashes, "lock": lock, "overall": overall,
            "by_category": categories, "comparisons": comparisons, "margin": lock["margin"],
            "status": ("held-out advantage" if overall["ci_low"] is not None
                       and overall["ci_low"] > lock["margin"] and all(v["n"] for v in categories.values())
                       else "unresolved")}
