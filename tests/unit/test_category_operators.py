"""Tests for the category-based operator selection workflow.

Synthetic fixtures cover the edge cases named in the implementation plan (Section 5, "Check
before a live run"); the main_v1 tests reproduce the plan's Section 2 and Section 7 numbers.
"""

from __future__ import annotations

import csv
import json
import math
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))

from apsa.analysis import category_operators as co  # noqa: E402

PAIR_COLUMNS = [
    "pair_id", "anchor_record_id", "comparison_record_id", "model", "provider", "prompt_id", "task_category",
    "condition", "operator", "family", "repetition", "perturbation_id", "anchor_output", "comparison_output",
    "anchor_correct", "comparison_correct", "anchor_final", "comparison_final", "any_truncated", "any_empty",
    "scoring_method", "code_name_fallback", "perturbed_prompt", "d_out_char", "d_out_token", "identical_output",
    "d_out_sem", "answer_changed", "scorable", "flip_c2i", "flip_i2c", "taxonomy", "audit_meaning_altering",
    "audit_kind",
]
MODELS = ["model-a", "model-b"]


def build_study(tmp_path: Path, *, prompts, candidates, controls, treatments, flagged=(), operators=None,
                reps=2, extra_rows=()):
    """Write a minimal finished study.

    prompts:    [(prompt_id, category, text)]
    candidates: {(pid, op): (char_edits, d_in_char)} for accepted; {(pid, op): None} for rejected
    controls:   {(pid, model): [d_out_sem per repetition, or dict overrides]}
    treatments: {(pid, model, op): d_out_sem or dict overrides}
    """
    study = tmp_path / "study"
    (study / "processed").mkdir(parents=True)
    operators = operators or sorted({op for _, op in candidates})
    dataset = tmp_path / "dataset.csv"
    with dataset.open("w", encoding="utf-8", newline="") as handle:
        w = csv.writer(handle)
        w.writerow(["prompt_id", "task_category", "task_description", "original_prompt", "expected_answer",
                    "difficulty_level", "metadata"])
        for pid, cat, text in prompts:
            w.writerow([pid, cat, "", text, "ref", "", json.dumps({"eval_metric": "exact_match"})])
    manifest = {"study_id": "fixture", "config_path": "config/experiments/fixture.yaml",
                "dataset_path": str(dataset), "selected_prompt_ids": [p for p, _, _ in prompts],
                "config": {"models": [{"name": m} for m in MODELS], "operators": operators + ["random_edit"],
                           "control_repetitions": reps}}
    (study / "study_manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    texts = {p: t for p, _, t in prompts}
    cats = {p: c for p, c, _ in prompts}
    with (study / "candidates.jsonl").open("w", encoding="utf-8") as handle:
        for (pid, op), spec in candidates.items():
            base = {"prompt_id": pid, "task_category": cats[pid], "operator": op, "seed": 42}
            if spec is None:
                handle.write(json.dumps({**base, "status": "rejected", "reason": "inapplicable_or_no_op"}) + "\n")
                continue
            edits, d_in = spec
            handle.write(json.dumps({**base, "status": "accepted", "reason": None,
                                     "perturbation_id": f"{pid}__{op}__42", "perturbed_prompt": f"{texts[pid]} [{op}]",
                                     "input_distances": {"char_levenshtein": edits, "char_levenshtein_normalized": d_in,
                                                         "semantic_cosine_distance": 0.01}}) + "\n")
    rows = []

    def row(pid, model, condition, op, rep, value):
        over = value if isinstance(value, dict) else {"d_out_sem": value}
        base = {c: "" for c in PAIR_COLUMNS}
        base.update({"pair_id": f"{model}|{pid}|{condition}|{op}|{rep}", "anchor_record_id": f"a-{pid}-{model}",
                     "comparison_record_id": f"c-{pid}-{model}-{op}-{rep}", "model": model, "provider": "mock",
                     "prompt_id": pid, "task_category": cats[pid], "condition": condition, "operator": op,
                     "repetition": rep, "anchor_output": "anchor", "comparison_output": "comparison",
                     "anchor_correct": "True", "comparison_correct": "True", "any_truncated": "False",
                     "any_empty": "False", "scoring_method": "answer_key", "scorable": "True", "flip_c2i": "False",
                     "flip_i2c": "False", "answer_changed": "0.0", "audit_meaning_altering":
                         str((pid, op) in set(flagged)), "audit_kind": "question_changed" if (pid, op) in set(flagged) else ""})
        if condition == "treatment":
            base["perturbed_prompt"] = f"{texts[pid]} [{op}]"
            base["perturbation_id"] = f"{pid}__{op}__42"
        base.update({k: str(v) for k, v in over.items()})
        rows.append(base)

    for (pid, model), values in controls.items():
        for rep, value in enumerate(values, start=1):
            row(pid, model, "control", "control", rep, value)
    for (pid, model, op), value in treatments.items():
        row(pid, model, "treatment", op, 1, value)
    rows.extend(extra_rows)
    with (study / "processed" / "analysis_pairs.csv").open("w", encoding="utf-8", newline="") as handle:
        w = csv.DictWriter(handle, fieldnames=PAIR_COLUMNS)
        w.writeheader()
        w.writerows(rows)
    return study


def full_controls(pids, values=(0.0, 0.0)):
    return {(p, m): list(values) for p in pids for m in MODELS}


# --------------------------------------------------------------------------- selection rules
def test_budget_mode_picks_largest_excess_and_keeps_negative_effects(tmp_path):
    study = build_study(
        tmp_path, prompts=[("P1", "logical_reasoning", "Is it so?")],
        candidates={("P1", "a"): (1, 0.02), ("P1", "b"): (2, 0.04)},
        controls=full_controls(["P1"], (0.02, 0.04)),
        treatments={("P1", m, "a"): 0.01 for m in MODELS} | {("P1", m, "b"): 0.20 for m in MODELS})
    data = co.load_study(study)
    sel = co.select_for_prompt(data, "P1")
    assert sel.status == "selected" and sel.winners == ["b"] and sel.tie_status == "unique"
    assert sel.result("b").control == pytest.approx(0.03)
    assert sel.result("b").excess == pytest.approx(0.17)
    assert sel.result("a").excess == pytest.approx(-0.02)  # negative effect retained, not clipped


def test_exact_tie_broken_by_fewer_character_edits_then_input_distance(tmp_path):
    study = build_study(
        tmp_path, prompts=[("P1", "classification", "Label it."), ("P2", "classification", "Label that.")],
        candidates={("P1", "a"): (3, 0.05), ("P1", "b"): (1, 0.05),
                    ("P2", "a"): (2, 0.06), ("P2", "b"): (2, 0.03)},
        controls=full_controls(["P1", "P2"]),
        treatments={(p, m, o): 0.3 for p in ("P1", "P2") for m in MODELS for o in ("a", "b")})
    data = co.load_study(study)
    first = co.select_for_prompt(data, "P1")
    assert first.winners == ["b"] and first.tie_status == "tie_broken_by_char_edits"
    second = co.select_for_prompt(data, "P2")
    assert second.winners == ["b"] and second.tie_status == "tie_broken_by_input_distance"


def test_unresolved_exact_tie_keeps_every_tied_operator(tmp_path):
    study = build_study(
        tmp_path, prompts=[("P1", "mathematical_reasoning", "Compute 2+2.")],
        candidates={("P1", "a"): (2, 0.05), ("P1", "b"): (2, 0.05), ("P1", "c"): (1, 0.02)},
        controls=full_controls(["P1"]),
        treatments={("P1", m, o): (0.4 if o != "c" else 0.1) for m in MODELS for o in ("a", "b", "c")})
    sel = co.select_for_prompt(co.load_study(study), "P1")
    assert sel.winners == ["a", "b"] and sel.tie_status == "unresolved_tie"
    assert "Exact tie retained" in sel.explanation
    assert sel.pareto == ["c", "a", "b"]  # c: fewest edits; a and b: largest change


def test_target_mode_selects_smallest_edit_reaching_target_or_reports_not_met(tmp_path):
    study = build_study(
        tmp_path, prompts=[("P1", "question_answering", "Who wrote it?")],
        candidates={("P1", "big"): (9, 0.09), ("P1", "small"): (1, 0.01), ("P1", "mid"): (4, 0.04)},
        controls=full_controls(["P1"]),
        treatments={("P1", m, "big"): 0.5 for m in MODELS} | {("P1", m, "small"): 0.05 for m in MODELS}
        | {("P1", m, "mid"): 0.25 for m in MODELS})
    data = co.load_study(study)
    hit = co.select_for_prompt(data, "P1", target=0.2, budget=None)
    assert hit.status == "selected" and hit.winners == ["mid"]
    capped = co.select_for_prompt(data, "P1", target=0.2, budget=0.03)
    assert capped.status == "target_not_met" and capped.best_achieved == pytest.approx(0.05)
    assert co.select_for_prompt(data, "P1", target=0.9, budget=None).status == "target_not_met"


def test_no_eligible_edit_when_everything_is_rejected_over_budget_or_flagged(tmp_path):
    study = build_study(
        tmp_path, prompts=[("P1", "code_generation", "Write f(x).")],
        candidates={("P1", "rej"): None, ("P1", "big"): (20, 0.4), ("P1", "flag"): (1, 0.01)},
        controls=full_controls(["P1"]), treatments={("P1", m, o): 0.2 for m in MODELS for o in ("big", "flag")},
        flagged=[("P1", "flag")])
    data = co.load_study(study)
    sel = co.select_for_prompt(data, "P1")
    assert sel.status == "no_eligible_edit" and sel.winners == []
    statuses = {r.operator: r.eligibility for r in sel.operators}
    assert statuses == {"big": "over_budget", "flag": "meaning_changing", "rej": "inapplicable",
                        "random_edit": "noise_benchmark"}
    assert sel.result("random_edit").status == "unmeasured"


def test_missing_control_or_truncated_treatment_is_incomplete_and_excluded(tmp_path):
    controls = full_controls(["P1", "P2"])
    controls[("P1", "model-b")] = [0.0]  # second repetition missing
    treatments = {(p, m, "a"): 0.2 for p in ("P1", "P2") for m in MODELS}
    treatments[("P2", "model-a", "a")] = {"d_out_sem": 0.2, "any_truncated": "True"}
    study = build_study(tmp_path, prompts=[("P1", "logical_reasoning", "A?"), ("P2", "logical_reasoning", "B?")],
                        candidates={("P1", "a"): (1, 0.02), ("P2", "a"): (1, 0.02)},
                        controls=controls, treatments=treatments)
    data = co.load_study(study)
    p1 = co.select_for_prompt(data, "P1")
    assert p1.status == "incomplete" and "controls_incomplete" in p1.result("a").status
    p2 = co.select_for_prompt(data, "P2")
    assert p2.status == "incomplete" and "treatment_truncated_output" in p2.result("a").status
    # A single model whose measurements are complete is still a valid scope.
    assert co.select_for_prompt(data, "P1", models=["model-a"]).status == "selected"
    ranking = co.rank_category(data, "logical_reasoning", bootstrap_draws=50)
    assert ranking.complete == []
    reasons = {e["prompt_id"]: e["reason"] for e in ranking.exclusions}
    assert "controls_incomplete" in reasons["P1"] and "treatment_truncated_output" in reasons["P2"]


def test_identical_outputs_score_zero_and_stay_in_the_comparison(tmp_path):
    study = build_study(tmp_path, prompts=[("P1", "classification", "Label it.")],
                        candidates={("P1", "a"): (1, 0.02)}, controls=full_controls(["P1"]),
                        treatments={("P1", m, "a"): 0.0 for m in MODELS})
    sel = co.select_for_prompt(co.load_study(study), "P1")
    assert sel.status == "selected" and sel.result("a").excess == 0.0


# --------------------------------------------------------------------------- category ranking
def test_category_ranking_fallback_coverage_ties_and_gap(tmp_path):
    prompts = [("P1", "classification", "One."), ("P2", "classification", "Two.")]
    study = build_study(
        tmp_path, prompts=prompts,
        candidates={("P1", "wide"): (1, 0.02), ("P2", "wide"): (1, 0.02),
                    ("P1", "narrow"): (1, 0.02), ("P2", "narrow"): None,
                    ("P1", "never1"): None, ("P2", "never1"): None, ("P1", "never2"): None, ("P2", "never2"): None},
        controls=full_controls(["P1", "P2"], (0.01, 0.03)),
        treatments={("P1", m, "wide"): 0.12 for m in MODELS} | {("P2", m, "wide"): 0.02 for m in MODELS}
        | {("P1", m, "narrow"): 0.30 for m in MODELS})
    ranking = co.rank_category(co.load_study(study), "classification", bootstrap_draws=200)
    rows = {r["operator"]: r for r in ranking.rows}
    # wide: (0.10 + -0.00) / 2 ; narrow: (0.28 + 0 fallback) / 2
    assert rows["wide"]["category_score"] == pytest.approx((0.10 + 0.0) / 2)
    assert rows["narrow"]["category_score"] == pytest.approx(0.28 / 2)
    assert rows["narrow"]["n_eligible_complete"] == 1 and rows["narrow"]["conditional_mean"] == pytest.approx(0.28)
    assert ranking.leaders == ["narrow"]
    assert rows["never1"]["rank"] == rows["never2"]["rank"] == 3 and rows["never1"]["tied_with"] == "never2"
    assert rows["narrow"]["paired_gap"] == pytest.approx(((0.28 - 0.10) + (0.0 - 0.0)) / 2)
    assert rows["narrow"]["shared_eligible_n"] == 1
    assert len(ranking.observations) == 3 * len(MODELS)
    assert ranking.max_raw[0].operator == "narrow"


# --------------------------------------------------------------------------- integrity checks
def test_duplicate_control_repetition_is_rejected(tmp_path):
    study = build_study(tmp_path, prompts=[("P1", "classification", "One.")], candidates={("P1", "a"): (1, 0.02)},
                        controls=full_controls(["P1"]), treatments={("P1", m, "a"): 0.1 for m in MODELS})
    path = study / "processed" / "analysis_pairs.csv"
    rows = list(csv.DictReader(path.open(encoding="utf-8")))
    rows.append(dict(rows[0]))  # same control repetition twice
    with path.open("w", encoding="utf-8", newline="") as handle:
        w = csv.DictWriter(handle, fieldnames=PAIR_COLUMNS)
        w.writeheader()
        w.writerows(rows)
    with pytest.raises(co.DataIntegrityError, match="Duplicate control repetition"):
        co.load_study(study)


def test_out_of_range_distance_and_unknown_candidate_are_rejected(tmp_path):
    study = build_study(tmp_path, prompts=[("P1", "classification", "One.")], candidates={("P1", "a"): (1, 0.02)},
                        controls=full_controls(["P1"]), treatments={("P1", m, "a"): 1.5 for m in MODELS})
    with pytest.raises(co.DataIntegrityError, match="outside"):
        co.load_study(study)
    other = build_study(tmp_path / "x", prompts=[("P1", "classification", "One.")], candidates={("P1", "a"): None},
                        controls=full_controls(["P1"]), treatments={("P1", "model-a", "a"): 0.1})
    with pytest.raises(co.DataIntegrityError, match="no accepted candidate"):
        co.load_study(other)


# --------------------------------------------------------------------------- validation mode
def _verdicts(path: Path, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        w = csv.writer(handle)
        w.writerow(["prompt_id", "operator", "reviewer_1", "reviewer_2", "final_verdict"])
        w.writerows(rows)
    return path


def test_validation_mode_requires_final_preserved_verdicts(tmp_path):
    study = build_study(tmp_path, prompts=[("P1", "classification", "One.")],
                        candidates={("P1", "a"): (1, 0.02), ("P1", "b"): (1, 0.02), ("P1", "c"): (1, 0.02)},
                        controls=full_controls(["P1"]),
                        treatments={("P1", m, o): 0.1 for m in MODELS for o in ("a", "b", "c")})
    verdicts = _verdicts(tmp_path / "v.csv", [("P1", "a", "preserved", "preserved", "preserved"),
                                              ("P1", "b", "preserved", "changed", "changed")])
    data = co.load_study(study, verdicts_path=verdicts)
    assert data.evidence_mode == "validation"
    assert data.eligibility("P1", "a", 0.1)[0] == "eligible"
    assert data.eligibility("P1", "b", 0.1)[0] == "meaning_changing"
    assert data.eligibility("P1", "c", 0.1)[0] == "uncertain"
    assert data.verdict_agreement["observed_agreement"] == pytest.approx(0.5)


def test_held_out_claim_rule_validates_clear_winner_and_rejects_overlap(tmp_path):
    pids = [f"V{i}" for i in range(8)]
    effects = [0.30, 0.32, 0.28, 0.31, 0.29, 0.33, 0.30, 0.27]
    treatments = {}
    for pid, effect in zip(pids, effects):
        for m in MODELS:
            treatments[(pid, m, "nom")] = effect
            treatments[(pid, m, "alt")] = 0.02
    candidates = {(p, o): (1, 0.02) for p in pids for o in ("nom", "alt")}
    study = build_study(tmp_path, prompts=[(p, "classification", f"Item {p}.") for p in pids],
                        candidates=candidates, controls=full_controls(pids), treatments=treatments)
    verdicts = _verdicts(tmp_path / "v.csv", [(p, o, "preserved", "preserved", "preserved") for p, o in candidates])
    data = co.load_study(study, verdicts_path=verdicts)
    result = co.held_out_validation(data, {"classification": "nom"})
    assert result["family_size"] == 2  # vs alt and vs unchanged
    assert result["decisions"]["classification"]["validated"] is True
    weak = co.held_out_validation(data, {"classification": "alt"})
    assert weak["decisions"]["classification"]["validated"] is False
    with pytest.raises(co.DataIntegrityError, match="different from the discovery"):
        co.held_out_validation(data, {"classification": "nom"}, discovery=data)


# --------------------------------------------------------------------------- screens and helpers
@pytest.mark.parametrize("original, perturbed, expected", [
    ("Options: [Joy, Anger, Fear].", "Options: [Joy, @nger, Fear].", "bracketed option"),
    ("Dave sits next to Bob. Where is Dave?", "D@ve sits next to Bob. Where is Dave?", "named entity 'Dave'"),
    ("Solve 3x + 2y = 16.", "Solve 3x + 2y = 1h.", "quantities changed"),
    ("List all valid orders.", "List all invalid orders.", "logical/negation"),
    ("Write fibonacci(n) that returns a list.", "Write f1bonacci(n) that returns a list.", "code identifier"),
    ("Task A must run before Task B.", "Task must run before Task B.", "variable 'A'"),
])
def test_protected_content_screen_flags_task_changes(original, perturbed, expected):
    assert any(expected in change for change in co.protected_content_changes(original, perturbed))


@pytest.mark.parametrize("original, perturbed", [
    ("A store sells apples.", "a store sells apples."),
    ("Is it raining?", "Is it raining"),
    ("Classify the review as positive or negative.", "Categorize the review as positive or negative."),
    ("Count the customer support requests.", "Count the cu5tomer support requests."),
])
def test_protected_content_screen_passes_surface_edits(original, perturbed):
    assert co.protected_content_changes(original, perturbed) == []


def test_bootstrap_interval_is_deterministic_and_uses_plan_percentiles():
    values = [0.1, -0.05, 0.2, 0.0, 0.07]
    first = co.bootstrap_interval(values, draws=10_000)
    assert first == co.bootstrap_interval(values, draws=10_000)
    assert first[0] < sum(values) / len(values) < first[1]


def test_recommendation_labels_custom_budget_and_validation(tmp_path):
    study = build_study(tmp_path, prompts=[("P1", "classification", "One."), ("P2", "classification", "Two.")],
                        candidates={(p, o): (1, 0.02) for p in ("P1", "P2") for o in ("a", "b")},
                        controls=full_controls(["P1", "P2"]),
                        treatments={(p, m, o): (0.3 if o == "a" else 0.1) for p in ("P1", "P2") for m in MODELS
                                    for o in ("a", "b")})
    rankings = co.rank_all(co.load_study(study), co.STANDARD_BUDGETS, bootstrap_draws=20)
    standard = co.category_recommendation("classification", 0.05, rankings, measured_prompt=False)
    assert standard["operators"] == ["a"] and standard["budget"] == "0.05"
    assert standard["evidence_status"].startswith("exploratory") and "unmeasured" in standard["prompt_status"]
    custom = co.category_recommendation("classification", 0.07, rankings, measured_prompt=True)
    assert custom["budget"] == "0.10" and "starting candidate" in custom["note"]
    confirmed = co.category_recommendation("classification", 0.10, rankings, measured_prompt=True,
                                           validated={"classification": "a"})
    assert confirmed["evidence_status"] == "validated on held-out prompts"


def test_parse_budget():
    assert co.parse_budget("none") is None and co.parse_budget("0.05") == 0.05
    with pytest.raises(ValueError):
        co.parse_budget("0")


def test_cli_prompt_report_on_fixture(tmp_path):
    import category_operators as cli
    study = build_study(tmp_path, prompts=[("P1", "logical_reasoning", "Is it so?")],
                        candidates={("P1", "a"): (1, 0.02)}, controls=full_controls(["P1"]),
                        treatments={("P1", m, "a"): 0.2 for m in MODELS})
    cli.main(["prompt", "--study-dir", str(study), "--prompt-id", "P1", "--draws", "20"])
    reports = list((study / "analysis" / "prompt_reports").glob("P1__panel__budget-0.10.*"))
    assert {p.suffix for p in reports} == {".md", ".json"}
    record = json.loads(next(p for p in reports if p.suffix == ".json").read_text(encoding="utf-8"))
    assert record["status"] == "selected" and record["selected"] == ["a"]


@pytest.mark.parametrize(("text", "expected"), [
    ("Classify this Python snippet as valid or invalid.", "classification"),
    ("Write a Python function that returns the length of a string.", "code_generation"),
    ("Determine the truth value of P implies Q.", "logical_reasoning"),
    ("Calculate the determinant of this matrix.", "mathematical_reasoning"),
    ("Who wrote Pride and Prejudice?", "question_answering"),
    ("Write a function and calculate the determinant of this matrix.", None),
    ("Write a poem about snow.", None),
])
def test_category_suggestion_is_grounded_in_requested_task(text, expected):
    from apsa.analysis.prompt_categories import suggest_category

    result = suggest_category(text)
    assert result["proposed_category"] == expected and result["reason"]
    assert "confidence" not in result


def test_prepared_prompt_requires_ambiguous_confirmation_and_saves_override(tmp_path, monkeypatch):
    import category_operators as cli
    from run_study import build_candidates
    from apsa.metrics.input_distance import semantic

    class LocalEmbedder:
        model_name = "fixture"

        def __init__(self, model_name):
            pass

        def encode(self, texts):
            return [[1.0, 0.0] for _ in texts]

    monkeypatch.setattr(semantic, "SentenceTransformerEmbedder", LocalEmbedder)
    monkeypatch.setattr(sys.stdin, "isatty", lambda: False)
    base = ["prompt", "--draws", "20", "--output-dir", str(tmp_path)]
    with pytest.raises(SystemExit, match="Confirm a category"):
        cli.main([*base, "--text", "Write a function and calculate the determinant."])
    assert not (tmp_path / "record.json").exists()
    prompt = "Who wrote Pride and Prejudice?"
    cli.main([*base, "--text", prompt, "--category", "logical_reasoning", "--reference", "Jane Austen"])
    record = json.loads((tmp_path / "record.json").read_text(encoding="utf-8"))
    assert record["category_identification"]["source"] == "manual_override"
    assert record["category_identification"]["proposed_category"] == "question_answering"
    assert record["status"] == "unmeasured" and len(record["candidates"]) == 10
    assert record["candidates"][-1]["role"] == "noise_benchmark"
    verdicts = list(csv.DictReader((tmp_path / "verdicts_template.csv").open(encoding="utf-8", newline="")))
    source_row = next(csv.DictReader((tmp_path / "prompt_row.csv").open(encoding="utf-8", newline="")))
    rebuilt = build_candidates([source_row], [o["operator"] for o in record["candidates"]],
                               record["candidate_seed"], semantic.SemanticDistanceCalculator(LocalEmbedder("fixture")))
    assert all(v["perturbation_id"] in {c.get("perturbation_id") for c in rebuilt} for v in verdicts)
    assert "--pairs-only" in (tmp_path / "report.md").read_text(encoding="utf-8")
    examples = {
        "question_answering": "Who discovered penicillin?",
        "mathematical_reasoning": "What is 12 + 17?",
        "classification": "Classify the following review as positive or negative.",
        "code_generation": "Write a Python function to count the characters in a string.",
        "logical_reasoning": "If all dogs are mammals, and Rex is a dog, is Rex a mammal?",
    }
    for category, text in examples.items():
        output = tmp_path / category
        cli.main(["prompt", "--text", text, "--draws", "20", "--output-dir", str(output)])
        generated = json.loads((output / "record.json").read_text(encoding="utf-8"))
        assert generated["category"] == category and generated["category_identification"]["source"] == "inferred"


def test_cli_search_reports_logic_gap_and_all_ten_operators(tmp_path):
    import category_operators as cli

    cli.main(["prompt", "--search", "truth value of (P implies Q)", "--draws", "20", "--output-dir", str(tmp_path)])
    path = tmp_path / "LOGIC-010__panel__budget-0.10.json"
    record = json.loads(path.read_text(encoding="utf-8"))
    assert record["category_identification"]["source"] == "dataset"
    assert record["selected"] == ["punctuation"]
    assert record["closest_rivals"][0]["excess_gap"] == pytest.approx(0.1093, abs=0.00005)
    assert len(record["operators"]) == 10
    noise = record["operators"][-1]
    assert noise["operator"] == "random_edit" and noise["status"] == "measured"
    assert noise["role"] == "noise_benchmark" and "unaudited" in noise["eligibility_detail"]
    punctuation = next(o for o in record["operators"] if o["operator"] == "punctuation")
    assert punctuation["exact_edit"][0]["removed"] == "."
    assert all(len(m["control_records"]) == 2 for m in punctuation["per_model"])
    report = path.with_suffix(".md").read_text(encoding="utf-8")
    assert "+0.1093" in report and "<th>Original response</th>" in report


def test_explicit_reference_scores_only_configured_text_prompts(tmp_path):
    import pandas as pd
    from analyze_study import score_generations

    frame = pd.DataFrame([
        {"prompt_id": "NEW-A", "task_category": "question_answering",
         "output": "A short explanation.\nFinal answer: Jane Austen.", "finish_reason": "stop"},
        {"prompt_id": "NEW-A", "task_category": "question_answering",
         "output": "Final answer: Jane Austen and another author", "finish_reason": "stop"},
        {"prompt_id": "NEW-B", "task_category": "code_generation",
         "output": "Final answer: example", "finish_reason": "stop"},
    ])
    scored = score_generations(frame, tmp_path / "cache.json", {"NEW-A": "Jane Austen"})
    assert scored["correct"].tolist() == [True, False, None]
    assert scored["scoring_method"].tolist() == ["explicit_reference_exact_match"] * 2 + ["unscored"]
    assert pd.isna(scored["final_answer_norm"].iloc[-1])


def test_runner_job_order_shuffle_is_recorded_and_deterministic(tmp_path):
    from run_study import ModelWorker
    from apsa.llm_providers import MockProvider

    prompts = [{"prompt_id": "P1", "task_category": "classification", "original_prompt": "x"}]
    cands = [{"prompt_id": "P1", "operator": op, "status": "accepted", "perturbed_prompt": f"x {op}",
              "perturbation_id": op, "input_distances": {"char_levenshtein_normalized": d}}
             for op, d in (("a", 0.05), ("b", 0.2), ("c", 0.01))]

    def worker(**kw):
        (tmp_path / "raw").mkdir(exist_ok=True)
        return ModelWorker(study_dir=tmp_path, study_id="t", model_cfg={"name": "m", "provider": "mock"},
                           provider=MockProvider("m"), generation={}, system_prompt="", prompts=prompts,
                           candidates=cands, control_repetitions=2, max_wait=1, is_mock=True, max_calls=None, **kw)

    plain = [(j[1], j[2], j[3]) for j in worker()._jobs()]
    assert plain[0] == ("anchor", None, 1) and plain[1:3] == [("control", None, 1), ("control", None, 2)]
    shuffled = [(j[1], j[2], j[3]) for j in worker(shuffle_seed=7)._jobs()]
    assert shuffled[0] == ("anchor", None, 1) and sorted(shuffled) == sorted(plain)
    assert shuffled == [(j[1], j[2], j[3]) for j in worker(shuffle_seed=7)._jobs()]
    capped = [j[2] for j in worker(treatment_allowed=lambda c: c["input_distances"]["char_levenshtein_normalized"] <= 0.1)._jobs()
              if j[1] == "treatment"]
    assert capped == ["a", "c"]


# --------------------------------------------------------------------------- main_v1 reproduction
MAIN = ROOT / "results" / "study" / "main_v1"
needs_main = pytest.mark.skipif(not (MAIN / "processed" / "analysis_pairs.csv").exists(),
                                reason="main_v1 study artifacts not present")


@pytest.fixture(scope="module")
def main_data():
    return co.load_study(MAIN)


@needs_main
def test_main_v1_category_leaders_match_plan_at_every_budget(main_data):
    expected = {
        "0.01": ["punctuation", "char_substitution", "char_substitution", "char_substitution", "capitalization"],
        "0.02": ["punctuation", "char_substitution", "punctuation", "char_substitution", "punctuation"],
        "0.05": ["synonym", "char_substitution", "punctuation", "char_substitution", "punctuation"],
        "0.10": ["synonym", "word_insertion", "punctuation", "char_substitution", "punctuation"],
        "none": ["synonym", "word_insertion", "instruction_reordering", "whitespace", "punctuation"],
    }
    for label, leaders in expected.items():
        budget = co.parse_budget(label)
        got = [co.rank_category(main_data, c, budget, bootstrap_draws=10).leaders for c in main_data.categories]
        assert got == [[x] for x in leaders], label


@needs_main
def test_main_v1_budget_010_scores_gaps_exclusions_and_maxima(main_data):
    expected = {  # category: (leader score, coverage, gap, ci_low, ci_high, shared_gap, shared_n, excluded, searched)
        "classification": (0.0761, 10, 0.0060, -0.0388, 0.0565, 0.0060, 10, [], 305),
        "code_generation": (0.0386, 10, 0.0074, -0.0138, 0.0279, -0.0037, 7, [], 330),
        "logical_reasoning": (0.0744, 9, 0.0114, -0.0115, 0.0404, 0.0095, 8, ["LOGIC-007"], 245),
        "mathematical_reasoning": (0.0853, 8, 0.0256, -0.0474, 0.0882, -0.0351, 4, ["MATH-005", "MATH-008"], 225),
        "question_answering": (0.0426, 10, 0.0044, -0.0065, 0.0153, 0.0020, 7, [], 230),
    }
    for cat, (score, cov, gap, low, high, sgap, sn, excluded, searched) in expected.items():
        r = co.rank_category(main_data, cat, 0.10)
        top = r.rows[0]
        assert round(top["category_score"], 4) == score
        assert top["n_eligible_complete"] == cov
        assert round(top["paired_gap"], 4) == gap
        assert round(top["gap_ci_low"], 4) == low and round(top["gap_ci_high"], 4) == high
        assert round(top["shared_eligible_gap"], 4) == sgap and top["shared_eligible_n"] == sn
        assert [e["prompt_id"] for e in r.exclusions] == excluded
        assert len(r.observations) == searched
    math_max = co.rank_category(main_data, "mathematical_reasoning", 0.10, bootstrap_draws=10).max_raw
    assert sorted(m.operator for m in math_max) == ["capitalization", "synonym", "word_substitution"]
    assert all(round(m.raw, 4) == 0.7400 and m.prompt_id == "MATH-010" for m in math_max)


@needs_main
def test_main_v1_logic_010_worked_example(main_data):
    single = co.select_for_prompt(main_data, "LOGIC-010", models=co.resolve_model(main_data.models, "gpt-oss-120b"))
    chosen = single.chosen
    assert single.status == "selected" and single.winners == ["punctuation"]
    assert chosen.char_edits == 1 and round(chosen.d_in_char, 4) == 0.0135
    assert round(chosen.raw, 4) == 0.7999 and chosen.control == 0.0 and round(chosen.excess, 4) == 0.7999
    row = chosen.measurements[0].row
    assert row["anchor_correct"] == "True" and row["comparison_correct"] == "True"
    assert row["comparison_output"].strip() == "Final answer: True"
    assert row["perturbed_prompt"] == "Determine the truth value of (P implies Q) when P is False and Q is False"
    panel = co.select_for_prompt(main_data, "LOGIC-010")
    assert panel.winners == ["punctuation"] and round(panel.chosen.excess, 4) == 0.2891


@needs_main
def test_main_v1_math_010_panel_tie_is_retained(main_data):
    sel = co.select_for_prompt(main_data, "MATH-010")
    assert sel.winners == ["synonym", "word_substitution"] and sel.tie_status == "unresolved_tie"


@needs_main
def test_main_v1_excluded_prompt_is_incomplete_not_a_maximum(main_data):
    sel = co.select_for_prompt(main_data, "MATH-005")
    assert sel.status == "incomplete" and sel.winners == [] and sel.provisional_best
