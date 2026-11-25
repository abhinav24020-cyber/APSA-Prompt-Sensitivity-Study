"""APSA main live study runner (anchor / control / treatment design).

For every (model, prompt):
  * ``anchor``    - the original prompt, generated once;
  * ``control``   - the original prompt re-generated ``control_repetitions`` times;
  * ``treatment`` - each applicable perturbed prompt, generated once.

Analysis pairs every control and treatment generation with the anchor of the same
(model, prompt). Raw generations are appended to per-model JSONL files and never
rewritten; a re-run with ``--resume`` skips generations that already exist.

Rate limits: a per-minute (or unspecified) HTTP 429 is waited out using the provider's
suggested delay; a wait longer than ``--max-wait-seconds`` (typically a daily quota)
stops only that model and is recorded in its failure log.

Usage (PowerShell):
  .\\.venv\\Scripts\\python.exe experiments\\run_study.py --config config\\experiments\\main_study.yaml --study-id main_v1
  .\\.venv\\Scripts\\python.exe experiments\\run_study.py --config ... --study-id demo --mock
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import logging
import platform
import random
import re
import sys
import threading
import time
import uuid
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from apsa.llm_providers import LLMProviderFactory, MockProvider  # noqa: E402
from apsa.llm_providers.base import load_env_file  # noqa: E402
from apsa.llm_providers.exceptions import RateLimitError  # noqa: E402
from apsa.metrics.input_distance import LexicalDistanceCalculator  # noqa: E402
from apsa.perturbations import get_perturbation  # noqa: E402
from apsa.perturbations.base_perturbation import PerturbationConfig  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("apsa.study")

SCORABLE_METRICS = {"exact_match", "code_execution"}


def slug(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", text)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def select_prompts(rows: list[dict[str, str]], per_category: int, rule: str) -> list[dict[str, str]]:
    """Select prompts per category and interleave categories round-robin."""
    by_category: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_category[row["task_category"]].append(row)
    chosen: dict[str, list[dict[str, str]]] = {}
    for category, items in by_category.items():
        if rule == "scorable_first_file_order":
            scorable = [
                r for r in items
                if json.loads(r.get("metadata") or "{}").get("eval_metric") in SCORABLE_METRICS
            ]
            rest = [r for r in items if r not in scorable]
            items = scorable + rest
        elif rule != "file_order":
            raise ValueError(f"Unknown selection rule: {rule}")
        chosen[category] = items[:per_category]
    interleaved = []
    for i in range(per_category):
        for category in sorted(chosen):
            if i < len(chosen[category]):
                interleaved.append(chosen[category][i])
    return interleaved


def build_candidates(
    prompts: list[dict[str, str]],
    operators: list[str],
    seed: int,
    semantic_calc,
) -> list[dict[str, Any]]:
    """Generate every perturbation candidate, keeping skipped ones with a reason."""
    lex = LexicalDistanceCalculator()
    candidates = []
    for row in prompts:
        original = row["original_prompt"]
        for op in operators:
            base = {
                "prompt_id": row["prompt_id"],
                "task_category": row["task_category"],
                "operator": op,
                "seed": seed,
            }
            params: dict[str, Any] = {}
            if op == "punctuation":
                params = {
                    "mode": "remove_trailing_period"
                    if original.rstrip().endswith((".", "!", "?"))
                    else "add_trailing_period"
                }
            try:
                record = get_perturbation(op).perturb(
                    original, prompt_id=row["prompt_id"],
                    config=PerturbationConfig(params=params, seed=seed),
                )
            except Exception as error:  # noqa: BLE001
                candidates.append({**base, "status": "rejected", "reason": f"error: {error}"})
                continue
            if record is None or record.perturbed_prompt == original:
                candidates.append({**base, "status": "rejected", "reason": "inapplicable_or_no_op"})
                continue
            lex_res = lex.compute(original, record.perturbed_prompt)
            sem = semantic_calc.compute(original, record.perturbed_prompt)
            candidates.append({
                **base,
                "status": "accepted",
                "reason": None,
                "perturbation_id": record.perturbation_id,
                "params": params,
                "perturbed_prompt": record.perturbed_prompt,
                "perturbation_metadata": record.metadata,
                "semantic_risk_level": record.semantic_risk_level.value,
                "semantic_risk_reasons": record.semantic_risk_reasons,
                "input_distances": {
                    "char_levenshtein": lex_res.char_levenshtein,
                    "char_levenshtein_normalized": lex_res.char_levenshtein_normalized,
                    "word_levenshtein": lex_res.word_levenshtein,
                    "pct_prompt_changed": lex_res.pct_prompt_changed,
                    "semantic_cosine_distance": sem.cosine_distance,
                    "semantic_embedding_model": sem.embedding_model,
                },
            })
    return candidates


class ModelWorker(threading.Thread):
    def __init__(self, *, study_dir: Path, study_id: str, model_cfg: dict[str, Any],
                 provider, generation: dict[str, Any], system_prompt: str,
                 prompts: list[dict[str, str]], candidates: list[dict[str, Any]],
                 control_repetitions: int, max_wait: float, is_mock: bool,
                 max_calls: int | None, treatment_allowed=None, shuffle_seed: int | None = None):
        super().__init__(name=model_cfg["name"], daemon=True)
        self.treatment_allowed = treatment_allowed
        self.shuffle_seed = shuffle_seed
        self.study_dir = study_dir
        self.study_id = study_id
        self.cfg = model_cfg
        self.provider = provider
        self.system_prompt = system_prompt
        self.prompts = prompts
        self.candidates = candidates
        self.control_repetitions = control_repetitions
        self.max_wait = max_wait
        self.is_mock = is_mock
        self.max_calls = max_calls
        self.min_interval = float(model_cfg.get("min_request_interval", 0) or 0)
        self.request_config = {
            **generation,
            **{k: model_cfg[k] for k in ("temperature", "max_tokens", "top_p", "seed",
                                        "reasoning_effort") if k in model_cfg},
            "system_prompt": system_prompt,
        }
        name = slug(model_cfg["name"])
        self.gen_path = study_dir / "raw" / f"generations__{name}.jsonl"
        self.fail_path = study_dir / "raw" / f"failures__{name}.jsonl"
        self.done = self._load_done()
        self.status = "pending"
        self.calls = 0
        self.successes = 0
        self.failures = 0
        self._last_call = 0.0

    def _load_done(self) -> set[tuple]:
        done = set()
        if self.gen_path.exists():
            for line in self.gen_path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    r = json.loads(line)
                    done.add((r["prompt_id"], r["condition"], r.get("operator"), r["repetition"]))
        return done

    def _jobs(self):
        cands = defaultdict(list)
        for c in self.candidates:
            if c["status"] == "accepted" and (self.treatment_allowed is None or self.treatment_allowed(c)):
                cands[c["prompt_id"]].append(c)
        for row in self.prompts:
            yield row, "anchor", None, 1, row["original_prompt"], None
            block = [(row, "control", None, rep, row["original_prompt"], None)
                     for rep in range(1, self.control_repetitions + 1)]
            block += [(row, "treatment", c["operator"], 1, c["perturbed_prompt"], c) for c in cands[row["prompt_id"]]]
            if self.shuffle_seed is not None:
                # Recorded, per-model and per-prompt order of repeats and treatments (plan Section 4, step 3).
                random.Random(f"{self.shuffle_seed}:{self.cfg['name']}:{row['prompt_id']}").shuffle(block)
            yield from block

    def _generate(self, text: str):
        attempts = 0
        while True:
            if self.min_interval and not self.is_mock:
                wait = self.min_interval - (time.time() - self._last_call)
                if wait > 0:
                    time.sleep(wait)
            self._last_call = time.time()
            self.calls += 1
            try:
                return self.provider.generate(text, self.request_config)
            except RateLimitError as error:
                attempts += 1
                wait = error.retry_after if error.retry_after is not None else 30.0
                wait = max(2.0, wait + 1.0)
                if wait > self.max_wait or attempts > 40:
                    raise
                logger.info("[%s] 429 (%s limit); waiting %.1fs", self.name,
                            error.scope or "unspecified", wait)
                time.sleep(wait)

    def run(self) -> None:
        self.status = "running"
        consecutive_failures = 0
        with self.gen_path.open("a", encoding="utf-8") as gen_f, \
                self.fail_path.open("a", encoding="utf-8") as fail_f:
            for row, condition, operator, rep, text, cand in self._jobs():
                key = (row["prompt_id"], condition, operator, rep)
                if key in self.done:
                    continue
                if self.max_calls is not None and self.successes >= self.max_calls:
                    self.status = "stopped_max_calls"
                    return
                base = {
                    "study_id": self.study_id,
                    "model": self.cfg["name"],
                    "provider": self.cfg["provider"],
                    "execution_mode": "mock" if self.is_mock else "live",
                    "prompt_id": row["prompt_id"],
                    "task_category": row["task_category"],
                    "condition": condition,
                    "operator": operator,
                    "repetition": rep,
                    "perturbation_id": cand["perturbation_id"] if cand else None,
                    "prompt_text": text,
                }
                try:
                    result = self._generate(text)
                except RateLimitError as error:
                    self.failures += 1
                    fail_f.write(json.dumps({
                        **base, "status": "failed", "error_type": "RateLimitError",
                        "rate_limit_scope": error.scope, "retry_after_seconds": error.retry_after,
                        "error": str(error)[:1000], "timestamp": datetime.now(UTC).isoformat(),
                        "model_stopped": True,
                    }) + "\n")
                    fail_f.flush()
                    self.status = "stopped_quota"
                    logger.warning("[%s] stopping: rate limit wait exceeds budget (%s)",
                                   self.name, error.retry_after)
                    return
                except Exception as error:  # noqa: BLE001 - record and continue
                    self.failures += 1
                    consecutive_failures += 1
                    fail_f.write(json.dumps({
                        **base, "status": "failed", "error_type": type(error).__name__,
                        "error": str(error)[:1000], "timestamp": datetime.now(UTC).isoformat(),
                        "model_stopped": consecutive_failures >= 8,
                    }) + "\n")
                    fail_f.flush()
                    if consecutive_failures >= 8:
                        self.status = "stopped_errors"
                        logger.error("[%s] stopping after repeated errors: %s", self.name, error)
                        return
                    continue
                consecutive_failures = 0
                self.successes += 1
                gen_f.write(json.dumps({
                    **base,
                    "record_id": str(uuid.uuid4()),
                    "status": "success",
                    "output": result.output,
                    "finish_reason": result.finish_reason,
                    "input_tokens": result.input_tokens,
                    "output_tokens": result.output_tokens,
                    "latency_seconds": round(result.latency, 4),
                    "timestamp": datetime.now(UTC).isoformat(),
                    "request_config": {k: v for k, v in self.request_config.items()
                                       if k != "system_prompt"},
                }) + "\n")
                gen_f.flush()
                self.done.add(key)
                if self.successes % 25 == 0:
                    logger.info("[%s] %d generations recorded", self.name, self.successes)
        self.status = "completed"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--config", default="config/experiments/main_study.yaml")
    parser.add_argument("--study-id", required=True)
    parser.add_argument("--output-root", default="results/study")
    parser.add_argument("--models", nargs="+", default=None, help="Subset of model names")
    parser.add_argument("--prompts-per-category", type=int, default=None)
    parser.add_argument("--mock", action="store_true", help="Offline mock provider (no API calls)")
    parser.add_argument("--max-wait-seconds", type=float, default=900.0)
    parser.add_argument("--max-calls-per-model", type=int, default=None)
    parser.add_argument("--dataset", default=None, help="Override the config's dataset CSV")
    parser.add_argument("--prompt-ids", nargs="+", default=None,
                        help="Explicit prompt allowlist (IDs, or @file with one ID per line); bypasses the "
                             "selection rule so validation runs cannot reselect discovery prompts")
    parser.add_argument("--verdicts", default=None,
                        help="CSV of final preservation verdicts; only 'preserved' candidates are generated")
    parser.add_argument("--max-input-distance", type=float, default=None,
                        help="Skip treatments whose normalised character distance exceeds this budget")
    parser.add_argument("--shuffle-seed", type=int, default=None,
                        help="Randomise the order of repeats and treatments within each prompt block")
    args = parser.parse_args()

    cfg = yaml.safe_load((ROOT / args.config).read_text(encoding="utf-8"))
    if args.dataset:
        cfg["dataset"] = args.dataset
    load_env_file()
    study_dir = ROOT / args.output_root / args.study_id
    (study_dir / "raw").mkdir(parents=True, exist_ok=True)

    dataset_path = ROOT / cfg["dataset"]
    rows = list(csv.DictReader(dataset_path.open(encoding="utf-8")))
    if args.prompt_ids:
        wanted: list[str] = []
        for item in args.prompt_ids:
            if item.startswith("@"):
                wanted += [l.strip() for l in (ROOT / item[1:]).read_text(encoding="utf-8").splitlines() if l.strip()]
            else:
                wanted += [p.strip() for p in item.split(",") if p.strip()]
        by_id = {r["prompt_id"]: r for r in rows}
        unknown = [p for p in wanted if p not in by_id]
        if unknown:
            raise SystemExit(f"Unknown prompt IDs in --prompt-ids: {unknown}")
        prompts = [by_id[p] for p in wanted]
        cfg["selection_rule"] = "explicit_allowlist"
    else:
        per_cat = args.prompts_per_category or cfg["prompts_per_category"]
        prompts = select_prompts(rows, per_cat, cfg["selection_rule"])

    preserved = None
    vrows = []
    if args.verdicts:
        with (ROOT / args.verdicts).open(encoding="utf-8-sig", newline="") as handle:
            vrows = list(csv.DictReader(handle))
        col = "final_verdict" if vrows and "final_verdict" in vrows[0] else "verdict"
        preserved = {(r["prompt_id"], r["operator"]) for r in vrows if (r.get(col) or "").strip().lower() == "preserved"}

    def treatment_allowed(c: dict[str, Any]) -> bool:
        if preserved is not None and (c["prompt_id"], c["operator"]) not in preserved:
            return False
        if args.max_input_distance is not None:
            return c["input_distances"]["char_levenshtein_normalized"] <= args.max_input_distance
        return True

    candidates_path = study_dir / "candidates.jsonl"
    if candidates_path.exists():
        candidates = [json.loads(l) for l in candidates_path.read_text(encoding="utf-8").splitlines() if l]
        logger.info("Loaded %d existing candidates", len(candidates))
    else:
        from apsa.metrics.input_distance.semantic import (
            SemanticDistanceCalculator,
            SentenceTransformerEmbedder,
        )
        semantic = SemanticDistanceCalculator(SentenceTransformerEmbedder(model_name=cfg["semantic_model"]))
        candidates = build_candidates(prompts, cfg["operators"], cfg["perturbation_seed"], semantic)
        with candidates_path.open("w", encoding="utf-8") as f:
            for c in candidates:
                f.write(json.dumps(c) + "\n")
    accepted = sum(c["status"] == "accepted" for c in candidates)
    if vrows:
        by_candidate = {(c["prompt_id"], c["operator"]): c for c in candidates if c["status"] == "accepted"}
        selected_ids = {p["prompt_id"] for p in prompts}
        for verdict in vrows:
            key = (verdict["prompt_id"], verdict["operator"])
            if key not in preserved or key[0] not in selected_ids:
                continue
            candidate = by_candidate.get(key)
            if candidate is None or any(verdict.get(field) and verdict[field] != candidate.get(field)
                                        for field in ("perturbation_id", "perturbed_prompt")):
                raise SystemExit(f"Preservation verdict does not match the generated candidate: {key[0]}/{key[1]}")
    logger.info("%d prompts, %d candidates (%d accepted)", len(prompts), len(candidates), accepted)

    models = cfg["models"]
    if args.models:
        models = [m for m in models if m["name"] in args.models]
    workers = []
    for m in models:
        provider = MockProvider(m["name"]) if args.mock else LLMProviderFactory.create(m["provider"], m["name"])
        workers.append(ModelWorker(
            study_dir=study_dir, study_id=args.study_id, model_cfg=m, provider=provider,
            generation=cfg["generation"], system_prompt=cfg["system_prompt"], prompts=prompts,
            candidates=candidates, control_repetitions=cfg["control_repetitions"],
            max_wait=args.max_wait_seconds, is_mock=args.mock,
            max_calls=args.max_calls_per_model,
            treatment_allowed=treatment_allowed if (preserved is not None or args.max_input_distance is not None) else None,
            shuffle_seed=args.shuffle_seed,
        ))

    manifest_path = study_dir / "study_manifest.json"
    runs = []
    if manifest_path.exists():
        runs = json.loads(manifest_path.read_text(encoding="utf-8")).get("runs", [])
    run_entry = {
        "run_started_at": datetime.now(UTC).isoformat(),
        "execution_mode": "mock" if args.mock else "live",
        "models": [m["name"] for m in models],
        "python_version": platform.python_version(),
        "platform": platform.platform(),
    }
    manifest = {
        "study_id": args.study_id,
        "config_path": args.config,
        "config_sha256": sha256_file(ROOT / args.config),
        "config": cfg,
        "dataset_path": cfg["dataset"],
        "dataset_sha256": sha256_file(dataset_path),
        "selected_prompt_ids": [r["prompt_id"] for r in prompts],
        "generation_filters": {"verdicts": args.verdicts, "max_input_distance": args.max_input_distance,
                               "shuffle_seed": args.shuffle_seed, "prompt_allowlist": bool(args.prompt_ids)},
        "candidate_counts": {"total": len(candidates), "accepted": accepted},
        "runs": runs + [run_entry],
    }
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    for w in workers:
        w.start()
    while any(w.is_alive() for w in workers):
        for w in workers:
            w.join(timeout=30 / max(1, len(workers)))
        if not any(w.is_alive() for w in workers):
            break
        logger.info("progress: " + ", ".join(f"{w.name}={w.successes}/{w.status}" for w in workers))
    run_entry.update({
        "run_finished_at": datetime.now(UTC).isoformat(),
        "per_model": {w.name: {"status": w.status, "new_generations": w.successes,
                               "failures": w.failures, "calls_started": w.calls}
                      for w in workers},
    })
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    logger.info("Study artifacts in %s", study_dir)


if __name__ == "__main__":
    main()
