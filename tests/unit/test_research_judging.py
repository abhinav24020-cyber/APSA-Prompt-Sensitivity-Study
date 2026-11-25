"""Offline verification of blinding, judge evaluation, and the policy claim rule."""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from apsa.analysis import category_operators as co
from apsa.analysis import research_judging as rj
from apsa.analysis import research_policy as policy
from apsa.analysis import research_statistics as stats


@pytest.fixture(scope="module")
def discovery():
    return co.load_study(ROOT / "results/study/main_v1")


def test_split_keeps_reviewed_template_groups_together(discovery, tmp_path):
    groups = {pid: pid for pid in discovery.prompt_ids}
    groups["LOGIC-002"] = groups["LOGIC-001"]
    first = rj.split_groups(discovery, groups, 2, 4, 23, None)
    assert first.get("LOGIC-001") == first.get("LOGIC-002")
    assert first == rj.split_groups(discovery, groups, 2, 4, 23, None)
    package = tmp_path / "balanced"
    manifest = rj.prepare(discovery, package, 0.10, 23, 2, 4, None, None, 0.20)
    assert {row["category"] for row in manifest["coverage"] if row["split"] == "evaluation"} == set(discovery.categories)
    assert any(key.startswith("evaluation/control") for key in manifest["output_sample_strata"])


def test_blinded_diagnostic_and_mock_pipeline(discovery, tmp_path):
    package, run, out = [tmp_path / name for name in ("package", "run", "out")]
    rj.prepare(discovery, package, 0.10, 11, 1, 1, None, "LOGIC-010", 1)
    _, items, key = stats.read_package(package)
    assert len(items) == 64
    assert all(set(item) == {"item_id", "kind", "task", "a", "b"} for item in items.values())
    output = next(i for i, row in key.items() if row["kind"] == "output")
    assert set(rj.judge_payload(items[output])) == {"task_requirements", "A", "B"}
    assert rj.judge_payload(items[output], True)["A"] == items[output]["b"]
    assert {item["condition"] for item in key.values() if item["kind"] == "output"} == {"control", "treatment"}
    mock = stats.run_judge(package, run, generator=None, provider="mock", model="fixture", version="v1",
                           mode="mock", limit=None)
    assert mock["by_status"] == {"ok": len(items) * 2}
    summary, human, live = stats.assess(package, out, (run,))
    assert summary["status"] == "pending" and human == live == {}
    assert summary["paired_substantive_rate_difference"]["human"]["mean"] is None
    assert summary["judge_runs"][0]["order_audit"]["n"] == len(items)
    ledger = rj.read_jsonl(package / "candidate_evidence.jsonl")
    assert len(ledger) == 500
    assert sum(c["role"] == "benchmark" for c in ledger) == 50
    case = next(c for c in ledger if c["prompt_id"] == "LOGIC-010" and c["operator"] == "punctuation")
    assert case["edits"] == [{"original_offset": 73, "edited_offset": 73, "removed": ".", "added": ""}]


def test_logical_verdict_requires_valid_flags_and_verbatim_quotes():
    payload = {"A": "Final answer: True", "B": "Final answer: False"}
    result = {**dict.fromkeys(rj.FIELDS), "verdict": "substantive",
              "rationale": "The Boolean answer changes.",
              "evidence": [{"side": "A", "excerpt": "True"}, {"side": "B", "excerpt": "False"}],
              "final_answer_or_claim_changed": True}
    assert stats.predict("output", rj.validate_verdict("output", payload, result)) == 1
    with pytest.raises(ValueError, match="conflicts"):
        rj.validate_verdict("output", payload, {**result, "verdict": "equivalent"})
    with pytest.raises(ValueError, match="verbatim"):
        rj.validate_verdict("output", payload, {**result, "evidence": [{"side": "B", "excerpt": "True"}]})


def test_independent_reviews_require_agreement_or_adjudication(discovery, tmp_path):
    import csv

    package = tmp_path / "package"
    rj.prepare(discovery, package, 0.10, 11, 1, 1, None, "LOGIC-010", 0)
    _, items, key = stats.read_package(package)
    item_id = next(i for i, row in key.items() if row["kind"] == "input" and row["operator"] == "punctuation")
    item = items[item_id]
    for name, verdict in (("reviewer_1", "preserved"), ("reviewer_2", "changed"), ("adjudicator", "preserved")):
        path = package / f"{name}.csv"
        with path.open(encoding="utf-8", newline="") as stream:
            fields = csv.DictReader(stream).fieldnames
        rj.write_csv(path, fields, [{"item_id": item_id, "verdict": verdict, "rationale": "Test fixture verdict.",
                                     "evidence_a": item["a"], "evidence_b": item["b"]}])
    one, two, three = [stats.read_reviews(package / f"{name}.csv", items)
                       for name in ("reviewer_1", "reviewer_2", "adjudicator")]
    assert stats.adjudicate(items, [one, two, {}]) == {}
    assert stats.adjudicate(items, [one, two, three])[item_id]["verdict"] == "preserved"
    out = tmp_path / "assessment"
    stats.assess(package, out)
    with (out / "preservation_verdicts.csv").open(encoding="utf-8", newline="") as stream:
        exported = next(csv.DictReader(stream))
    assert exported["perturbed_prompt"] == discovery.candidates["LOGIC-010", "punctuation"]["perturbed_prompt"]
    assert exported["reviewer_2"] == "changed" and exported["final_verdict"] == "preserved"


def test_calibration_and_matched_substantive_rates_exclude_missing_controls():
    assert stats.fit_threshold([(0.05, 0), (0.3, 1), (0.6, 1)]) == 0.3
    assert stats.fit_threshold([(0.05, 0)]) is None
    key = {"candidate": {"kind": "input", "candidate_id": "p1"}}
    marks = {"candidate": {"verdict": "preserved"}}
    for pid in ("P1", "P2"):
        for i, (condition, verdict) in enumerate((
            ("treatment", "substantive"), ("control", "equivalent"),
            ("control", "equivalent" if pid == "P1" else "uncertain"),
        )):
            case = f"{pid}/{i}"
            key[case] = {"kind": "output", "split": "evaluation", "category": "logical_reasoning",
                         "model": "model-a", "group": pid, "prompt_id": pid, "d_in_char": 0.02,
                         "condition": condition, "candidate_id": "p1", "operator": "punctuation", "repeat": i}
            marks[case] = {"verdict": verdict}
    report = stats.matched_outcome(key, marks, marks, {"control_repetitions": 2, "budget": 0.10})
    assert report["mean"] == 1 and report["treatment_n"] == 1 and report["control_n"] == 2
    assert report["candidate_blocks"] == 2 and report["n"] == 1


def test_policies_lock_on_discovery_and_reject_overlapping_prompts(discovery):
    from dataclasses import replace

    groups = {pid: f"group-{pid}" for pid in discovery.prompt_ids}
    lock = policy.lock_policies(discovery, groups, 0.10, 0)
    assert lock["global_policy"] in discovery.operators
    assert lock["category_policies"]["logical_reasoning"] == "punctuation"
    with pytest.raises(ValueError, match="overlaps"):
        policy.evaluate_policies(replace(discovery, study_id="another", verdicts={}), lock, groups)


def test_independent_policy_comparison_uses_matched_effects(tmp_path):
    import hashlib

    ids = ["A", "B"]
    model, category = "model-a", "logical_reasoning"
    groups = {pid: f"new-group-{pid}" for pid in ids}
    verdicts = {(pid, operator): "preserved" for pid in ids for operator in ("punctuation", "capitalization")}
    candidates = {(pid, operator): {"status": "accepted", "input_distances": {"char_levenshtein_normalized": 0.02}}
                  for pid, operator in verdicts}
    treatments = {(pid, model, operator): {"d_out_sem": raw}
                  for pid in ids for operator, raw in (("punctuation", 0.4), ("capitalization", 0.2))}
    controls = {(pid, model): {1: {"d_out_sem": 0.01}, 2: {"d_out_sem": 0.03}} for pid in ids}
    data = co.StudyData(tmp_path, "heldout", "", [model], ["punctuation", "capitalization"], 2, ids,
                        {pid: {"category": category, "original_prompt": f"fresh task {pid}"} for pid in ids},
                        candidates, treatments, controls, {}, verdicts=verdicts)
    lock = {"protocol": "apsa-policy-comparison-v1", "study_id": "discovery", "budget": 0.10, "margin": 0.05,
            "models": [model], "category_policies": {category: "punctuation"}, "global_policy": "capitalization",
            "discovery_prompt_hashes": {"X": hashlib.sha256(b"different").hexdigest()}, "discovery_groups": ["old"]}
    result = policy.evaluate_policies(data, lock, groups)
    assert result["overall"]["mean"] == pytest.approx(0.2)
    assert result["status"] == "held-out advantage"
