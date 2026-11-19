"""APSA end-to-end demonstration for one prompt (Phase 17, Task 17.5).

Steps shown: baseline prompt -> perturbation -> input distances and semantic-risk flag ->
original/perturbed outputs -> output deviation, correctness, sensitivity -> where the pair
appears in the analysis dataset.

By default the outputs are RECORDED generations from a completed live study (no network
calls). With ``--live`` the two prompts are sent to the chosen model now.

Examples (PowerShell):
  .\\.venv\\Scripts\\python.exe experiments\\demo.py --prompt-id MATH-005 --operator char_substitution
  .\\.venv\\Scripts\\python.exe experiments\\demo.py --prompt-id CLASS-004 --operator word_insertion --model allam-2-7b
  .\\.venv\\Scripts\\python.exe experiments\\demo.py --prompt-id QA-001 --operator synonym --live
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

import yaml  # noqa: E402

from apsa.metrics.functional.answer_key import ANSWER_KEY, score_answer  # noqa: E402
from apsa.metrics.functional.code_execution import CODE_TESTS, run_code_tests  # noqa: E402
from apsa.metrics.input_distance import LexicalDistanceCalculator  # noqa: E402
from apsa.metrics.output_distance import OutputDeviationMetrics  # noqa: E402
from apsa.perturbations import get_perturbation  # noqa: E402
from apsa.perturbations.base_perturbation import PerturbationConfig  # noqa: E402


def banner(text: str) -> None:
    print("\n" + "=" * 78 + f"\n{text}\n" + "=" * 78)


def show(label: str, text: str, width: int = 76, limit: int = 1200) -> None:
    text = text if len(text) <= limit else text[:limit] + f"\n... [{len(text) - limit} more chars]"
    print(f"--- {label} ---")
    for para in text.splitlines() or [""]:
        print(textwrap.fill(para, width) if para.strip() else "")


def correctness(prompt_id: str, output: str):
    if prompt_id in CODE_TESTS:
        return run_code_tests(prompt_id, output).passed
    if prompt_id in ANSWER_KEY:
        return score_answer(prompt_id, output)
    return None


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--prompt-id", default="MATH-005")
    p.add_argument("--operator", default="char_substitution")
    p.add_argument("--model", default="openai/gpt-oss-120b")
    p.add_argument("--study-dir", default="results/study/main_v1")
    p.add_argument("--live", action="store_true", help="Send both prompts to the model now")
    args = p.parse_args()

    cfg = yaml.safe_load((ROOT / "config/experiments/main_study.yaml").read_text(encoding="utf-8"))
    rows = {r["prompt_id"]: r for r in csv.DictReader(open(ROOT / cfg["dataset"], encoding="utf-8"))}
    row = rows[args.prompt_id]
    original = row["original_prompt"]

    banner(f"1. Baseline prompt {args.prompt_id} ({row['task_category']})")
    show("original prompt", original)
    print(f"reference answer: {row['expected_answer'][:200]}")

    banner(f"2. Perturbation operator: {args.operator} (seed {cfg['perturbation_seed']})")
    params = {}
    if args.operator == "punctuation":
        params = {"mode": "remove_trailing_period" if original.rstrip().endswith((".", "!", "?"))
                  else "add_trailing_period"}
    record = get_perturbation(args.operator).perturb(
        original, prompt_id=args.prompt_id, config=PerturbationConfig(params=params, seed=cfg["perturbation_seed"]))
    if record is None:
        print("Operator is inapplicable to this prompt (no candidate generated). Try another operator.")
        return
    perturbed = record.perturbed_prompt
    show("perturbed prompt", perturbed)

    banner("3. Input distance and semantic-risk check")
    lex = LexicalDistanceCalculator().compute(original, perturbed)
    print(f"character edits: {lex.char_levenshtein}  normalised: {lex.char_levenshtein_normalized:.4f}")
    print(f"word edits: {lex.word_levenshtein}   share of prompt changed: {lex.pct_prompt_changed:.2f}%")
    from apsa.metrics.input_distance.semantic import SemanticDistanceCalculator, SentenceTransformerEmbedder

    sem = SemanticDistanceCalculator(SentenceTransformerEmbedder(model_name=cfg["semantic_model"])).compute(
        original, perturbed)
    print(f"semantic cosine distance (MiniLM): {sem.cosine_distance:.4f}")
    print(f"semantic risk flag: {record.semantic_risk_level.value}  reasons: {record.semantic_risk_reasons}")
    print("NOTE: a small embedding distance is evidence, not proof, that meaning is preserved.")

    banner(f"4. Model outputs ({'LIVE call now' if args.live else 'RECORDED live-study generations'})")
    if args.live:
        from apsa.llm_providers import LLMProviderFactory

        m = next(x for x in cfg["models"] if x["name"] == args.model)
        provider = LLMProviderFactory.create(m["provider"], m["name"])
        req = {**cfg["generation"], **{k: v for k, v in m.items() if k in ("reasoning_effort",)},
               "system_prompt": cfg["system_prompt"]}
        out_o = provider.generate(original, req).output
        out_p = provider.generate(perturbed, req).output
        source = "live call (not part of the archived study data)"
    else:
        slug = args.model.replace("/", "_")
        path = ROOT / args.study_dir / "raw" / f"generations__{slug}.jsonl"
        gens = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
        anchor = next((g for g in gens if g["prompt_id"] == args.prompt_id and g["condition"] == "anchor"), None)
        treat = next((g for g in gens if g["prompt_id"] == args.prompt_id and g["condition"] == "treatment"
                      and g["operator"] == args.operator), None)
        if anchor is None or treat is None:
            print("No recorded generation for this model/prompt/operator. Use --live or another combination.")
            return
        out_o, out_p = anchor["output"], treat["output"]
        source = f"recorded: anchor {anchor['record_id']} / treatment {treat['record_id']}"
    print(f"model: {args.model}   source: {source}")
    show("output for ORIGINAL prompt", out_o)
    show("output for PERTURBED prompt", out_p)

    banner("5. Output deviation, correctness and sensitivity")
    odm = OutputDeviationMetrics(use_semantic=False)
    from sentence_transformers import SentenceTransformer

    enc = SentenceTransformer(cfg["semantic_model"])
    e = enc.encode([out_o, out_p], normalize_embeddings=True)
    d_sem = 0.0 if out_o.strip() == out_p.strip() else max(0.0, 1 - float(e[0] @ e[1]))
    print(f"semantic output distance: {d_sem:.4f}")
    print(f"character output distance: {odm.normalized_character_distance(out_o, out_p):.4f}")
    print(f"token Jaccard distance: {odm.token_level_distance(out_o, out_p):.4f}")
    c_o, c_p = correctness(args.prompt_id, out_o), correctness(args.prompt_id, out_p)
    print(f"correct (original -> perturbed): {c_o} -> {c_p}"
          + ("   <-- CORRECTNESS FLIP" if c_o is not None and c_o != c_p else ""))
    d_in = 0.5 * lex.char_levenshtein_normalized + 0.5 * sem.cosine_distance
    print(f"sensitivity ratio d_out_sem / (0.5*d_char + 0.5*d_sem + 1e-4) = {d_sem / (d_in + 1e-4):.2f}"
          + ("  (denominator < 0.01: ratio unstable, read the absolute deviation)" if d_in < 0.01 else ""))

    banner("6. Where this appears in the analysis")
    print(f"pair_id = {args.model}|{args.prompt_id}|treatment|{args.operator}|1")
    print(f"-> {args.study_dir}/processed/analysis_pairs.csv (one row per anchor-paired comparison)")
    print(f"-> aggregated in {args.study_dir}/analysis/results.json and figures/")
    print("Interpretation: compare with the unchanged-prompt controls for the same model; "
          "temperature-0 APIs are not perfectly deterministic.")


if __name__ == "__main__":
    main()
