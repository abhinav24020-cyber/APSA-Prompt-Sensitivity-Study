"""Category-based selection of perturbation operators.

Implements docs/roadmap/category_operator_implementation_plan.md and
docs/roadmap/category_operator_stage_by_stage.md on top of a finished APSA study
(``run_study.py`` + ``analyze_study.py`` outputs). Nothing here calls a model provider:
every quantity is computed from stored, already-scored pairs.

Core quantities (plan Section 1)::

    control(p, m)        = mean(d_out_sem(anchor, repeat_r) for r in repeats)
    effect(p, m, o)      = d_out_sem(anchor, treatment_o) - control(p, m)    # negatives kept
    prompt_score(p, o)   = mean over the model scope of effect(p, m, o)
    category_score(c, o) = mean over complete prompts of prompt_score, with 0 for an
                           operator that has no eligible candidate on a prompt (fallback:
                           the unchanged prompt is sent).

A candidate is *eligible* when it was generated, is not a no-op, fits the input budget
``0 < d_in_char <= budget`` and is not flagged as meaning-changing (retrospective
audit) or has a final ``preserved`` verdict (validation runs).
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import random
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from statistics import fmean, mean, stdev
from typing import Any, Iterable

# --------------------------------------------------------------------------- constants
DEFAULT_BUDGET = 0.10
STANDARD_BUDGETS: tuple[float | None, ...] = (0.01, 0.02, 0.05, 0.10, None)
BOOTSTRAP_SEED = 20261124
BOOTSTRAP_DRAWS = 10_000
NOISE_OPERATORS = frozenset({"random_edit"})
VALIDATION_ALPHA = 0.05

CATEGORY_LABELS = {
    "classification": "Classification",
    "code_generation": "Code generation",
    "logical_reasoning": "Logical reasoning",
    "mathematical_reasoning": "Mathematical reasoning",
    "question_answering": "Question answering",
}

MODEL_LABELS = {
    "allam-2-7b": "ALLaM-2-7B",
    "gemini-3.1-flash-lite": "Gemini 3.1 Flash-Lite",
    "openai/gpt-oss-120b": "GPT-OSS-120B",
    "openai/gpt-oss-20b": "GPT-OSS-20B",
    "qwen/qwen3.8-27b": "Qwen 3.8 27B",
}

OPERATOR_DESCRIPTIONS = {
    "capitalization": "changes the case of one word",
    "char_substitution": "replaces one character with a look-alike (a typo)",
    "punctuation": "removes or adds terminal punctuation",
    "whitespace": "adds extra spacing",
    "word_insertion": "inserts a low-information filler word (seed 42: 'Carefully')",
    "word_deletion": "deletes one non-essential word",
    "synonym": "replaces one word with a dictionary synonym",
    "word_substitution": "replaces one word with a contextual alternative",
    "instruction_reordering": "moves one sentence to a different position",
    "random_edit": "applies random character edits (noise benchmark)",
}

# Plan Section 3: why each 0.10 category leader is worth testing.
CATEGORY_RATIONALE = {
    ("classification", "synonym"):
        "Replacing an instruction verb (e.g. Classify -> Categorize) changes the cue used to request a "
        "label while preserving the label set and evidence.",
    ("code_generation", "word_insertion"):
        "A leading tone cue ('Carefully') can change which implementation the model writes while "
        "preserving the signature and input/output contract.",
    ("logical_reasoning", "punctuation"):
        "A terminal punctuation edit changes the cue at the end of the prompt while leaving premises and "
        "the requested conclusion intact.",
    ("mathematical_reasoning", "char_substitution"):
        "A typo in prose changes how the task is rendered while leaving quantities and the requested "
        "result intact.",
    ("question_answering", "punctuation"):
        "Editing the question's final delimiter can change the form or length of the answer while keeping "
        "the requested fact fixed.",
}

# Coverage of the retrospective main_study audit (config/experiments/main_study_semantic_audit.yaml).
MAIN_STUDY_AUDIT_FILE = "config/experiments/main_study_semantic_audit.yaml"
MAIN_STUDY_AUDIT_COVERAGE = {
    "word_substitution": "every candidate of this operator was audited",
    "word_deletion": "every candidate of this operator was audited",
    "char_substitution": "every candidate of this operator was audited",
    "instruction_reordering": "every candidate of this operator was audited",
    "synonym": "every candidate of this operator was audited",
    "capitalization": "operator audited by a sample of 5 candidates",
    "punctuation": "operator audited by a sample of 5 candidates",
    "whitespace": "operator audited by a sample of 5 candidates",
    "word_insertion": "operator audited by a sample of 5 candidates",
}

ELIGIBLE = "eligible"
MEASURED = "measured"


class DataIntegrityError(ValueError):
    """Raised when the stored study violates a structural assumption of the analysis."""


# --------------------------------------------------------------------------- helpers
def budget_label(budget: float | None) -> str:
    return "none" if budget is None else f"{budget:.2f}"


def parse_budget(text: str | float | None) -> float | None:
    if text is None:
        return None
    if isinstance(text, (int, float)):
        value = float(text)
    else:
        cleaned = text.strip().lower()
        if cleaned in {"", "none", "inf", "nocap", "no-cap", "uncapped"}:
            return None
        value = float(cleaned)
    if not value > 0:
        raise ValueError("budget must be positive (or 'none' for no character cap)")
    return value


def model_label(model: str) -> str:
    return MODEL_LABELS.get(model, model)


def resolve_model(models: Iterable[str], requested: str | None) -> list[str]:
    """Return the model scope: all models for None/'panel', else exactly one matching model."""
    models = list(models)
    if requested is None or requested.strip().lower() in {"panel", "all"}:
        return models
    wanted = requested.strip().lower()
    exact = [m for m in models if m.lower() == wanted or model_label(m).lower() == wanted]
    if exact:
        return exact[:1]
    partial = [m for m in models if wanted in m.lower() or wanted in model_label(m).lower()]
    if len(partial) == 1:
        return partial
    raise ValueError(f"Unknown or ambiguous model {requested!r}; choose one of {models} or 'panel'")


def _sha256(path: Path) -> str | None:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None


def _find_root(start: Path) -> Path:
    for parent in [start, *start.parents]:
        if (parent / "pyproject.toml").exists():
            return parent
    return Path.cwd()


def _truthy(value: Any) -> bool | None:
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if text in {"true", "1", "1.0"}:
        return True
    if text in {"false", "0", "0.0"}:
        return False
    return None


def _float_or_none(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def row_problem(row: dict[str, str]) -> str | None:
    """Why a stored pair cannot be used as a measurement (None when usable)."""
    if _truthy(row.get("any_empty")):
        return "empty_output"
    if _truthy(row.get("any_truncated")):
        return "truncated_output"
    raw = row.get("d_out_sem", "")
    if raw in ("", None):
        return "missing_score"
    try:
        value = float(raw)
    except ValueError:
        return "missing_score"
    if not math.isfinite(value):
        return "nonfinite_score"
    return None


def bootstrap_interval(values: list[float], *, seed: int = BOOTSTRAP_SEED,
                       draws: int = BOOTSTRAP_DRAWS) -> tuple[float, float] | tuple[None, None]:
    """Percentile 95% interval of the mean (same resampling scheme as the plan's appendix)."""
    if not values:
        return None, None
    rng = random.Random(seed)
    k = len(values)
    samples = sorted(fmean(rng.choices(values, k=k)) for _ in range(draws))
    low_index = int(round(0.025 * draws)) - 1
    high_index = int(round(0.975 * draws)) - 1
    return samples[low_index], samples[high_index]


# --------------------------------------------------------------------------- data model
@dataclass
class StudyData:
    """Everything the selection workflow needs from one stored study."""

    study_dir: Path
    study_id: str
    config_path: str
    models: list[str]
    operators: list[str]
    control_repetitions: int
    prompt_ids: list[str]
    prompts: dict[str, dict[str, Any]]
    candidates: dict[tuple[str, str], dict[str, Any]]
    treatments: dict[tuple[str, str, str], dict[str, str]]
    controls: dict[tuple[str, str], dict[int, dict[str, str]]]
    flagged: dict[tuple[str, str], str]
    verdicts: dict[tuple[str, str], str] | None = None
    verdict_agreement: dict[str, Any] | None = None
    source_hashes: dict[str, str | None] = field(default_factory=dict)

    @property
    def evidence_mode(self) -> str:
        return "validation" if self.verdicts is not None else "retrospective"

    def prompts_in_category(self, category: str) -> list[str]:
        return [p for p in self.prompt_ids if self.prompts[p]["category"] == category]

    @property
    def categories(self) -> list[str]:
        seen: list[str] = []
        for p in self.prompt_ids:
            cat = self.prompts[p]["category"]
            if cat not in seen:
                seen.append(cat)
        return sorted(seen)

    # ---- Stage 3: eligibility -------------------------------------------------
    def eligibility(self, prompt: str, operator: str, budget: float | None) -> tuple[str, str]:
        cand = self.candidates.get((prompt, operator))
        if cand is None:
            return "not_generated", "no candidate record for this prompt and operator"
        if cand.get("status") != "accepted":
            reason = cand.get("reason") or "inapplicable_or_no_op"
            if str(reason).startswith("error"):
                return "generator_error", str(reason)
            return "inapplicable", str(reason)
        distance = float(cand["input_distances"]["char_levenshtein_normalized"])
        if not distance > 0:
            return "no_op", "the edit does not change the prompt"
        if budget is not None and distance > budget:
            return "over_budget", f"d_in_char {distance:.4f} exceeds budget {budget_label(budget)}"
        if self.verdicts is None:
            if (prompt, operator) in self.flagged:
                kind = self.flagged[(prompt, operator)] or "meaning-altering"
                return "meaning_changing", f"retrospective audit flag: {kind}"
            return ELIGIBLE, self.preservation_evidence(operator)
        verdict = self.verdicts.get((prompt, operator))
        if verdict == "preserved":
            return ELIGIBLE, "final reviewer verdict: preserved"
        if verdict == "changed":
            return "meaning_changing", "final reviewer verdict: changed"
        return "uncertain", ("final reviewer verdict: uncertain" if verdict == "uncertain"
                             else "no final preservation verdict recorded")

    def preservation_evidence(self, operator: str) -> str:
        if self.verdicts is not None:
            return "final reviewer verdict: preserved"
        if self.config_path.replace("\\", "/").endswith("config/experiments/main_study.yaml"):
            coverage = MAIN_STUDY_AUDIT_COVERAGE.get(operator, "operator not covered by the audit")
            return f"not flagged by the retrospective audit ({coverage})"
        return "not flagged by the retrospective audit"

    # ---- Stage 4/5: measurement ----------------------------------------------
    def control_state(self, prompt: str, model: str) -> tuple[dict[int, float] | None, str]:
        reps = self.controls.get((prompt, model), {})
        usable: dict[int, float] = {}
        problems = []
        for rep, row in sorted(reps.items()):
            problem = row_problem(row)
            if problem is None:
                usable[rep] = float(row["d_out_sem"])
            else:
                problems.append(f"repeat {rep}: {problem}")
        if len(usable) != self.control_repetitions:
            missing = self.control_repetitions - len(reps)
            detail = "; ".join(problems + ([f"{missing} repeat(s) missing"] if missing > 0 else []))
            return None, f"controls_incomplete ({len(usable)}/{self.control_repetitions} usable: {detail})"
        return usable, "ok"


@dataclass
class Measurement:
    prompt_id: str
    model: str
    operator: str
    status: str
    raw: float | None = None
    control_mean: float | None = None
    control_values: dict[int, float] | None = None
    excess: float | None = None
    row: dict[str, str] | None = None

    @property
    def pair_id(self) -> str | None:
        return self.row.get("pair_id") if self.row else None


def measure(data: StudyData, prompt: str, model: str, operator: str) -> Measurement:
    controls, control_status = data.control_state(prompt, model)
    row = data.treatments.get((prompt, model, operator))
    if row is None:
        status = "treatment_missing"
    else:
        problem = row_problem(row)
        status = f"treatment_{problem}" if problem else MEASURED
    if controls is None:
        status = control_status if status == MEASURED else f"{status}; {control_status}"
    if status != MEASURED:
        return Measurement(prompt, model, operator, status, row=row)
    raw = float(row["d_out_sem"])
    control_mean = mean(controls.values())
    return Measurement(prompt, model, operator, MEASURED, raw=raw, control_mean=control_mean,
                       control_values=controls, excess=raw - control_mean, row=row)


# --------------------------------------------------------------------------- loading
def _load_verdicts(path: Path) -> tuple[dict[tuple[str, str], str], dict[str, Any] | None]:
    """Read final preservation verdicts; report agreement when two reviewer columns exist."""
    rows = list(csv.DictReader(path.open(encoding="utf-8", newline="")))
    if not rows:
        raise DataIntegrityError(f"{path} has no verdict rows")
    allowed = {"preserved", "changed", "uncertain"}
    final_col = "final_verdict" if "final_verdict" in rows[0] else "verdict"
    if final_col not in rows[0]:
        raise DataIntegrityError(f"{path} needs a 'verdict' or 'final_verdict' column")
    verdicts: dict[tuple[str, str], str] = {}
    for row in rows:
        value = (row.get(final_col) or "").strip().lower()
        if value not in allowed:
            raise DataIntegrityError(f"Invalid verdict {value!r} for {row.get('prompt_id')}/{row.get('operator')}")
        key = (row["prompt_id"].strip(), row["operator"].strip())
        if key in verdicts:
            raise DataIntegrityError(f"Duplicate verdict for {key}")
        verdicts[key] = value
    agreement = None
    if {"reviewer_1", "reviewer_2"} <= set(rows[0]):
        pairs = [((r["reviewer_1"] or "").strip().lower(), (r["reviewer_2"] or "").strip().lower()) for r in rows]
        n = len(pairs)
        observed = sum(a == b for a, b in pairs) / n
        c1, c2 = Counter(a for a, _ in pairs), Counter(b for _, b in pairs)
        expected = sum(c1[k] * c2[k] for k in allowed) / (n * n)
        kappa = (observed - expected) / (1 - expected) if expected < 1 else 1.0
        agreement = {"n": n, "observed_agreement": observed, "cohens_kappa": kappa,
                     "final_counts": dict(Counter(verdicts.values()))}
    return verdicts, agreement


def load_study(study_dir: Path | str, *, verdicts_path: Path | str | None = None,
               dataset_path: Path | str | None = None) -> StudyData:
    """Load and integrity-check a finished study (manifest, candidates, scored pairs)."""
    study_dir = Path(study_dir).resolve()
    manifest_path = study_dir / "study_manifest.json"
    candidates_path = study_dir / "candidates.jsonl"
    pairs_path = study_dir / "processed" / "analysis_pairs.csv"
    for required in (manifest_path, candidates_path, pairs_path):
        if not required.exists():
            raise FileNotFoundError(f"Missing study artifact: {required}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    config = manifest["config"]
    models = [m["name"] for m in config["models"]]
    operators = [op for op in config["operators"] if op not in NOISE_OPERATORS]
    reps = int(config["control_repetitions"])
    root = _find_root(study_dir)

    candidates: dict[tuple[str, str], dict[str, Any]] = {}
    for line in candidates_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        cand = json.loads(line)
        key = (cand["prompt_id"], cand["operator"])
        if key in candidates:
            raise DataIntegrityError(f"Duplicate candidate for {key}; the analysis expects one per prompt and operator")
        candidates[key] = cand

    ds_path = Path(dataset_path) if dataset_path else root / manifest.get("dataset_path", config.get("dataset", ""))
    dataset: dict[str, dict[str, str]] = {}
    if ds_path.exists() and ds_path.is_file():
        dataset = {r["prompt_id"]: r for r in csv.DictReader(ds_path.open(encoding="utf-8", newline=""))}

    prompt_ids = list(manifest["selected_prompt_ids"])
    prompts: dict[str, dict[str, Any]] = {}
    for pid in prompt_ids:
        ds = dataset.get(pid, {})
        category = ds.get("task_category") or next(
            (c["task_category"] for (p, _), c in candidates.items() if p == pid), None)
        if category is None:
            raise DataIntegrityError(f"Cannot determine the category of {pid}")
        metadata = {}
        if ds.get("metadata"):
            try:
                metadata = json.loads(ds["metadata"])
            except json.JSONDecodeError:
                metadata = {}
        prompts[pid] = {"category": category, "original_prompt": ds.get("original_prompt"),
                        "expected_answer": ds.get("expected_answer"),
                        "eval_metric": metadata.get("eval_metric")}

    treatments: dict[tuple[str, str, str], dict[str, str]] = {}
    controls: dict[tuple[str, str], dict[int, dict[str, str]]] = defaultdict(dict)
    flagged: dict[tuple[str, str], str] = {}
    with pairs_path.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            prompt, model, operator = row["prompt_id"], row["model"], row["operator"]
            value = _float_or_none(row.get("d_out_sem"))
            if value is not None and not 0.0 <= value <= 1.0:
                raise DataIntegrityError(f"d_out_sem {value} outside [0, 1] in {row.get('pair_id')}")
            if row["condition"] == "control":
                rep = int(row["repetition"])
                if rep in controls[(prompt, model)]:
                    raise DataIntegrityError(f"Duplicate control repetition {rep} for {prompt} / {model}")
                controls[(prompt, model)][rep] = row
                continue
            key = (prompt, model, operator)
            if key in treatments:
                raise DataIntegrityError(f"Duplicate treatment key {key}")
            cand = candidates.get((prompt, operator))
            if cand is None or cand.get("status") != "accepted":
                raise DataIntegrityError(f"Treatment {row.get('pair_id')} has no accepted candidate")
            if row.get("perturbed_prompt") and row["perturbed_prompt"] != cand.get("perturbed_prompt"):
                raise DataIntegrityError(f"Treatment {row.get('pair_id')} does not match its candidate text")
            treatments[key] = row
            if _truthy(row.get("audit_meaning_altering")):
                flagged[(prompt, operator)] = row.get("audit_kind") or "meaning-altering"

    verdicts = agreement = None
    if verdicts_path:
        verdicts, agreement = _load_verdicts(Path(verdicts_path))

    hashes = {"study_manifest.json": _sha256(manifest_path), "candidates.jsonl": _sha256(candidates_path),
              "processed/analysis_pairs.csv": _sha256(pairs_path)}
    if verdicts_path:
        hashes["verdicts"] = _sha256(Path(verdicts_path))
    audit_file = root / MAIN_STUDY_AUDIT_FILE
    if verdicts is None and audit_file.exists():
        hashes[MAIN_STUDY_AUDIT_FILE] = _sha256(audit_file)
    return StudyData(study_dir=study_dir, study_id=manifest.get("study_id", study_dir.name),
                     config_path=manifest.get("config_path", ""), models=models, operators=operators,
                     control_repetitions=reps, prompt_ids=prompt_ids, prompts=prompts,
                     candidates=candidates, treatments=treatments, controls=dict(controls),
                     flagged=flagged, verdicts=verdicts, verdict_agreement=agreement,
                     source_hashes=hashes)


# --------------------------------------------------------------------------- category rankings
@dataclass
class CategoryRanking:
    category: str
    budget: float | None
    models: list[str]
    prompts: list[str]
    complete: list[str]
    exclusions: list[dict[str, str]]
    eligible: dict[str, list[str]]
    eligible_before: dict[str, int]
    scores: dict[str, dict[str, float]]
    rows: list[dict[str, Any]]
    observations: list[Measurement]
    max_raw: list[Measurement]
    max_excess: list[Measurement]

    @property
    def leaders(self) -> list[str]:
        return [r["operator"] for r in self.rows if r["rank"] == 1]


def _competition_ranks(values: dict[str, float]) -> dict[str, int]:
    ordered = sorted(values, key=lambda op: (-values[op], op))
    ranks: dict[str, int] = {}
    for position, op in enumerate(ordered, start=1):
        previous = ordered[position - 2] if position > 1 else None
        ranks[op] = ranks[previous] if previous is not None and values[previous] == values[op] else position
    return ranks


def _flip_counts(data: StudyData, prompts: list[str], operator: str, models: list[str]) -> tuple[int, int, int]:
    c2i = i2c = scorable = 0
    for prompt in prompts:
        for model in models:
            row = data.treatments.get((prompt, model, operator))
            if row is None or not _truthy(row.get("scorable")):
                continue
            scorable += 1
            c2i += bool(_truthy(row.get("flip_c2i")))
            i2c += bool(_truthy(row.get("flip_i2c")))
    return c2i, i2c, scorable


def rank_category(data: StudyData, category: str, budget: float | None = DEFAULT_BUDGET,
                  models: list[str] | None = None, *, bootstrap_draws: int = BOOTSTRAP_DRAWS) -> CategoryRanking:
    """Rank the operator policies of one category on its common complete cohort (plan Section 1)."""
    models = models or data.models
    prompts = data.prompts_in_category(category)
    eligible = {p: [op for op in data.operators if data.eligibility(p, op, budget)[0] == ELIGIBLE] for p in prompts}
    eligible_before = {op: sum(op in eligible[p] for p in prompts) for op in data.operators}

    complete: list[str] = []
    exclusions: list[dict[str, str]] = []
    measurements: dict[tuple[str, str, str], Measurement] = {}
    for prompt in prompts:
        problems = []
        for model in models:
            controls, status = data.control_state(prompt, model)
            if controls is None:
                problems.append(f"{model_label(model)}: {status}")
                continue
            for op in eligible[prompt]:
                m = measure(data, prompt, model, op)
                measurements[(prompt, model, op)] = m
                if m.status != MEASURED:
                    problems.append(f"{model_label(model)} / {op}: {m.status}")
        if problems:
            exclusions.append({"category": category, "budget": budget_label(budget), "prompt_id": prompt,
                               "reason": "; ".join(problems)})
        else:
            complete.append(prompt)

    scores = {op: {p: 0.0 for p in complete} for op in data.operators}
    observations: list[Measurement] = []
    for prompt in complete:
        for op in eligible[prompt]:
            effects = [measurements[(prompt, model, op)].excess for model in models]
            scores[op][prompt] = mean(effects)
            observations.extend(measurements[(prompt, model, op)] for model in models)

    rows: list[dict[str, Any]] = []
    if complete:
        category_scores = {op: mean(scores[op].values()) for op in data.operators}
        ranks = _competition_ranks(category_scores)
        order = sorted(data.operators, key=lambda op: (-category_scores[op], op))
        leader = order[0]
        runner_up = order[1] if len(order) > 1 else None
        for op in order:
            supported = [scores[op][p] for p in complete if op in eligible[p]]
            reference = runner_up if op == leader else leader
            if reference is None:
                gap = low = high = shared_gap = None
                shared_n = 0
            else:
                first, second = (op, reference) if op == leader else (leader, op)
                gaps = [scores[first][p] - scores[second][p] for p in complete]
                gap = mean(gaps)
                low, high = bootstrap_interval(gaps, draws=bootstrap_draws)
                shared = [p for p in complete if first in eligible[p] and second in eligible[p]]
                shared_n = len(shared)
                shared_gap = mean(scores[first][p] - scores[second][p] for p in shared) if shared else None
            c2i, i2c, n_scorable = _flip_counts(data, [p for p in complete if op in eligible[p]], op, models)
            rows.append({
                "category": category, "budget": budget_label(budget), "operator": op,
                "rank": ranks[op],
                "tied_with": ";".join(o for o in data.operators if o != op and category_scores[o] == category_scores[op]),
                "category_score": category_scores[op],
                "n_prompts": len(prompts), "n_complete_prompts": len(complete),
                "n_eligible_before_exclusions": eligible_before[op],
                "n_eligible_complete": len(supported),
                "conditional_mean": mean(supported) if supported else None,
                "contrast": (f"{leader} - {runner_up}" if op == leader and runner_up else
                             f"{leader} - {op}" if op != leader else ""),
                "paired_gap": gap, "gap_ci_low": low, "gap_ci_high": high,
                "shared_eligible_n": shared_n, "shared_eligible_gap": shared_gap,
                "c2i_flips": c2i, "i2c_flips": i2c, "n_scorable_pairs": n_scorable,
                "n_models": len(models),
                "evidence_status": ("exploratory (discovery data)" if data.evidence_mode == "retrospective"
                                    else "held-out measurement (see validate for the claim rule)"),
                "study_id": data.study_id,
            })

    max_raw = max_excess = []
    if observations:
        top_raw = max(m.raw for m in observations)
        top_excess = max(m.excess for m in observations)
        max_raw = [m for m in observations if m.raw == top_raw]
        max_excess = [m for m in observations if m.excess == top_excess]
    return CategoryRanking(category, budget, list(models), prompts, complete, exclusions, eligible,
                           eligible_before, scores, rows, observations, max_raw, max_excess)


def rank_all(data: StudyData, budgets: Iterable[float | None] = STANDARD_BUDGETS,
             models: list[str] | None = None, *, bootstrap_draws: int = BOOTSTRAP_DRAWS
             ) -> dict[tuple[str, str], CategoryRanking]:
    return {(cat, budget_label(b)): rank_category(data, cat, b, models, bootstrap_draws=bootstrap_draws)
            for b in budgets for cat in data.categories}


# --------------------------------------------------------------------------- prompt-level selection
@dataclass
class OperatorResult:
    operator: str
    eligibility: str
    eligibility_detail: str
    candidate: dict[str, Any] | None
    measurements: list[Measurement]
    status: str
    raw: float | None = None
    control: float | None = None
    excess: float | None = None

    @property
    def char_edits(self) -> int | None:
        if not self.candidate or "input_distances" not in self.candidate:
            return None
        return int(self.candidate["input_distances"]["char_levenshtein"])

    @property
    def d_in_char(self) -> float | None:
        if not self.candidate or "input_distances" not in self.candidate:
            return None
        return float(self.candidate["input_distances"]["char_levenshtein_normalized"])

    @property
    def d_in_sem(self) -> float | None:
        if not self.candidate or "input_distances" not in self.candidate:
            return None
        return _float_or_none(self.candidate["input_distances"].get("semantic_cosine_distance"))


@dataclass
class PromptSelection:
    prompt_id: str
    category: str
    original_prompt: str | None
    expected_answer: str | None
    budget: float | None
    target: float | None
    models: list[str]
    mode: str
    status: str
    winners: list[str]
    tie_status: str
    operators: list[OperatorResult]
    pareto: list[str]
    recommendation: dict[str, Any]
    explanation: str
    provisional_best: list[str] = field(default_factory=list)
    best_achieved: float | None = None
    study_id: str = ""
    evidence_mode: str = "retrospective"

    @property
    def chosen(self) -> OperatorResult | None:
        return self.result(self.winners[0]) if self.winners else None

    def result(self, operator: str) -> OperatorResult | None:
        return next((r for r in self.operators if r.operator == operator), None)

    @property
    def scope_label(self) -> str:
        if len(self.models) == 1:
            return f"{model_label(self.models[0])} (single model)"
        return f"fixed panel of {len(self.models)} models, equal weights"


def _break_ties(candidates: list[OperatorResult], *, prefer_larger_excess: bool = False
                ) -> tuple[list[OperatorResult], str]:
    """Fewest character edits, then smallest normalised input distance (then larger effect in target mode)."""
    if len(candidates) == 1:
        return candidates, "unique"
    fewest = min(c.char_edits for c in candidates)
    stage = [c for c in candidates if c.char_edits == fewest]
    if len(stage) == 1:
        return stage, "tie_broken_by_char_edits"
    smallest = min(c.d_in_char for c in stage)
    stage = [c for c in stage if c.d_in_char == smallest]
    if len(stage) == 1:
        return stage, "tie_broken_by_input_distance"
    if prefer_larger_excess:
        best = max(c.excess for c in stage)
        stage = [c for c in stage if c.excess == best]
        if len(stage) == 1:
            return stage, "tie_broken_by_larger_effect"
    return sorted(stage, key=lambda c: c.operator), "unresolved_tie"


def pareto_frontier(results: list[OperatorResult]) -> list[str]:
    """Edits not dominated on (fewer-or-equal character edits, larger-or-equal excess, one strict)."""
    frontier = []
    for r in results:
        dominated = any(
            o is not r and o.char_edits <= r.char_edits and o.excess >= r.excess
            and (o.char_edits < r.char_edits or o.excess > r.excess)
            for o in results)
        if not dominated:
            frontier.append(r)
    return [r.operator for r in sorted(frontier, key=lambda r: (r.char_edits, -r.excess, r.operator))]


def category_recommendation(category: str, budget: float | None,
                            rankings: dict[tuple[str, str], CategoryRanking] | None,
                            *, measured_prompt: bool, validated: dict[str, str] | None = None) -> dict[str, Any]:
    """Stage 2: the category's recommended operator for this budget, with source and evidence status."""
    label = budget_label(budget)
    source_budget = label
    note = ""
    ranking = rankings.get((category, label)) if rankings else None
    if ranking is None and rankings:
        ranking = rankings.get((category, budget_label(DEFAULT_BUDGET)))
        source_budget = budget_label(DEFAULT_BUDGET)
        note = (f"No category ranking exists for budget {label}; the {source_budget} leader is a starting "
                "candidate and the actual budget filters the generated edits.")
    if ranking is None or not ranking.rows:
        return {"operators": [], "source": "no category ranking available", "budget": label,
                "evidence_status": "unavailable", "note": note, "rationale": ""}
    leaders = ranking.leaders
    status = f"exploratory ({ranking.rows[0]['study_id']} discovery ranking)"
    if validated and validated.get(category) in leaders:
        status = "validated on held-out prompts"
    row = next(r for r in ranking.rows if r["operator"] == leaders[0])
    rationale = CATEGORY_RATIONALE.get((category, leaders[0]),
                                       f"{leaders[0]} {OPERATOR_DESCRIPTIONS.get(leaders[0], '')}.")
    return {
        "operators": leaders, "source": f"category_operator_rankings.csv ({category}, budget {source_budget})",
        "budget": source_budget, "category_score": row["category_score"],
        "coverage": f"{row['n_eligible_complete']}/{row['n_complete_prompts']} complete prompts",
        "evidence_status": status, "rationale": rationale, "note": note,
        "prompt_status": "measured" if measured_prompt else "unmeasured until this prompt is run",
    }


def select_for_prompt(data: StudyData, prompt_id: str, *, budget: float | None = DEFAULT_BUDGET,
                      target: float | None = None, models: list[str] | None = None,
                      rankings: dict[tuple[str, str], CategoryRanking] | None = None,
                      validated: dict[str, str] | None = None) -> PromptSelection:
    """Stages 3-6 for one stored prompt: eligibility, matched measurement, selection, explanation."""
    if prompt_id not in data.prompts:
        raise KeyError(f"{prompt_id} is not a selected prompt of study {data.study_id}")
    models = models or data.models
    info = data.prompts[prompt_id]
    category = info["category"]
    results: list[OperatorResult] = []
    for op in data.operators:
        status, detail = data.eligibility(prompt_id, op, budget)
        cand = data.candidates.get((prompt_id, op))
        if status != ELIGIBLE:
            results.append(OperatorResult(op, status, detail, cand, [], status))
            continue
        ms = [measure(data, prompt_id, model, op) for model in models]
        if all(m.status == MEASURED for m in ms):
            results.append(OperatorResult(op, status, detail, cand, ms, MEASURED,
                                          raw=mean(m.raw for m in ms), control=mean(m.control_mean for m in ms),
                                          excess=mean(m.excess for m in ms)))
        else:
            missing = "; ".join(f"{model_label(m.model)}: {m.status}" for m in ms if m.status != MEASURED)
            results.append(OperatorResult(op, status, detail, cand, ms, "incomplete (" + missing + ")"))

    eligible = [r for r in results if r.eligibility == ELIGIBLE]
    measured = [r for r in eligible if r.status == MEASURED]
    incomplete = [r for r in eligible if r.status != MEASURED]
    mode = "target" if target is not None else "budget"
    recommendation = category_recommendation(category, budget, rankings, measured_prompt=True, validated=validated)
    winners: list[str] = []
    tie_status = ""
    provisional: list[str] = []
    best_achieved = max((r.excess for r in measured), default=None)
    pareto = pareto_frontier(measured) if measured else []

    if not eligible:
        status = "no_eligible_edit"
        explanation = ("No candidate is eligible: every operator was inapplicable, over the budget, or failed "
                       "the preservation screen. The unchanged prompt is the only policy.")
    elif incomplete:
        status = "incomplete"
        if measured:
            top = max(r.excess for r in measured)
            provisional = [r.operator for r in measured if r.excess == top]
        explanation = (f"{len(incomplete)} eligible operator(s) lack complete matched measurements "
                       f"({', '.join(r.operator for r in incomplete)}), so no maximum is claimed. "
                       + (f"Among the {len(measured)} fully measured edits the largest excess is "
                          f"{best_achieved:+.4f} ({', '.join(provisional)}), which is provisional."
                          if measured else "No eligible edit is fully measured."))
    elif mode == "budget":
        top = max(r.excess for r in measured)
        tied = [r for r in measured if r.excess == top]
        kept, tie_status = _break_ties(tied)
        winners = [r.operator for r in kept]
        status = "selected"
        chosen = kept[0]
        others = sorted((r for r in measured if r.operator not in winners), key=lambda r: -r.excess)
        runner = (f" The next best eligible edit was {others[0].operator} ({others[0].excess:+.4f})."
                  if others else " It was the only eligible measured edit.")
        tie_text = {"unique": "", "tie_broken_by_char_edits": " Exact score tie broken by fewer character edits.",
                    "tie_broken_by_input_distance": " Exact score tie broken by smaller normalised input distance.",
                    "unresolved_tie": f" Exact tie retained: {', '.join(winners)} are indistinguishable on score, "
                                      "character edits and input distance."}[tie_status]
        explanation = (f"{chosen.operator} produced the largest control-adjusted change ({chosen.excess:+.4f}) "
                       f"among {len(measured)} eligible, measured edits within budget {budget_label(budget)}."
                       f"{runner}{tie_text} Preservation evidence: {chosen.eligibility_detail}.")
    else:
        reaching = [r for r in measured if r.excess >= target]
        if not reaching:
            status = "target_not_met"
            explanation = (f"No eligible edit reached the target excess of {target:.4f}; the largest measured "
                           f"excess was {best_achieved:+.4f}.")
            provisional = [r.operator for r in measured if r.excess == best_achieved]
        else:
            kept, tie_status = _break_ties(reaching, prefer_larger_excess=True)
            winners = [r.operator for r in kept]
            status = "selected"
            chosen = kept[0]
            explanation = (f"{chosen.operator} is the smallest eligible edit ({chosen.char_edits} character "
                           f"edit(s), d_in_char {chosen.d_in_char:.4f}) whose control-adjusted change "
                           f"({chosen.excess:+.4f}) reaches the target {target:.4f}; {len(reaching)} of "
                           f"{len(measured)} measured edits reached it. Preservation evidence: "
                           f"{chosen.eligibility_detail}.")
    return PromptSelection(prompt_id, category, info.get("original_prompt"), info.get("expected_answer"),
                           budget, target, list(models), mode, status, winners, tie_status, results, pareto,
                           recommendation, explanation, provisional, best_achieved, data.study_id,
                           data.evidence_mode)


# --------------------------------------------------------------------------- protected content screen
_LOGIC_WORDS = {"true", "false", "not", "no", "never", "valid", "invalid", "all", "some", "none", "every",
                "only", "if", "then", "and", "or", "cannot", "can't", "before", "after", "more", "less"}


def protected_content_changes(original: str, perturbed: str) -> list[str]:
    """Automatic screen for edits that touch protected content (plan Stage 3).

    A non-empty result marks a candidate as likely meaning-changing. An empty result is not proof
    of preservation: reviewers still issue the final verdict.
    """
    changes: list[str] = []

    def multiset(pattern: str, text: str, flags: int = 0) -> Counter:
        return Counter(re.findall(pattern, text, flags))

    def squash(text: str) -> str:
        return re.sub(r"\s+", " ", text).strip()

    number = r"(?<![A-Za-z0-9_.])\d+(?:\.\d+)?%?(?![A-Za-z_])"  # standalone quantities, not typo digits
    numbers_o, numbers_p = multiset(number, original), multiset(number, perturbed)
    if numbers_o != numbers_p:
        changes.append(f"quantities changed: {sorted((numbers_o - numbers_p).elements())} -> "
                       f"{sorted((numbers_p - numbers_o).elements())}")
    quote = r"'([^']{3,})'|\"([^\"]{3,})\""
    quotes_o = [squash(a or b) for a, b in re.findall(quote, original)]
    quotes_p = [squash(a or b) for a, b in re.findall(quote, perturbed)]
    if quotes_o != quotes_p:
        changes.append("quoted text changed")
    options_o = [squash(o) for o in re.findall(r"\[[^\]]*\]", original)]
    options_p = [squash(o) for o in re.findall(r"\[[^\]]*\]", perturbed)]
    if options_o != options_p:
        changes.append("bracketed option list or type changed")
    for name in set(re.findall(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\(", original)):
        if not re.search(rf"\b{re.escape(name)}\s*\(", perturbed):
            changes.append(f"code identifier '{name}' no longer present")
    words_o = Counter(w for w in re.findall(r"[a-z']+", original.lower()) if w in _LOGIC_WORDS)
    words_p = Counter(w for w in re.findall(r"[a-z']+", perturbed.lower()) if w in _LOGIC_WORDS)
    if words_o != words_p:
        changes.append(f"logical/negation words changed: {dict(words_o - words_p)} -> {dict(words_p - words_o)}")
    words_o_all = Counter(re.findall(r"[a-z0-9_]+", original.lower()))
    words_p_all = Counter(re.findall(r"[a-z0-9_]+", perturbed.lower()))
    perturbed_tokens = Counter(re.findall(r"\b[A-Z]\b", perturbed))
    entities, variables = set(), Counter()
    for match in re.finditer(r"\b([A-Z][a-z]*)\b", original):
        before = original[:match.start()].rstrip()
        if not before or before[-1] in ".!?:'\"":
            continue  # a capitalised word that only ever starts a sentence is not treated as a name
        token = match.group(1)
        if len(token) == 1:
            variables[token] += 1
        else:
            entities.add(token)
    for name in sorted(entities):
        # Count every occurrence (sentence-initial ones too), case-insensitively, so re-casing is harmless.
        if words_p_all[name.lower()] < words_o_all[name.lower()]:
            changes.append(f"named entity '{name}' removed or altered")
    for var, count in sorted(variables.items()):
        if perturbed_tokens[var] < count:
            changes.append(f"variable '{var}' removed or altered")
    # Mathematical operators only (between operands or spaces), so a typo such as "+ext" is not counted.
    operator_symbol = r"(?:(?<=[\s\d(A-Za-z_])|^)([=<>^+\-*/%])(?=[\s\d(]|$)"
    symbols_o, symbols_p = multiset(operator_symbol, original), multiset(operator_symbol, perturbed)
    if symbols_o != symbols_p:
        changes.append(f"operator symbols changed: {dict(symbols_o - symbols_p)} -> {dict(symbols_p - symbols_o)}")
    return changes


# --------------------------------------------------------------------------- held-out claim rule
def held_out_validation(data: StudyData, nominees: dict[str, str], *, budget: float | None = DEFAULT_BUDGET,
                        alpha: float = VALIDATION_ALPHA, margin: float = 0.0,
                        discovery: StudyData | None = None) -> dict[str, Any]:
    """Plan Section 4: Bonferroni-adjusted one-sided paired t lower bounds for each locked nominee."""
    from scipy import stats

    overlap: list[str] = []
    if discovery is not None:
        if discovery.study_dir == data.study_dir:
            raise DataIntegrityError("The validation study must be different from the discovery study")
        disc_ids = set(discovery.prompt_ids)
        disc_text = {_norm_text(v["original_prompt"]) for v in discovery.prompts.values() if v["original_prompt"]}
        for pid in data.prompt_ids:
            text = data.prompts[pid]["original_prompt"]
            if pid in disc_ids or (text and _norm_text(text) in disc_text):
                overlap.append(pid)
        if overlap:
            raise DataIntegrityError(f"Validation prompts overlap the discovery set: {overlap}")
    categories = [c for c in data.categories if c in nominees]
    contrasts_per_category = len(data.operators)  # (operators - nominee) + the unchanged reference
    family = max(1, contrasts_per_category * len(categories))
    rows, decisions = [], {}
    for category in categories:
        nominee = nominees[category]
        if nominee not in data.operators:
            raise ValueError(f"Nominee {nominee!r} for {category} is not a registered operator")
        ranking = rank_category(data, category, budget)
        n = len(ranking.complete)
        lowers = []
        for alt in [op for op in data.operators if op != nominee] + ["unchanged"]:
            gaps = [ranking.scores[nominee][p] - (0.0 if alt == "unchanged" else ranking.scores[alt][p])
                    for p in ranking.complete]
            row: dict[str, Any] = {"category": category, "nominee": nominee, "alternative": alt,
                                   "n_prompts": n, "family_size": family, "margin": margin}
            if n < 2:
                row.update(mean_gap=mean(gaps) if gaps else None, sd_gap=None, lower_bound=None,
                           ci_low=None, ci_high=None, note="fewer than 2 complete prompts")
                lowers.append(None)
            else:
                sd = stdev(gaps)
                gap = mean(gaps)
                low, high = bootstrap_interval(gaps)
                if sd == 0:
                    note = ("identically zero by design" if all(g == 0 for g in gaps)
                            else "zero variance: conservative unresolved")
                    bound = gap if all(g == 0 for g in gaps) else None
                else:
                    quantile = stats.t.ppf(1 - alpha / family, n - 1)
                    bound = gap - quantile * sd / math.sqrt(n)
                    note = ""
                row.update(mean_gap=gap, sd_gap=sd, lower_bound=bound, ci_low=low, ci_high=high, note=note)
                lowers.append(bound)
            rows.append(row)
        validated = all(b is not None and b > margin for b in lowers)
        leader = ranking.leaders
        decisions[category] = {
            "nominee": nominee, "validated": validated, "n_complete_prompts": n,
            "held_out_leader": leader,
            "status": ("validated winner" if validated else
                       "unresolved: at least one adjusted lower bound is not above the margin"),
            "unresolved_rivals": [r["alternative"] for r in rows if r["category"] == category
                                  and (r["lower_bound"] is None or r["lower_bound"] <= margin)],
        }
    return {"family_size": family, "alpha": alpha, "margin": margin, "budget": budget_label(budget),
            "contrasts": rows, "decisions": decisions, "overlap_checked": discovery is not None,
            "verdict_agreement": data.verdict_agreement}


def _norm_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())
