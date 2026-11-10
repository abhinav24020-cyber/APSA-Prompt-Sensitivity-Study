# APSA Pilot Study: Workflow and Output Guide

## Purpose and scope

The APSA pilot is an exploratory paired experiment and pipeline check. It can select baseline prompts, generate perturbations, measure lexical and embedding-based input distances, query a model, save raw responses and finish reasons, add unchanged-prompt controls, and calculate descriptive output and correctness statistics.

It is **not** a comprehensive evaluation of LLM robustness or an adversarial optimizer. Controls estimate output variation under repeated identical prompts, but do not by themselves establish causality or generalize across prompts and models. Semantic embedding distance and correctness heuristics are informative measurements, not human judgments that meaning was preserved or the answer is correct.

## Which pilot script?

There are two experiment entry points in the repository:

- `experiments/pilot_experiment.py` is the lightweight pilot described here. It reads `data/baseline_prompts.csv` and writes the pilot-specific JSONL format.
- `scripts/run_experiment.py --config ...` runs the modular experiment engine and writes a different `ExperimentRun` schema.

Do not pass the lightweight pilot's raw JSONL to `scripts/run_analysis.py`. Use `experiments/evaluate_experiment.py` for that JSONL format.

## Pilot procedure

### 1. Select model(s) and validate setup

The pilot reads model definitions from `config/models.yaml`. By default, it selects all entries marked `is_free_tier: true`. `--models` restricts the run to named entries. For a live provider, the required provider credential must be available locally; API keys belong in `.env` or the environment, never in the experiment data or this document. `--mock` uses deterministic mock responses and makes no live model calls.

The validation step checks that the CSV exists and that the five configured perturbation operators are registered. For live runs, models without credentials can be skipped unless `--require-all` is used.

### 2. Select baseline prompts

`sample_dataset()` reads the CSV in file order. By default, it takes the first 10 rows for each category, then selects the first five categories with at least 10 rows, in the order categories appear in the CSV. `--prompts-per-category` changes the per-category cap for smaller pilots. This is a fixed first-rows-per-category selection, **not randomized sampling**.

The pilot prompt fields are `prompt_id`, `task_category`, and `original_prompt`. The baseline text is used as provided in the CSV and retained in the raw result record.

### 3. Generate one candidate for each operator

Each selected prompt is passed to these five operators, with seed `42`:

1. punctuation
2. word insertion
3. word deletion
4. word substitution
5. instruction reordering

For punctuation, the script removes a trailing period when the prompt ends in `.`, `!`, or `?`; otherwise it adds a period. Other operators use their default parameters. If an operator cannot modify a prompt (for example, reordering a single-sentence prompt), the script skips that candidate and makes no model calls for it.

The script calculates character Levenshtein distance, normalized character distance, word Levenshtein distance, percentage changed, a rule-based semantic-risk label, and embedding cosine distance using the configured sentence-transformer model (default `sentence-transformers/all-MiniLM-L6-v2`). The semantic-risk label and embedding distance do not prove that meaning was preserved.

### 4. Query the model with the paired prompts

For each prompt, the runner first issues unchanged-prompt control pairs. Each control pair compares two independently generated outputs for the exact same prompt. For every applicable treatment candidate and repetition, the provider receives:

- the original prompt; and
- the perturbed prompt.

The pilot calls these sequentially, using the same model configuration. Each successful pair is one trial and normally involves two model requests. `--repetitions` repeats treatment pairs; `--control-repetitions` controls the number of unchanged-prompt pairs per prompt and model (default 1). The control and treatment conditions are labeled separately in raw data and analysis.

The number of possible pairs before inapplicable candidates is:

```text
selected models × selected prompts × (5 operators × treatment repetitions + control repetitions)
```

The number of actual requests can be lower because inapplicable perturbations are skipped or higher/lower than expected if requests fail or retries occur within a provider.

Inapplicable candidates are counted per operator and summarized once in the run log and `pilot_report.md`; they are not emitted as one warning per prompt. This keeps logs readable while retaining a per-operator accounting of skipped candidates.

### 5. Save raw records

Each run gets a unique directory separated by execution mode:

```text
<output-dir>/mock|live/<experiment-id>/
  raw_results.jsonl
  failed_trials.jsonl
  run_manifest.json
  pilot_report.md
```

Each non-empty line in `raw_results.jsonl` is a successful observation containing experiment/mode/provider/model metadata, generation settings, task/prompt IDs, expected answer, condition, perturbation provenance, input distances, finish reasons, both outputs, latency, and token counts. Failed model calls are written separately to `failed_trials.jsonl` with error details and any response already received for an incomplete pair. Inapplicable perturbations are logged and skipped, rather than written as successful no-op records. The manifest records dataset hash, selected IDs and category counts, resolved model config, generation settings, output-token limit, and semantic embedding model; secret-like configuration fields are redacted.

The run-specific directory prevents reports and raw data from different runs from overwriting one another. Keep the manifest and raw JSONL together as the source record.

For Groq, an HTTP 429 rate-limit response is saved as a failed JSONL record with any available `Retry-After` value. The runner stops sending requests to that provider for the current run instead of sleeping through repeated long retry windows or continuing to generate more 429s. Completed records are retained, and the report marks the run as partially completed. A rate limit is a provider/account quota condition, not a perturbation failure; wait for the stated reset, reduce the run size or repetition count, or check the provider's current limits before starting another live run.

### 6. Evaluate output differences

Run the pilot evaluator on the raw file:

```powershell
.\.venv\Scripts\python.exe experiments\evaluate_experiment.py `
  --input results\pilot_experiment\raw\pilot_raw_results_<unix-time>.jsonl `
  --output-dir results\pilot_experiment\analysis\<run-name>
```

The evaluator analyzes controls separately, writes the evaluated records and summary below, and includes the count from the sibling `failed_trials.jsonl` when present:

```text
results/pilot_experiment/analysis/<run-name>/sensitivity_analysis_summary.json
results/pilot_experiment/analysis/<run-name>/evaluated_records.jsonl
```

Output deviation and its descriptive statistics use **normalized character output distance**. The evaluator reports the character-only sensitivity ratio and, when actual semantic input distance is present, a composite-input ratio:

```text
composite input distance = 0.5 × normalized character distance + 0.5 × semantic embedding distance
sensitivity ratio = normalized character output distance / (composite input distance + 0.0001)
```

The syntactic tree-distance weight is `0.0` because tree edit distance is not implemented. Missing semantic distances are kept unavailable and are not replaced with lexical distance. Ratios can become large when their denominator is small; they are not probabilities, percentages, or standalone measures of semantic sensitivity.

### 7. Interpret the results carefully

The summary describes differences in output strings. For supported task categories, it also applies conservative reference-answer checks and reports correctness transitions. These automated checks are heuristics, not human adjudication or validated task-specific scoring. A distance of `1.0` means maximal normalized **character-string distance under this metric**, not necessarily a maximal change in meaning or correctness.

Control records quantify observed repeated-output string variation for identical prompts; compare their distribution with treatment deviations, but do not treat a single control mean as a causal adjustment. Task-specific checks are limited to categories with supported heuristics; code generation is reported as not evaluated.

Provider finish reasons and token counts are saved when returned by the provider. A finish reason such as `length` indicates output-limit termination; a missing finish reason is not evidence that the response was complete. Compare caps by running separate experiments and retaining each manifest.

## Example: the existing live pilot artifact

The repository includes an earlier live-model pilot and the separate, partial current-code live
run:

- Raw paired records: `results/pilot_experiment/raw/pilot_raw_results_1793047745.jsonl`
- Summary: `results/pilot_experiment/analysis/live_model_pilot_1793047745/sensitivity_analysis_summary.json`
- Current-code manifest and data: `results/pilot_experiment/live/pilot_live_cf5a4c9f/`
- Current-code analysis: `results/pilot_experiment/analysis/live_pilot_cf5a4c9f/sensitivity_analysis_summary.json`

That raw file contains 150 successful paired records from `openai/gpt-oss-20b`, one repetition per recorded pair, across 50 prompts (10 in each of five categories). Operator coverage is not balanced: 50 insertions, 50 deletions, 24 substitutions, 18 reorderings, and 8 punctuation variants. The raw records also show 81 original and 86 perturbed responses at the configured 256-token ceiling. These counts do not prove truncation, but the absent finish reasons mean it cannot be ruled out.

The summary reports a mean normalized character output distance of `0.2816`, a median of `0.1821`, and a record-level 95% interval of `[0.2301, 0.3331]`. These are descriptive statistics for this specific pilot artifact, not causal estimates, correctness results, or evidence that the rankings generalize to other prompts, operators, or models.

Keep mock-run outputs separate from live-model observations. A mock run is useful for checking the software path and output format, but its generated responses are not model evidence.

## Re-running safely

### Professor/demo walkthrough (offline mock)

From the project root in PowerShell, run a small, reproducible demonstration without API calls:

```powershell
.\.venv\Scripts\python.exe experiments\pilot_experiment.py `
  --mock --models openai/gpt-oss-20b --prompts-per-category 1 `
  --repetitions 1 --control-repetitions 1 `
  --output-dir results\demo
```

This selects one baseline prompt from each of the five categories. At most 30 pairs
(5 prompts × (5 treatment operators + 1 control)) are scheduled, or 60 mock generations;
inapplicable transformations are skipped. The run is stored in
`results\demo\mock\<experiment-id>\`.

To evaluate the newest demo run and write its Phase 9/10 analysis:

```powershell
$run = Get-ChildItem results\demo\mock -Directory |
  Sort-Object LastWriteTime -Descending |
  Select-Object -First 1

.\.venv\Scripts\python.exe experiments\evaluate_experiment.py `
  --input "$($run.FullName)\raw_results.jsonl" `
  --output-dir "results\demo\analysis\$($run.Name)"
```

In the terminal, note the analysis summary path. Open `sensitivity_analysis_summary.json`
to show output distances, correctness transitions where supported, unchanged-prompt control
variation, budget-filtered maxima, and the Phase 10 sensitivity ratios. Open
`evaluated_records.jsonl` for prompt-level details, and the run's `run_manifest.json` for
dataset hash, sample IDs, model settings, embedding model, and execution mode.

The existing demonstration at `results\demo\mock\pilot_mock_097c0680\` used 5 prompts, completed
24 mock pairs, skipped 6 inapplicable candidates, and had no failed trials. Re-running creates a
new run ID and does not overwrite that artifact. Mock responses are canned software checks, not
outputs from `openai/gpt-oss-20b`; clearly label them as mock during the presentation.

Suggested demonstration sequence:

1. Show one row in `raw_results.jsonl`: original prompt, perturbed prompt, operator provenance,
   character/semantic input distances, paired outputs, and finish reasons.
2. Show a `control` record to explain repeated unchanged prompts and natural variation.
3. Show `sensitivity_analysis_summary.json` and describe its score as output character distance
   divided by the recorded composite input distance plus `0.0001`. The composite input weights
   lexical and embedding distance equally; syntactic tree distance has zero weight because it is
   not implemented.
4. State explicitly that this mock run demonstrates the Phase 1–10 software path, not empirical
   LLM behavior or validated scientific conclusions.

For a smaller live pilot, limit the baseline sample per category (for example, two prompts per category, up to 10 prompts total):

```powershell
.\.venv\Scripts\python.exe experiments\pilot_experiment.py `
  --models openai/gpt-oss-20b --prompts-per-category 2 --repetitions 1 `
  --control-repetitions 1 --max-tokens 1024 `
  --output-dir results\pilot_experiment
```

`--prompts-per-category` must be a positive integer; the default is 10. The selected rows are still the first rows for each category, so this is a smaller pilot workload, not randomized sampling.

To run a live pilot, first verify the selected provider, credential, current usage limits, model ID, and output-token configuration. Live calls may consume quota or incur charges. Each run gets a unique directory and does not overwrite prior records. Consider increasing `--prompts-per-category`, selecting multiple model IDs with `--models`, and adjusting control repetitions only after confirming the corresponding request budget.

If a live run returns 429, use the saved `retry_after_seconds` as guidance rather than immediately re-running the same workload. You can make a smaller run by selecting a subset of prompts in a separate CSV and passing it with `--data`, or by lowering `--repetitions`. This avoids treating a provider quota limit as a model response or silently dropping the failed comparisons.

The earlier 150-pair artifact predates current code and must not be conflated with the partial current-code attempt. The latter stopped at a provider HTTP 429 tokens-per-day limit after recording 7 treatment pairs and 2 controls across two math prompts. It did not provide the planned expanded coverage. Live calls may consume quota or incur charges; do not use them for a classroom demo unless specifically needed and approved.
