# Adversarial Prompt Sensitivity Analysis (APSA)
## Project Progress and Demonstration Guide — Phases 1–10

|  |  |
|---|---|
| **Prepared for** | Project supervisor / professor |
| **Status date** | November 6, 2026 |
| **Scope** | Work completed and remaining within Phases 1–10 |
| **Project status** | Research framework implemented; broad live validation remains incomplete |

> **Presentation note:** The demo instructions use mock responses so the pipeline can be demonstrated without making API calls. Clearly distinguish mock validation from live-model observations and empirical validation.

## Contents

- [Project overview](#1-project-overview)
- [Experimental workflow](#2-experimental-workflow)
- [Work completed by phase](#3-work-completed-by-phase)
- [Run the offline demonstration](#4-how-to-run-the-demo-mockoffline)
- [Optional live execution](#5-optional-live-execution)
- [Run artifacts and reproducibility](#6-output-files-and-reproducibility)
- [Evidence and current results](#7-evidence-and-limits)
- [Current problems and risks](#8-current-project-problems-and-remaining-risks)
- [Validation commands](#9-running-tests-and-dataset-audit)
- [Related documentation](#10-related-documentation)

## 1. Project overview

### Research question

> **How much can a language model's response change when its prompt is modified by a small, controlled amount?**

### Project at a glance

- **Purpose:** Measure relationships between prompt changes and model response changes.
- **Research design:** Compare original and perturbed prompts under the same model configuration, alongside unchanged-prompt controls.
- **Traceability:** Store perturbation provenance, input/output metrics, provider/model settings, and run metadata.
- **Important boundary:** A small edit, high embedding similarity, or large output difference does not by itself prove semantic equivalence, causality, or model vulnerability.
- **Search capability:** The system evaluates a finite set of predefined perturbations; it does not optimize the prompt or guarantee a worst-case result.

### Phase status summary

| Phase | Component | Status |
|---:|---|---|
| 1 | Research methodology | Documented |
| 2 | Modular architecture | Implemented |
| 3 | Baseline dataset | Implemented; full expert answer review pending |
| 4 | Perturbation engine | Implemented; semantic preservation not guaranteed |
| 5 | Input distance metrics | Lexical and semantic distances implemented; syntactic tree distance unavailable |
| 6 | LLM provider interface | Implemented; provider limits apply |
| 7 | Control experiment | Implemented in pilot; broader repetitions needed |
| 8 | Pilot experiment | Implemented; current live run stopped early |
| 9 | Output deviation and correctness | Implemented with text distance and preliminary correctness checks |
| 10 | Sensitivity score | Implemented; interpret as descriptive, not causal |

## 2. Experimental workflow

```text
Baseline dataset
      ↓
Controlled perturbation ──→ Input distance and risk metadata
      ↓
Original / perturbed model outputs + unchanged-prompt controls
      ↓
Output deviation and task-correctness checks
      ↓
Sensitivity summaries and traceable JSON/JSONL artifacts
```

- Select baseline prompts, categories, and reference answers.
- Generate variants with a recorded operator, ID, seed, and metadata.
- Measure lexical and embedding-based semantic input distance.
- Generate original/perturbed pairs under the same provider/model configuration.
- Generate unchanged-prompt controls to observe natural response variation.
- Store successful results, failed trials, and run metadata separately.
- Calculate output deviation, supported-category correctness heuristics, controls, and sensitivity ratios.

## 3. Work completed by phase

### Phase 1 — Research methodology

- **Goal:** Define the research question and experimental framework.
- **Implemented:** Constrained objective, research factors, reproducibility practices, and controls are documented.
- **Caveat:** Hypotheses are not findings; an observed output change alone does not establish causality or vulnerability.

### Phase 2 — Modular architecture

- **Goal:** Separate research components into maintainable modules.
- **Implemented:** Configuration, data, perturbations, metrics, providers, execution, storage, and analysis modules.
- **Caveat:** The lightweight pilot and modular runner use different record formats and analysis commands. This guide uses the lightweight pilot.

### Phase 3 — Baseline dataset

- **Goal:** Store prompts, categories, expected answers, and metadata.
- **Implemented:** 100 rows; 20 each for math, logic, QA, classification, and code generation. Structural audit checks fields, duplicates, metadata, balance, and code syntax.
- **Corrections:** `MATH-002`, `MATH-010`, `LOGIC-006`, `LOGIC-008`, `QA-006`.
- **Caveat:** Sampling is first N rows per category, not randomized. Targeted review is not full expert validation; code has not been execution-tested.
- **Details:** [Dataset card](../data/dataset_card.md) · [Audit report](../data/baseline_dataset_audit.json)

### Phase 4 — Perturbation engine

- **Goal:** Generate traceable prompt variants.
- **Implemented pilot operators:** Punctuation, word insertion, word deletion, word substitution, instruction reordering.
- **Provenance:** Seed, perturbation ID, operator, and metadata are recorded.
- **Skip behavior:** Inapplicable candidates are skipped, not replaced with unchanged prompts.
- **Caveat:** Operators do not guarantee minimality or meaning preservation; risk labels are heuristic.

### Phase 5 — Input distance metrics

- **Goal:** Quantify prompt differences.
- **Implemented:** Character Levenshtein, normalized character, word distance, percentage changed, embedding cosine distance.
- **Traceability:** Embedding model and measured values are stored.
- **Caveat:** Embeddings are not a semantic-equivalence oracle. Syntactic tree distance is unimplemented and has zero composite weight.

### Phase 6 — LLM provider interface

- **Goal:** Use a common interface for model calls.
- **Implemented:** Provider outputs, token usage, latency, generation settings, finish reason where available.
- **Rate limits:** Groq HTTP 429 stops further calls for that model; completed pairs and failed calls are retained.
- **Caveat:** Live calls require credentials and may consume quota or incur costs.

### Phase 7 — Control experiment

- **Goal:** Observe variation without changing the prompt.
- **Implemented:** Unchanged-prompt control pairs per prompt/model; configurable with `--control-repetitions`.
- **Caveat:** Controls are references, not an automatic causal correction or universal noise threshold. Strong estimates need broader coverage and repetitions.

### Phase 8 — Pilot experiment

- **Goal:** Exercise the pipeline end to end.
- **Implemented:** Prompt sampling, treatment/control pairs, mock/live modes, run manifest, failures, prompt caps, repetitions, token-cap override.
- **Caveat:** Mock validates software only. The current live attempt stopped early at Groq's daily-token limit.

### Phase 9 — Output deviation and correctness

- **Goal:** Compare generated responses and answer outcomes.
- **Implemented:** Normalized output character distance, control deviations, and heuristic correctness checks for supported categories.
- **Caveat:** Character distance is not meaning. Correctness checks are not expert grading; code generation is not evaluated by the pilot helper.

### Phase 10 — Sensitivity score

- **Goal:** Relate output change to input change.
- **Implemented:** Character-only and composite-input sensitivity ratios, budget-filtered maxima, grouped summaries.
- **Formula:** `normalized output character distance / (0.5 × normalized character input distance + 0.5 × semantic embedding distance + 0.0001)`.
- **Caveat:** Ratios can inflate for small denominators; they are not probabilities, causal effects, or standalone robustness measures. Headline output deviation remains character-based.

### Input/output sensitivity formula

For pilot analysis:

```text
d_input_composite = 0.5 * d_character_normalized + 0.5 * d_semantic_embedding
sensitivity       = d_output_character_normalized / (d_input_composite + 0.0001)
```

- Syntactic distance is omitted because it is not implemented.
- Missing semantic input distance remains unavailable; it is not replaced with another metric.

## 4. How to run the demo (mock/offline)

### 4.1 Requirements

- **Terminal:** PowerShell, opened at the repository root.
- **Environment:** Use `.venv` if it is already set up.
- **First-time setup:** Otherwise create the environment and install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[huggingface,gemini,dev]"
```

- **Embedding model:** First use may load or download the configured sentence-transformer.
- **API usage:** `--mock` ensures prompt generations are not sent to an LLM provider.

### 4.2 Run a small demo

From the project root:

```powershell
.\.venv\Scripts\python.exe experiments\pilot_experiment.py `
  --mock --models openai/gpt-oss-20b --prompts-per-category 1 `
  --repetitions 1 --control-repetitions 1 `
  --output-dir results\demo
```

- **Sample:** Up to five prompts—one from each category.
- **Maximum scheduled pairs:** 30 before inapplicable candidates are skipped.

```text
5 prompts × (5 treatment operators × 1 repetition + 1 control pair) = 30 pairs
```

- **Maximum mock generations:** 60 (two generations per pair).
- **Actual count:** Lower if some perturbations are inapplicable.
- **Credentials:** No API credentials required.

### 4.3 Analyze the run

- **Run location:** The runner prints the new ID and directory. Example:

```text
results\demo\mock\pilot_mock_<id>\
```

- **Analyze an existing demo:** The example below analyzes the included run:

```powershell
.\.venv\Scripts\python.exe experiments\evaluate_experiment.py `
  --input results\demo\mock\pilot_mock_317408b8\raw_results.jsonl `
  --output-dir results\demo\analysis\pilot_mock_317408b8
```

- **For a new run:** Replace `pilot_mock_317408b8` in both paths with the printed ID.
- **Analysis files:**

```text
results\demo\analysis\<run-id>\sensitivity_analysis_summary.json
results\demo\analysis\<run-id>\evaluated_records.jsonl
```

### 4.4 What to show

- **`run_manifest.json`:** Mode, model/provider configuration, dataset hash, prompt IDs, category counts, token cap, embedding model, and run counts.
- **`raw_results.jsonl`:** Successful treatment/control pairs. Show original/perturbed prompts, operator/ID, input distances, outputs, token counts, and finish reasons.
- **Control record:** A `condition: "control"` pair compares two generations of the same prompt.
- **`sensitivity_analysis_summary.json`:** Output distances, control summaries, correctness transitions, budget-filtered maxima, and sensitivity summaries.
- **`evaluated_records.jsonl`:** Per-pair metrics and correctness fields.
- **`failed_trials.jsonl`:** Failed calls and any one-sided output; may be empty.

**Included demo run (`pilot_mock_317408b8`):**

- 5 prompts: 1 per category.
- 19 treatment pairs + 5 controls = 24 successful pairs.
- 6 inapplicable perturbations; no failed trials.
- Mean normalized output character distance: `0.1587`.
- Mean control distance: `0.0`.
- Correctness checks applicable to 15 pairs.
- **Interpretation:** Mock text is not output from the named LLM; do not present its correctness figures as model accuracy.

### Suggested professor walkthrough

1. **Research question:** Introduce the effect being studied—output changes under small prompt edits.
2. **Method:** Show one baseline prompt, one perturbation, and its measured input distances.
3. **Controls:** Explain how unchanged-prompt pairs help observe natural response variation.
4. **Analysis:** Show output deviation and the sensitivity formula.
5. **Evidence boundary:** State that this walkthrough is mock-tested software, not a live-model finding.

### 4.5 Optional analysis of output semantic metrics

- **Default:** Output character distance.
- **Optional:** `--use-semantic` also calculates output embedding metrics; it may load/download the embedding model.

```powershell
.\.venv\Scripts\python.exe experiments\evaluate_experiment.py `
  --input results\demo\mock\pilot_mock_317408b8\raw_results.jsonl `
  --output-dir results\demo\analysis\pilot_mock_317408b8_with_output_semantics `
  --use-semantic
```

- The output semantic measure is separate from semantic **input** distance, which the pilot already records.

## 5. Optional live-model execution

- **Demo requirement:** Live execution is not needed for a software presentation.
- **External calls:** Live execution sends prompts to a provider and may consume quota or incur costs.
- **Before running:** Confirm provider, local credential, model, token cap, and request budget.
- **Secret handling:** Never copy API keys into the repository or experiment outputs.

Example small live command:

```powershell
.\.venv\Scripts\python.exe experiments\pilot_experiment.py `
  --models openai/gpt-oss-20b --prompts-per-category 1 `
  --repetitions 1 --control-repetitions 1 --max-tokens 1024 `
  --output-dir results\pilot_experiment
```

- `openai/gpt-oss-20b` is configured through Groq in `config/models.yaml`.
- Maximum for the example: 60 generations before inapplicable skips.
- On Groq HTTP 429: the run stops for that model and retains completed records.
- Follow the retry window and quota; do not immediately repeat the full request plan.

## 6. Output files and reproducibility

- **Unique run directory:** Each pilot run gets a new directory, separated by execution mode.

```text
<output-dir>\
  mock|live\
    <experiment-id>\
      raw_results.jsonl
      failed_trials.jsonl
      run_manifest.json
      pilot_report.md
```

- **Analysis:** Written separately to the evaluator's `--output-dir`.
- **Manifest:** Records dataset SHA-256, selected IDs/category counts, provider/model, generation settings, token override, embedding model, and timestamps.
- **Separation:** Mock and live runs have separate directories.
- **Sampling:** Fixed file order, not randomized.
- **Reproduction:** Match the dataset hash, prompt IDs, model, and generation configuration.
- **Hosted models:** Reproducible configuration does not guarantee identical responses.

## 7. Evidence and limits

### Evidence levels

- **Implemented:** code and documentation exist.
- **Unit/integration tested:** automated tests exercise defined software behavior; the full suite most recently passed 198 tests.
- **Mock-tested:** the run format and pipeline execute without live model requests.
- **Live-observed:** actual provider responses and corresponding manifests/raw records exist.
- **Empirically validated:** requires sufficient, reviewed, controlled observations and an analysis supporting the research claim.

### Existing evidence

- **Current-code live run:** Groq `openai/gpt-oss-20b`, 1,024-token cap.
- **Stopped early:** HTTP 429 tokens-per-day limit after 9 complete pairs (7 treatments, 2 controls) across 2 math prompts.
- **Finish reasons:** All 18 were `stop`; no output reached the cap. This small sample does not resolve the earlier output-limit concern.
- **Earlier live artifact:** 50 prompts/150 pairs; lacks current controls, finish reasons, and semantic input distance.
- **Interpretation:** Keep the two live records separate. Neither establishes causality, broad model rankings, or semantic preservation.
- **Details:** [Work summary](./work_completed_summary.md)

## 8. Current project problems and remaining risks

- **Context:** These are known implementation and evidence limitations.
- **Presentation:** Explain these caveats alongside phase-completion labels.

### Research-method limitations

- **No adversarial optimizer:** the engine tries a finite set of predefined transformations. It does not search for or guarantee the maximum-output-change prompt.
- **Meaning is not guaranteed to be preserved:** small character distance, embedding similarity, and heuristic risk labels cannot prove semantic equivalence. Some edits can change task meaning.
- **Output deviation is primarily textual:** headline output metrics use normalized character distance. A large string difference can still express the same answer, and a small difference can encode a different answer.
- **Sensitivity ratios are scale-dependent:** a tiny input-distance denominator can make the ratio large. It is not a probability, causal effect, or standalone robustness score.
- **Controls are limited:** a control pair compares two generations of an unchanged prompt, but one repetition is not enough to characterize a model's natural variance. Controls are not currently used as a formal causal adjustment.
- **Coverage remains narrow:** pilot sampling is the first N rows in CSV order, not a random or stratified sample. One-model/one-prompt observations cannot support broad model or task-category rankings.
- **Correctness evaluation is preliminary:** reference-answer matching is heuristic for supported categories; code generation is not evaluated, and open-ended tasks need better rubrics or adjudication.

### Implementation and dataset limitations

- **Syntactic tree distance is missing:** the calculator remains unimplemented. Its weight is set to zero; syntactic budgets should not be described as enforced by that metric.
- **Dataset gold answers still need validation:** structural checks confirm populated fields, parseable metadata, and Python syntax, not the correctness or executability of every answer. Five targeted issues were corrected, but full independent review remains outstanding.
- **Embedding scores depend on the embedding model:** changing the sentence-transformer model can alter semantic distances. The selected model is recorded, but model-based similarity is not human semantic review.
- **Multiple experiment entry points:** `experiments/pilot_experiment.py` and `scripts/run_experiment.py` use different schemas and analysis tools. Use the paired lightweight evaluator described in this guide for the mock demo.
- **Provider and quota fragility:** live experiments depend on external provider availability, model identifiers, credentials, rate limits, and token/day budgets. A 429 can end a partial run; the runner records completed pairs and failed calls, not fabricated replacements.
- **Partial-run handling is not resume:** if a live experiment stops early, start a new run after checking quota. The current lightweight pilot does not resume a partial manifest automatically; rerunning may repeat calls already made.
- **Finish reason availability varies:** the provider may omit finish reasons. A `stop` reason is useful evidence of normal termination, but absence of a reason cannot verify completeness.
- **Reproducibility has limits:** the manifest records dataset hash, sample IDs, settings, and model metadata, but hosted model versions and provider behavior can change. Temperature zero does not guarantee identical hosted responses.

### Current live-evidence limitation

- **Current-code Groq attempt:** Stopped on tokens-per-day HTTP 429 after 9 complete pairs (7 treatments, 2 controls) across 2 math prompts.
- **Coverage:** Planned five-category coverage was not completed.
- **Earlier 150-pair artifact:** Predates current controls, finish reasons, and semantic-input measurements.
- **Conclusion:** Neither live dataset supports broad empirical conclusions. The mock demo is only a software demonstration.

### Priority next steps within Phases 1–10

1. Complete expert review of the baseline answers and execute code-reference tests.
2. Plan an affordable live request budget after provider quotas reset, then collect enough prompts and matched controls across categories.
3. Use randomized or otherwise justified sampling for confirmatory work, and record exclusions and sampling seeds.
4. Evaluate output meaning and task correctness with validated task-specific scoring and human adjudication where necessary.
5. Consider implementing syntactic tree distance only if the research protocol needs it; otherwise continue to exclude it and document its zero weight.
6. Analyze treatment results alongside control variation and report uncertainty at the prompt level, avoiding unsupported causal claims.

## 9. Running tests and dataset audit

- **Run the test suite:**

```powershell
.\.venv\Scripts\python.exe -m pytest --basetemp=.pytest-tmp -q
```

- **Run the structural baseline audit:**

```powershell
.\.venv\Scripts\python.exe experiments\validate_baseline_dataset.py
```

- **Audit output:** `data\baseline_dataset_audit.json`.
- **What it verifies:** Dataset structure and Python syntax of code references.
- **What it does not verify:** Correctness of every reference answer or functional behavior of the code.

## 10. Related documentation

- [Research methodology](./research_methodology.md)
- [Software architecture](./software_architecture.md)
- [Metrics reference](./metrics.md)
- [Pilot workflow guide](./pilot_study_workflow.md)
- [Work completed summary and live-pilot record](./work_completed_summary.md)
- [Dataset card](../data/dataset_card.md)
- [Baseline structural audit](../data/baseline_dataset_audit.json)
