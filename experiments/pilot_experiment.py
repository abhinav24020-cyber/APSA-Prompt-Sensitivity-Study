import argparse
import csv
import hashlib
import json
import logging
import platform
import sys
import time
import uuid
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

from apsa.llm_providers import LLMProviderFactory, MockProvider
from apsa.llm_providers.base import load_env_file
from apsa.llm_providers.exceptions import ConfigurationError, RateLimitError
from apsa.metrics.input_distance import LexicalDistanceCalculator
from apsa.perturbations import get_perturbation
from apsa.perturbations.base_perturbation import PerturbationConfig

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

PERTURBATION_TYPES = [
    "punctuation",
    "word_insertion",
    "word_deletion",
    "word_substitution",
    "instruction_reordering"
]

def load_models_config(config_path: str) -> list[dict[str, Any]]:
    with open(config_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
        return data.get("models", [])

def validate_environment(
    models: list[dict[str, Any]], 
    data_path: Path, 
    use_mock: bool = False,
    allow_partial: bool = True
):
    """Validate APIs, config, dataset, and perturbations before running."""
    logger.info("Validating environment...")
    load_env_file()
    
    # 1. Dataset Integrity
    if not data_path.exists():
        logger.error(f"Dataset not found at {data_path}")
        sys.exit(1)
        
    # 2. Perturbation Integrity
    for p_name in PERTURBATION_TYPES:
        try:
            get_perturbation(p_name)
        except KeyError as e:
            logger.error(f"Perturbation validation failed: {e}")
            sys.exit(1)
            
    # 3. API Availability (Instantiate models to check for credentials)
    providers = []
    skipped_models = []
    for model_cfg in models:
        try:
            if use_mock:
                provider = MockProvider(model_cfg["name"])
            else:
                provider = LLMProviderFactory.create(model_cfg["provider"], model_cfg["name"])
            providers.append((provider, model_cfg))
        except ConfigurationError as e:
            if allow_partial and not use_mock:
                logger.warning(f"Model {model_cfg['name']} skipped (credentials not configured): {e}")
                skipped_models.append(model_cfg["name"])
            else:
                logger.error(f"API validation failed for model {model_cfg['name']}: {e}")
                sys.exit(1)
                
    if not providers:
        logger.error("No LLM models could be validated. Please configure GEMINI_API_KEY and/or GROQ_API_KEY in your .env file.")
        sys.exit(1)
        
    validated_names = [p.model_name for p, _ in providers]
    logger.info(f"Environment validation successful. Active models for pilot ({len(providers)}): {validated_names}")
    return providers

def sample_dataset(data_path: Path, num_categories: int = 5, prompts_per_category: int = 10) -> list[dict[str, str]]:
    if num_categories < 1:
        raise ValueError("num_categories must be at least 1")
    if prompts_per_category < 1:
        raise ValueError("prompts_per_category must be at least 1")

    logger.info("Sampling dataset...")
    categories = defaultdict(list)
    with open(data_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            cat = row.get("task_category", "unknown")
            if len(categories[cat]) < prompts_per_category:
                categories[cat].append(row)
                
    # Filter to requested number of categories
    sampled_prompts = []
    cat_count = 0
    for cat, items in categories.items():
        if len(items) == prompts_per_category:
            sampled_prompts.extend(items)
            cat_count += 1
            if cat_count == num_categories:
                break
                
    if cat_count < num_categories:
        logger.warning(f"Could only find {cat_count} categories with {prompts_per_category} prompts.")
        
    return sampled_prompts

def generate_pilot_report(
    results_dir: Path,
    report_path: Path,
    total_trials: int,
    successful_trials: int,
    failed_trials: int,
    total_llm_calls: int,
    models: list[str],
    num_prompts: int = 50,
    repetitions: int = 3,
    control_repetitions: int = 1,
    is_mock: bool = False,
    interrupted: bool = False,
    inapplicable_counts: dict[str, int] | None = None,
):
    if interrupted:
        status_str = "Interrupted (partial results saved)"
    elif is_mock:
        status_str = "Completed (Mock Validation)"
    else:
        status_str = "Completed" if failed_trials == 0 else "Partially Completed"
    breakdown_str = f"{len(models)} models * {num_prompts} prompts * {len(PERTURBATION_TYPES)} perturbations * {repetitions} repetitions"
    skip_lines = [
        f"- **{operator}**: {count}"
        for operator, count in sorted((inapplicable_counts or {}).items())
    ]
    skip_summary = "\n".join(skip_lines) if skip_lines else "- None"
    report_content = f"""# Pilot Experiment Report

## Overview
- **Status**: {status_str}
- **Maximum Possible Trials (before inapplicable skips)**: {total_trials}
- **Maximum Trial Breakdown**: {breakdown_str} plus {len(models)} models * {num_prompts} prompts * {control_repetitions} control repetitions
- **Generation Calls Started**: {total_llm_calls} (provider-level HTTP retries, if any, are not counted separately)
- **Successful Trials**: {successful_trials}
- **Failed Trials**: {failed_trials}
- **Models Tested**: {', '.join(models)}
- **Perturbations Applied**: {', '.join(PERTURBATION_TYPES)}
- **Execution Mode**: {'Mock Provider (No API charges incurred)' if is_mock else 'Real API Providers'}

## Execution Details
The pilot executes data sampling, perturbation generation, paired model requests, and raw result recording. Failed provider calls and inapplicable perturbations are not successful trials.

## Inapplicable Perturbation Candidates
Counts are candidates skipped because the operator could not modify the prompt; they are not provider failures.

{skip_summary}

## Next Steps
- Compare treatment deviations and correctness changes with the unchanged-prompt controls; interpret these as descriptive results for this run only.
- Review `failed_trials.jsonl` and check provider quota before attempting another live run.
- Expand prompts and models only within an explicitly planned request budget, then conduct independent reference-answer review before confirmatory analysis.
"""
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    logger.info(f"Pilot report generated at {report_path}")


def redact_secrets(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: (
                "[REDACTED]"
                if any(
                    marker in str(key).casefold()
                    for marker in ("api_key", "secret", "password", "access_token")
                )
                else redact_secrets(item)
            )
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [redact_secrets(item) for item in value]
    return value


class _KeyboardInterruptRecorder:
    def __init__(self) -> None:
        self.interrupted = False

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception, traceback) -> bool:
        if exception_type is KeyboardInterrupt:
            self.interrupted = True
            return True
        return False


def run_pilot(
    providers: list[tuple],
    prompts: list[dict[str, str]],
    output_dir: Path,
    repetitions: int = 1,
    is_mock: bool = False,
    control_repetitions: int = 1,
    max_tokens: int | None = None,
    semantic_model: str = "sentence-transformers/all-MiniLM-L6-v2",
    semantic_calculator=None,
    dataset_path: Path | None = None,
) -> Path:
    if repetitions < 1:
        raise ValueError("repetitions must be at least 1")
    if control_repetitions < 1:
        raise ValueError("control_repetitions must be at least 1")
    if max_tokens is not None and max_tokens < 1:
        raise ValueError("max_tokens must be at least 1")

    from apsa.metrics.input_distance.semantic import (
        SemanticDistanceCalculator,
        SentenceTransformerEmbedder,
    )

    semantic_calc = semantic_calculator or SemanticDistanceCalculator(
        SentenceTransformerEmbedder(model_name=semantic_model)
    )

    execution_mode = "mock" if is_mock else "live"
    experiment_id = f"pilot_{execution_mode}_{uuid.uuid4().hex[:8]}"
    run_dir = output_dir / execution_mode / experiment_id
    run_dir.mkdir(parents=True, exist_ok=False)
    results_file = run_dir / "raw_results.jsonl"
    failures_file = run_dir / "failed_trials.jsonl"
    manifest_path = run_dir / "run_manifest.json"
    report_path = run_dir / "pilot_report.md"
    started_at = datetime.now(UTC).isoformat()

    category_counts: dict[str, int] = defaultdict(int)
    for prompt in prompts:
        category_counts[prompt["task_category"]] += 1

    model_runs = []
    for provider, config in providers:
        resolved_config = dict(config)
        if max_tokens is not None:
            resolved_config["max_tokens"] = max_tokens
        generation_config = {
            key: resolved_config[key]
            for key in ("temperature", "top_p", "max_tokens", "seed")
            if key in resolved_config
        }
        model_runs.append((provider, resolved_config, generation_config))

    dataset_hash = None
    if dataset_path is not None:
        digest = hashlib.sha256()
        with dataset_path.open("rb") as dataset_file:
            for chunk in iter(lambda: dataset_file.read(1024 * 1024), b""):
                digest.update(chunk)
        dataset_hash = digest.hexdigest()

    manifest = {
        "experiment_id": experiment_id,
        "status": "running",
        "started_at": started_at,
        "execution_mode": execution_mode,
        "python_version": platform.python_version(),
        "dataset": {
            "path": str(dataset_path.resolve()) if dataset_path else None,
            "sha256": dataset_hash,
            "sampling": "first N rows in file order per category; first five eligible categories",
            "prompt_count": len(prompts),
            "category_counts": dict(category_counts),
            "prompt_ids": [prompt["prompt_id"] for prompt in prompts],
        },
        "generation": {
            "task_repetitions": repetitions,
            "control_repetitions": control_repetitions,
            "temperature": "model-configured",
            "max_tokens_override": max_tokens,
            "semantic_input_model": semantic_calc.embedding_model_name,
        },
        "perturbation_types": list(PERTURBATION_TYPES),
        "models": [
            {
                "provider": config.get("provider"),
                "model": provider.model_name,
                "model_config": redact_secrets(config),
                "generation_config": generation_config,
            }
            for provider, config, generation_config in model_runs
        ],
    }
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    treatment_trial_max = (
        len(model_runs) * len(prompts) * len(PERTURBATION_TYPES) * repetitions
    )
    control_trial_max = len(model_runs) * len(prompts) * control_repetitions
    total_trial_max = treatment_trial_max + control_trial_max
    logger.info("Starting Pilot Experiment: %s", experiment_id)
    logger.info(
        "Maximum pairs before inapplicable candidates: %s treatment + %s control",
        treatment_trial_max,
        control_trial_max,
    )
    logger.info("Maximum generation calls before skips: %s", total_trial_max * 2)

    successful_trials = 0
    failed_trials = 0
    total_generation_calls = 0
    inapplicable_counts: dict[str, int] = defaultdict(int)
    perturbation_instances = {name: get_perturbation(name) for name in PERTURBATION_TYPES}
    lex_calc = LexicalDistanceCalculator()
    semantic_cache: dict[tuple[str, str], Any] = {}

    def write_error(
        stream,
        provider,
        prompt_data: dict[str, str],
        condition: str,
        error: Exception,
        run_number: int,
        *,
        stop_model: bool = False,
        partial_generations: dict[str, Any] | None = None,
    ) -> None:
        def summarize_generation(result):
            if result is None:
                return None
            return {
                "output": result.output,
                "latency": result.latency,
                "input_tokens": result.input_tokens,
                "output_tokens": result.output_tokens,
                "finish_reason": result.finish_reason,
            }

        error_row = {
            "status": "failed",
            "experiment_id": experiment_id,
            "execution_mode": execution_mode,
            "provider": next(
                (cfg.get("provider") for p, cfg, _ in model_runs if p is provider),
                None,
            ),
            "model": provider.model_name,
            "task_category": prompt_data["task_category"],
            "prompt_id": prompt_data["prompt_id"],
            "condition": condition,
            "run_number": run_number,
            "error_type": type(error).__name__,
            "error": str(error),
            "retry_after_seconds": (
                error.retry_after if isinstance(error, RateLimitError) else None
            ),
            "remaining_trials_aborted": stop_model,
            "partial_generations": {
                side: summarize_generation(result)
                for side, result in (partial_generations or {}).items()
            },
        }
        stream.write(json.dumps(error_row) + "\n")
        stream.flush()

    interrupt_recorder = _KeyboardInterruptRecorder()
    with (
        interrupt_recorder,
        results_file.open("w", encoding="utf-8") as out_f,
        failures_file.open("w", encoding="utf-8") as failures_f,
    ):
        for provider, config, generation_config in model_runs:
            logger.info("Running model %s via %s", provider.model_name, config.get("provider"))
            rate_limited = False

            for prompt_data in prompts:
                original_prompt = prompt_data["original_prompt"]
                prompt_id = prompt_data["prompt_id"]
                task_category = prompt_data["task_category"]
                common = {
                    "experiment_id": experiment_id,
                    "execution_mode": execution_mode,
                    "provider": config.get("provider"),
                    "model": provider.model_name,
                    "task_category": task_category,
                    "prompt_id": prompt_id,
                    "expected_answer": prompt_data.get("expected_answer"),
                    "generation_config": generation_config,
                    "max_output_tokens": generation_config.get("max_tokens"),
                }

                for control_num in range(control_repetitions):
                    baseline = None
                    repeated = None
                    try:
                        total_generation_calls += 1
                        baseline = provider.generate(original_prompt, config)
                        if not is_mock:
                            time.sleep(0.5)
                        total_generation_calls += 1
                        repeated = provider.generate(original_prompt, config)
                        row = {
                            **common,
                            "status": "success",
                            "condition": "control",
                            "perturbation_type": "unchanged_prompt_control",
                            "run_number": control_num + 1,
                            "original_prompt": original_prompt,
                            "perturbed_prompt": original_prompt,
                            "original_output": baseline.output,
                            "perturbed_output": repeated.output,
                            "latency": baseline.latency + repeated.latency,
                            "token_counts": {
                                "original_input": baseline.input_tokens,
                                "original_output": baseline.output_tokens,
                                "perturbed_input": repeated.input_tokens,
                                "perturbed_output": repeated.output_tokens,
                            },
                            "finish_reasons": {
                                "original": baseline.finish_reason,
                                "perturbed": repeated.finish_reason,
                            },
                            "input_distances": {
                                "char_levenshtein_normalized": 0.0,
                                "semantic_cosine_distance": 0.0,
                                "semantic_embedding_model": semantic_calc.embedding_model_name,
                            },
                        }
                        out_f.write(json.dumps(row) + "\n")
                        out_f.flush()
                        successful_trials += 1
                        if not is_mock:
                            time.sleep(0.5)
                    except RateLimitError as error:
                        failed_trials += 1
                        rate_limited = True
                        write_error(
                            failures_f, provider, prompt_data, "control", error,
                            control_num + 1, stop_model=True,
                            partial_generations={
                                "original": baseline,
                                "perturbed": repeated,
                            },
                        )
                        break
                    except Exception as error:  # noqa: BLE001 - persist failed control
                        failed_trials += 1
                        write_error(
                            failures_f, provider, prompt_data, "control", error,
                            control_num + 1,
                            partial_generations={
                                "original": baseline,
                                "perturbed": repeated,
                            },
                        )

                if rate_limited:
                    break

                for p_name, pert_instance in perturbation_instances.items():
                    try:
                        pert_config = PerturbationConfig(seed=42)
                        if p_name == "punctuation":
                            mode = (
                                "remove_trailing_period"
                                if original_prompt.rstrip().endswith((".", "!", "?"))
                                else "add_trailing_period"
                            )
                            pert_config = PerturbationConfig(params={"mode": mode}, seed=42)
                        record = pert_instance.perturb(
                            original_prompt, prompt_id=prompt_id, config=pert_config
                        )
                        if record is None:
                            inapplicable_counts[p_name] += 1
                            continue
                        perturbed_prompt = record.perturbed_prompt
                        lex_res = lex_calc.compute(original_prompt, perturbed_prompt)
                        cache_key = (original_prompt, perturbed_prompt)
                        if cache_key not in semantic_cache:
                            semantic_cache[cache_key] = semantic_calc.compute(
                                original_prompt, perturbed_prompt
                            )
                        sem_res = semantic_cache[cache_key]
                        input_distances = {
                            "char_levenshtein": lex_res.char_levenshtein,
                            "char_levenshtein_normalized": lex_res.char_levenshtein_normalized,
                            "word_levenshtein": lex_res.word_levenshtein,
                            "pct_prompt_changed": lex_res.pct_prompt_changed,
                            "semantic_cosine_distance": sem_res.cosine_distance,
                            "semantic_cosine_similarity": sem_res.cosine_similarity,
                            "semantic_embedding_model": sem_res.embedding_model,
                            "semantic_risk_level": record.semantic_risk_level.value,
                        }
                    except Exception as error:  # noqa: BLE001 - log and skip invalid candidate
                        logger.error("Perturbation %s failed on %s: %s", p_name, prompt_id, error)
                        continue

                    for run_num in range(repetitions):
                        baseline = None
                        perturbed = None
                        try:
                            total_generation_calls += 1
                            baseline = provider.generate(original_prompt, config)
                            if not is_mock:
                                time.sleep(0.5)
                            total_generation_calls += 1
                            perturbed = provider.generate(perturbed_prompt, config)
                            row = {
                                **common,
                                "status": "success",
                                "condition": "treatment",
                                "perturbation_type": p_name,
                                "perturbation_id": record.perturbation_id,
                                "perturbation_metadata": record.metadata,
                                "semantic_risk_reasons": record.semantic_risk_reasons,
                                "run_number": run_num + 1,
                                "original_prompt": original_prompt,
                                "perturbed_prompt": perturbed_prompt,
                                "original_output": baseline.output,
                                "perturbed_output": perturbed.output,
                                "latency": baseline.latency + perturbed.latency,
                                "token_counts": {
                                    "original_input": baseline.input_tokens,
                                    "original_output": baseline.output_tokens,
                                    "perturbed_input": perturbed.input_tokens,
                                    "perturbed_output": perturbed.output_tokens,
                                },
                                "finish_reasons": {
                                    "original": baseline.finish_reason,
                                    "perturbed": perturbed.finish_reason,
                                },
                                "input_distances": input_distances,
                            }
                            out_f.write(json.dumps(row) + "\n")
                            out_f.flush()
                            successful_trials += 1
                            if not is_mock:
                                time.sleep(0.5)
                        except RateLimitError as error:
                            logger.warning(
                                "Stopping model %s after a rate limit; completed records "
                                "are preserved and remaining trials were not sent.",
                                provider.model_name,
                            )
                            failed_trials += 1
                            rate_limited = True
                            write_error(
                                failures_f, provider, prompt_data, "treatment", error,
                                run_num + 1, stop_model=True,
                                partial_generations={
                                    "original": baseline,
                                    "perturbed": perturbed,
                                },
                            )
                            break
                        except Exception as error:  # noqa: BLE001 - persist failed treatment
                            logger.error("Generation failed on %s (run %s): %s", prompt_id, run_num + 1, error)
                            failed_trials += 1
                            write_error(
                                failures_f, provider, prompt_data, "treatment", error,
                                run_num + 1,
                                partial_generations={
                                    "original": baseline,
                                    "perturbed": perturbed,
                                },
                            )
                    if rate_limited:
                        break
                if rate_limited:
                    break

    interrupted = interrupt_recorder.interrupted
    manifest.update({
        "status": (
            "interrupted"
            if interrupted
            else "partially_completed" if failed_trials else "completed"
        ),
        "completed_at": datetime.now(UTC).isoformat(),
        "artifacts": {
            "raw_results": results_file.name,
            "failed_trials": failures_file.name,
            "manifest": manifest_path.name,
            "report": report_path.name,
        },
        "counts": {
            "maximum_possible_trials": total_trial_max,
            "successful_trials": successful_trials,
            "failed_trials": failed_trials,
            "generation_calls_started": total_generation_calls,
            "inapplicable_candidates": dict(inapplicable_counts),
        },
    })
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    generate_pilot_report(
        run_dir,
        report_path,
        total_trial_max,
        successful_trials,
        failed_trials,
        total_generation_calls,
        [provider.model_name for provider, _, _ in model_runs],
        num_prompts=len(prompts),
        repetitions=repetitions,
        control_repetitions=control_repetitions,
        is_mock=is_mock,
        interrupted=interrupted,
        inapplicable_counts=dict(inapplicable_counts),
    )
    skipped_total = sum(inapplicable_counts.values())
    if skipped_total:
        counts = ", ".join(
            f"{operator}={count}"
            for operator, count in sorted(inapplicable_counts.items())
        )
        logger.info("Skipped %s inapplicable candidates: %s", skipped_total, counts)
    logger.info("Pilot artifacts saved under %s", run_dir.resolve())
    return run_dir

def main():
    parser = argparse.ArgumentParser(description="Run Pilot Experiment")
    parser.add_argument("--config", type=str, default="config/models.yaml", help="Path to models config file")
    parser.add_argument("--data", type=str, default="data/baseline_prompts.csv", help="Path to baseline prompts")
    parser.add_argument("--output-dir", type=str, default="results/pilot_experiment/raw", help="Output directory for raw results")
    parser.add_argument("--repetitions", type=int, default=3, help="Number of repetitions")
    parser.add_argument(
        "--control-repetitions",
        type=int,
        default=1,
        help="Unchanged-prompt control pairs per prompt/model (default: 1).",
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=None,
        help="Override the model-configured generation token cap.",
    )
    parser.add_argument(
        "--semantic-model",
        default="sentence-transformers/all-MiniLM-L6-v2",
        help="Sentence-transformer model used for input semantic distance.",
    )
    parser.add_argument(
        "--prompts-per-category",
        type=int,
        default=10,
        help="Maximum baseline prompts sampled per task category (default: 10).",
    )
    parser.add_argument("--mock", action="store_true", help="Run with mock provider for validation (no API keys required)")
    parser.add_argument("--models", type=str, nargs="+", default=None, help="Specific model names to run (e.g. --models gemini-1.5-flash llama-3.1-8b-instant)")
    parser.add_argument("--all-models", action="store_true", help="Include paid models as well (OpenAI GPT-3.5/GPT-4o)")
    parser.add_argument("--require-all", action="store_true", help="Fail if any selected model has unconfigured credentials")
    
    args = parser.parse_args()
    if args.repetitions < 1:
        parser.error("--repetitions must be at least 1")
    if args.control_repetitions < 1:
        parser.error("--control-repetitions must be at least 1")
    if args.prompts_per_category < 1:
        parser.error("--prompts-per-category must be at least 1")
    if args.max_tokens is not None and args.max_tokens < 1:
        parser.error("--max-tokens must be at least 1")
    
    all_models = load_models_config(args.config)
    if args.models:
        models = [m for m in all_models if m["name"] in args.models]
        if not models:
            logger.error(f"None of requested models {args.models} found in {args.config}")
            sys.exit(1)
    elif args.all_models:
        models = all_models
    else:
        # Default: Use ALL models that have free API keys!
        free_models = [m for m in all_models if m.get("is_free_tier", False)]
        models = free_models if free_models else all_models
    
    data_path = Path(args.data)
    providers = validate_environment(models, data_path, use_mock=args.mock, allow_partial=not args.require_all)
    prompts = sample_dataset(
        data_path,
        num_categories=5,
        prompts_per_category=args.prompts_per_category,
    )
    
    run_pilot(
        providers,
        prompts,
        Path(args.output_dir),
        repetitions=args.repetitions,
        is_mock=args.mock,
        control_repetitions=args.control_repetitions,
        max_tokens=args.max_tokens,
        semantic_model=args.semantic_model,
        dataset_path=data_path,
    )

if __name__ == "__main__":
    main()
