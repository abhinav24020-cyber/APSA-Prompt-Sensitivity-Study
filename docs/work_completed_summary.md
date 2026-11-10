# APSA Work Completed Summary

**Status date:** November 6, 2026  
**Scope:** Work completed within the planned APSA Phases 1–10. No Phase 11 work is included.

## Project direction

APSA is intended to study how model responses change when prompts receive small, controlled modifications. The codebase and documentation have been reviewed against that goal, with emphasis on reproducibility, traceability, conservative interpretation of semantic risk, and separating software checks from empirical evidence.

The project has a substantial research-software foundation, but it is **not yet ready for broad empirical conclusions**. Candidate generation is not an adversarial optimizer, and the existing pilot is exploratory rather than a controlled validation study.

## Work completed

### Research design and documentation

- Documented the research question, constrained input/output-distance framing, research questions, hypotheses, and the planned Phase 1–10 workflow.
- Corrected project status claims to distinguish implemented functionality, software tests, mock runs, and live-model observations.
- Corrected the documented baseline dataset size to 100 prompts across five task categories.
- Added a pilot workflow guide covering the lightweight pilot script, its JSONL format, evaluation command, and interpretation limits.
- Added this summary as a navigational account of the work and remaining research requirements.

### Dataset and perturbation engine

- Added a baseline structure audit for required fields, IDs/prompts, metadata JSON, category balance, answer coverage, and Python syntax of code references.
- Audited the 100-row dataset: 20 prompts per category, difficulty counts 59 easy/34 medium/7 hard, no structural omissions or duplicate IDs/prompts, and all code references parse as Python.
- Corrected five reference/prompt issues found in a targeted answer review: `MATH-002`, `MATH-010`, `LOGIC-006`, `LOGIC-008`, and `QA-006`. Code reference behavior remains untested and complete independent expert review is not claimed.
- Documented the implemented perturbation families, their operating constraints, and the difference between lexical distance, surface form, and semantic equivalence.
- Added more conservative semantic-risk rules for negation, known polarity changes, critical quantifiers, and numeric changes. Lexical and punctuation edits are not assumed to preserve meaning.
- Recorded risk rationales and normalized character/word edit distances with perturbation provenance.
- Made generated perturbation identifiers stable for the same inputs/configuration while distinguishing parameter variants.
- Removed or corrected operator behavior that could modify unrelated capitalization, silently skip unknown operators, or claim a multiword change was a single-token synonym replacement.
- Kept inapplicable candidates as skips rather than substituting the unchanged prompt.
- Added focused tests for operator behavior, risk detection, edit-distance metadata, and identifiers.

### Experiment execution and stored results

- Updated the main trial runner to reject inapplicable or over-budget candidates before making model requests.
- Removed fallback substitutions that could present a different metric as a missing semantic or output metric. When syntactic distance is unavailable but required by configured weights, sensitivity remains unavailable instead of being assigned a fabricated value.
- Made unavailable sensitivity values representable in the stored result schema.
- Added a separate `failures.jsonl` stream for failed main-run trials, retaining successful pairs in `results.jsonl`.
- Added a separate rate-limit exception for Groq. On HTTP 429 the pilot stops sending requests to that provider, preserves completed records, records the failure and available retry-after value, and marks the report partially complete instead of sleeping through repeated long retries.
- Separated lightweight-pilot successful observations (`raw_results.jsonl`) from failed provider trials (`failed_trials.jsonl`); mock and live runs each receive a unique mode-specific directory, while evaluator outputs are written to a separate analysis directory.
- Added `--prompts-per-category` to the lightweight pilot for smaller workloads. It selects the first N available rows per category; this is a workload cap, not randomized sampling.
- Added mode-separated, run-specific output directories; a `run_manifest.json` containing the dataset hash and selected IDs, resolved provider/model and generation settings, finish-token cap, semantic model, timestamps, and counts; secret-like configuration fields are redacted.
- Added unchanged-prompt control pairs (`--control-repetitions`) and per-response provider finish reasons where available. `--max-tokens` can override the configured output limit for a new run.
- Added actual sentence-embedding input cosine distance to each treatment record and a matched `0.5` lexical / `0.5` semantic sensitivity ratio. Missing semantic distances remain unavailable; syntactic tree distance has zero weight.
- Added pilot evaluation for supported-category reference-answer checks, output character deviation, separate control statistics, and correctness transitions. The correctness checks are heuristics, not human adjudication; code generation is not evaluated.
- Changed inapplicable perturbation logging from one warning per prompt to aggregate per-operator counts in the run log and pilot report.
- Clarified pilot report terminology so the scheduled count is labeled as a maximum before inapplicable candidates are skipped.

### Metrics and interpretation

- Reviewed input distance, output deviation, functional evaluation, and sensitivity scoring paths.
- Documented that character edit distance measures output-string change, not semantic change or correctness.
- Documented that the pilot's headline output statistics are normalized character distances, while sensitivity analysis also reports a lexical/semantic composite-input ratio when available.
- Documented that finish reasons help identify output-limit termination, while absent finish reasons cannot establish completeness.
- Updated metrics and architecture documentation to state that syntactic tree distance is unimplemented and excluded from composite scoring.

## Verification completed

- The full repository test suite passed: **198 passed**.
- Ruff passed for the new and rewritten pilot/dataset code. A full-repository Ruff run still reports numerous pre-existing lint violations outside this focused change.
- The new CLI option was checked with `experiments/pilot_experiment.py --help`.
- The baseline audit passed: 100 rows, 20 per category, no blank required fields, duplicate IDs/prompts, metadata errors, or Python syntax errors in code references.
- Mock runs were used for software-path validation only. Mock responses are not model observations.
- One user-approved current-code live pilot was executed separately; its partial results and provider failure are documented below.

Passing tests establish software behavior covered by those tests; they do not prove semantic preservation, causal effects, or general model robustness.

## Existing pilot evidence

The repository contains an earlier live pilot artifact, separate from the work above:

- Raw paired records: `results/pilot_experiment/raw/pilot_raw_results_1793047745.jsonl`
- Live-only summary: `results/pilot_experiment/analysis/live_model_pilot_1793047745/sensitivity_analysis_summary.json`

The raw file has 150 successful pairs from `openai/gpt-oss-20b` through Groq, covering 50 prompts across five categories. Operator counts are unbalanced: 50 insertions, 50 deletions, 24 substitutions, 18 reorderings, and 8 punctuation variants. Of the 300 responses, 167 report the configured 256-token ceiling. Finish reasons were not stored, so truncation is possible but unconfirmed.

The live-only summary reports mean normalized character output distance `0.2816`, median `0.1821`, record-level 95% interval `[0.2301, 0.3331]`, and maximum observed character output distance `1.0` under the listed character-distance budgets. These are descriptive statistics for that artifact. They are not semantic or correctness scores, causal estimates, or generalizable rankings. The summary beside the live-only directory that contains 1,152 mock records must not be cited as live-model evidence.

The live artifact predates the latest pilot changes. It should not be assumed to have been generated by the current code revision.

## Current-code live pilot

The approved run is stored separately under:

- Raw successful observations: `results/pilot_experiment/live/pilot_live_cf5a4c9f/raw_results.jsonl`
- Failed trial: `results/pilot_experiment/live/pilot_live_cf5a4c9f/failed_trials.jsonl`
- Resolved configuration and sampling provenance: `results/pilot_experiment/live/pilot_live_cf5a4c9f/run_manifest.json`
- Analysis: `results/pilot_experiment/analysis/live_pilot_cf5a4c9f/sensitivity_analysis_summary.json`

The run used Groq `openai/gpt-oss-20b`, temperature 0, a 1,024-token output cap, the first 10 prompts per each of five categories, one treatment repetition, and one unchanged-prompt control pair per prompt. It stopped after a provider HTTP 429 tokens-per-day limit while processing `MATH-002`; the provider reported a 148-second retry-after. The run had started 20 model requests and recorded 9 successful pairs (7 treatments and 2 controls) across only `MATH-001` and `MATH-002`, plus one failed treatment. One successful response from that incomplete pair was not retained by the run writer in this run; current code now records one-sided responses with failures, but the missing historical response cannot be reconstructed. Thus, it did **not** achieve the planned 50-prompt or multi-category coverage.

All 18 finish reasons in successful pairs were `stop`; the maximum observed output length was 568 tokens and none reached the 1,024-token cap. This small, partial run therefore supplies no evidence of truncation at the raised cap; it is not a full replication of the earlier pilot. The two unchanged-prompt controls had zero character output distance. Across seven treatment pairs, the descriptive mean normalized character distance was 0.4180; one pair changed from correct to incorrect under the pilot's heuristic evaluator. These observations are limited to two math prompts and one model; they are not generalizable or causal results.

## Remaining work within Phases 1–10

Before using APSA for the main study:

1. Re-run or continue the current-code live experiment only after the provider quota resets, using a request budget that can complete the planned coverage.
2. Compare the earlier 256-token live artifact with an adequately covered run using the higher cap; finish reasons are now stored when providers return them.
3. Expand live prompt/model coverage and control repetitions within an explicitly approved request budget. The runner supports multiple models, per-category prompt caps, all registered pilot operators, and control repetitions.
4. Complete independent expert review and code-reference execution tests before treating the dataset's reference answers as validated ground truth.
5. Continue to keep mock observations, live observations, failed trials, and analyses clearly separated.

These are remaining requirements within the declared Phases 1–10; they do not introduce a new phase.
