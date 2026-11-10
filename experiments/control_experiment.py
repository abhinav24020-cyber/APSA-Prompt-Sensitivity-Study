import os
import csv
import json
import logging
import argparse
from pathlib import Path
from typing import List, Dict, Any
from collections import defaultdict
import itertools
import Levenshtein
import yaml

import sys
sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

from apsa.llm_providers import LLMProviderFactory, MockProvider
from apsa.llm_providers.base import load_env_file

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def load_models_config(config_path: str) -> Dict[str, Any]:
    load_env_file()
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def load_baseline_prompts(csv_path: str, limit: int = None) -> List[Dict[str, str]]:
    prompts = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if limit and i >= limit:
                break
            prompts.append(row)
    return prompts

def calculate_variance(outputs: List[str]) -> Dict[str, Any]:
    """Calculate the baseline variance across identical prompt runs.
    
    This establishes the model's natural stochastic variance.
    The final analysis must distinguish natural output variance from 
    perturbation-induced output variance.
    """
    failed_runs = sum(1 for o in outputs if not o or o.startswith("[ERROR]"))
    valid_outputs = [o for o in outputs if o and not o.startswith("[ERROR]")]
    
    if len(valid_outputs) < 2:
        return {
            "mean_levenshtein_distance": 0.0,
            "mean_normalized_char_distance": 0.0,
            "max_levenshtein_distance": 0.0,
            "max_normalized_char_distance": 0.0,
            "exact_match_ratio": 1.0 if len(valid_outputs) == 1 else 0.0,
            "valid_runs": len(valid_outputs),
            "failed_runs": failed_runs,
            "is_valid": len(valid_outputs) >= 2,
        }
    
    lev_distances = []
    norm_distances = []
    exact_matches = 0
    pairs = list(itertools.combinations(valid_outputs, 2))
    
    for o1, o2 in pairs:
        dist = Levenshtein.distance(o1, o2)
        norm_dist = dist / max(len(o1), len(o2), 1)
        lev_distances.append(dist)
        norm_distances.append(norm_dist)
        if dist == 0:
            exact_matches += 1
            
    return {
        "mean_levenshtein_distance": sum(lev_distances) / len(lev_distances),
        "mean_normalized_char_distance": sum(norm_distances) / len(norm_distances),
        "max_levenshtein_distance": max(lev_distances),
        "max_normalized_char_distance": max(norm_distances),
        "exact_match_ratio": exact_matches / len(pairs),
        "valid_runs": len(valid_outputs),
        "failed_runs": failed_runs,
        "is_valid": True,
    }

def run_control_experiment(
    model_name: str, 
    provider_name: str, 
    config: Dict[str, Any], 
    prompts: List[Dict[str, str]], 
    repetitions: int,
    output_dir: Path,
    use_mock: bool = False,
):
    try:
        if use_mock:
            provider = MockProvider(model_name)
        else:
            provider = LLMProviderFactory.create(provider_name, model_name)
    except Exception as e:
        logger.error(f"Failed to initialize provider: {e}")
        return

    output_dir.mkdir(parents=True, exist_ok=True)
    results_file = output_dir / f"control_results_{model_name.replace('/', '_')}.jsonl"
    variance_file = output_dir / f"control_variance_{model_name.replace('/', '_')}.json"

    logger.info(f"Starting control experiment for {model_name} with {repetitions} repetitions (mock={use_mock}).")
    
    all_results = {}
    category_variances = defaultdict(list)
    
    with open(results_file, 'w', encoding='utf-8') as out_f:
        for prompt_data in prompts:
            prompt_id = prompt_data["prompt_id"]
            original_prompt = prompt_data["original_prompt"]
            task_category = prompt_data.get("task_category", "unknown")
            logger.info(f"Processing prompt {prompt_id} ({task_category})...")
            
            prompt_outputs = []
            
            for i in range(repetitions):
                try:
                    result = provider.generate(original_prompt, config)
                    prompt_outputs.append(result.output)
                    
                    record = {
                        "status": "success",
                        "prompt_id": prompt_id,
                        "task_category": task_category,
                        "repetition": i + 1,
                        "result": result.model_dump()
                    }
                    out_f.write(json.dumps(record) + "\n")
                except Exception as e:
                    logger.error(f"Error generating output for {prompt_id} on repetition {i+1}: {e}")
                    prompt_outputs.append(f"[ERROR]: {str(e)}")
                    error_record = {
                        "status": "failed",
                        "prompt_id": prompt_id,
                        "task_category": task_category,
                        "repetition": i + 1,
                        "error": str(e)
                    }
                    out_f.write(json.dumps(error_record) + "\n")
                if not use_mock:
                    import time
                    time.sleep(1.0)
                    
            # Calculate variance for this prompt
            variance_metrics = calculate_variance(prompt_outputs)
            all_results[prompt_id] = {
                "task_category": task_category,
                "outputs": prompt_outputs,
                "variance": variance_metrics
            }
            if variance_metrics["is_valid"]:
                category_variances[task_category].append(variance_metrics["mean_normalized_char_distance"])
            logger.info(f"Prompt {prompt_id} variance: {variance_metrics}")
            
    # Calculate per-category statistics
    per_category_stats = {}
    for cat, diffs in category_variances.items():
        per_category_stats[cat] = {
            "mean_normalized_distance": sum(diffs) / len(diffs) if diffs else 0.0,
            "max_normalized_distance": max(diffs) if diffs else 0.0,
            "sample_count": len(diffs),
        }

    overall_mean_levenshtein = (
        sum(r["variance"]["mean_levenshtein_distance"] for r in all_results.values() if r["variance"]["is_valid"]) 
        / max(sum(1 for r in all_results.values() if r["variance"]["is_valid"]), 1)
    )
    overall_mean_norm_dist = (
        sum(r["variance"]["mean_normalized_char_distance"] for r in all_results.values() if r["variance"]["is_valid"]) 
        / max(sum(1 for r in all_results.values() if r["variance"]["is_valid"]), 1)
    )
    
    summary = {
        "model_name": model_name,
        "is_mock": use_mock,
        "total_prompts": len(prompts),
        "overall_mean_levenshtein": overall_mean_levenshtein,
        "overall_mean_normalized_distance": overall_mean_norm_dist,
        "per_category_baseline_variances": per_category_stats,
        "prompt_details": all_results,
    }

    with open(variance_file, 'w', encoding='utf-8') as vf:
        json.dump(summary, vf, indent=2)
        
    logger.info(f"Control experiment completed. Results saved to {output_dir}")
    logger.info(f"Overall Mean Levenshtein Distance across prompts: {overall_mean_levenshtein:.2f}")
    logger.info(f"Overall Mean Normalized Distance across prompts: {overall_mean_norm_dist:.4f}")

def main():
    parser = argparse.ArgumentParser(description="Run Control Experiment to measure natural LLM output variability.")
    parser.add_argument("--model", type=str, required=True, help="Model name (e.g., gpt-3.5-turbo)")
    parser.add_argument("--config", type=str, default="config/models.yaml", help="Path to models config file")
    parser.add_argument("--data", type=str, default="data/baseline_prompts.csv", help="Path to baseline prompts")
    parser.add_argument("--repetitions", type=int, default=3, help="Number of times to run each prompt")
    parser.add_argument("--limit", type=int, default=5, help="Number of prompts to run (for pilot)")
    parser.add_argument("--output-dir", type=str, default="results/control_experiment", help="Output directory")
    parser.add_argument("--mock", action="store_true", help="Run with mock provider for validation")
    
    args = parser.parse_args()
    
    models_config = load_models_config(args.config)
    
    model_cfg = next((m for m in models_config.get("models", []) if m["name"] == args.model), None)
    if not model_cfg:
        logger.error(f"Model {args.model} not found in {args.config}")
        sys.exit(1)
        
    prompts = load_baseline_prompts(args.data, limit=args.limit)
    
    run_control_experiment(
        model_name=model_cfg["name"],
        provider_name=model_cfg["provider"],
        config=model_cfg,
        prompts=prompts,
        repetitions=args.repetitions,
        output_dir=Path(args.output_dir),
        use_mock=args.mock,
    )

if __name__ == "__main__":
    main()
