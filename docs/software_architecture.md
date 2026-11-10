# Software Architecture: Adversarial Prompt Sensitivity Analysis

**Version:** 1.0  
**Date:** September 2026  
**Status:** Approved Design  

---

## 1. Architectural Philosophy

The system is designed around five core principles:

1. **Modularity** — Every concern is encapsulated in its own module or package. Adding a new LLM provider, perturbation type, or evaluation metric requires only adding a new file implementing a known interface; no core orchestration code needs to change.
2. **Reproducibility** — Every run is deterministic given a fixed configuration file and random seed. Experiment state is checkpointed so interrupted runs can be resumed.
3. **Separation of Concerns** — Data loading, perturbation, model inference, metric computation, and analysis are fully decoupled and communicate only through typed data schemas.
4. **Immutability of Results** — Every inference result is serialized to an append-only JSONL file immediately after production. Results are never mutated in-place.
5. **Observability** — Structured logging at every stage enables post-hoc debugging of any individual experiment run.

---

## 2. Directory Structure

```
adversarial-prompt-sensitivity/
│
├── docs/
│   ├── research_methodology.md          # Phase 1 approved methodology
│   └── software_architecture.md         # This document
│
├── config/
│   ├── default.yaml                     # Master default configuration
│   ├── models/
│   │   ├── llama_3_1_8b.yaml
│   │   ├── llama_3_1_70b.yaml
│   │   ├── qwen_2_5_7b.yaml
│   │   ├── qwen_2_5_coder_32b.yaml
│   │   ├── mistral_7b_v0_3.yaml
│   │   ├── gemini_1_5_flash.yaml
│   │   └── gemini_1_5_pro.yaml
│   ├── perturbations/
│   │   ├── surface.yaml
│   │   ├── lexical.yaml
│   │   ├── syntactic.yaml
│   │   └── structural.yaml
│   └── experiments/
│       ├── pilot_small.yaml             # Small pilot run for sanity-check
│       ├── full_experiment.yaml         # Full production experiment
│       └── ablation_temperature.yaml    # Temperature ablation study
│
├── src/
│   └── apsa/                            # Main Python package
│       ├── __init__.py
│       │
│       ├── data/                        # MODULE 1: Dataset Management
│       │   ├── __init__.py
│       │   ├── base_dataset.py
│       │   ├── gsm8k.py
│       │   ├── math_dataset.py
│       │   ├── humaneval.py
│       │   ├── mbpp.py
│       │   ├── squad_v2.py
│       │   ├── hotpotqa.py
│       │   ├── cnn_dailymail.py
│       │   ├── xsum.py
│       │   └── registry.py
│       │
│       ├── prompts/                     # MODULE 2: Prompt Generation
│       │   ├── __init__.py
│       │   ├── base_formatter.py
│       │   ├── reasoning_formatter.py
│       │   ├── code_formatter.py
│       │   ├── qa_formatter.py
│       │   ├── summarization_formatter.py
│       │   └── registry.py
│       │
│       ├── perturbations/               # MODULE 3: Prompt Perturbation
│       │   ├── __init__.py
│       │   ├── base_perturbation.py
│       │   ├── surface/
│       │   │   ├── __init__.py
│       │   │   ├── capitalization.py
│       │   │   ├── whitespace.py
│       │   │   └── punctuation.py
│       │   ├── lexical/
│       │   │   ├── __init__.py
│       │   │   ├── synonym.py
│       │   │   ├── substitution.py
│       │   │   ├── addition.py
│       │   │   └── deletion.py
│       │   ├── syntactic/
│       │   │   ├── __init__.py
│       │   │   └── rephrasing.py
│       │   ├── structural/
│       │   │   ├── __init__.py
│       │   │   └── reordering.py
│       │   ├── random_edit.py
│       │   └── registry.py
│       │
│       ├── providers/                   # MODULE 4: LLM Providers
│       │   ├── __init__.py
│       │   ├── base_provider.py
│       │   ├── huggingface_provider.py
│       │   ├── gemini_provider.py
│       │   ├── openai_provider.py
│       │   └── registry.py
│       │
│       ├── execution/                   # MODULE 5: Experiment Execution
│       │   ├── __init__.py
│       │   ├── engine.py
│       │   ├── trial.py
│       │   ├── scheduler.py
│       │   ├── checkpoint.py
│       │   └── budget_enforcer.py
│       │
│       ├── metrics/                     # MODULES 6, 7, 8: All Metrics
│       │   ├── __init__.py
│       │   ├── input_distance/
│       │   │   ├── __init__.py
│       │   │   ├── lexical.py
│       │   │   ├── syntactic.py
│       │   │   └── semantic.py
│       │   ├── output_distance/
│       │   │   ├── __init__.py
│       │   │   ├── textual.py
│       │   │   ├── semantic.py
│       │   │   └── llm_judge.py
│       │   ├── functional/
│       │   │   ├── __init__.py
│       │   │   ├── exact_match.py
│       │   │   ├── code_execution.py
│       │   │   └── schema_validation.py
│       │   ├── sensitivity.py
│       │   └── composite.py
│       │
│       ├── analysis/                    # MODULE 9: Statistical Analysis
│       │   ├── __init__.py
│       │   ├── hypothesis_testing.py
│       │   ├── effect_size.py
│       │   ├── regression.py
│       │   └── extreme_value.py
│       │
│       ├── visualization/               # MODULE 10: Visualization
│       │   ├── __init__.py
│       │   ├── sensitivity_heatmap.py
│       │   ├── distribution_plots.py
│       │   ├── phase_transition.py
│       │   ├── task_comparison.py
│       │   └── report_generator.py
│       │
│       ├── config/                      # MODULE 11: Configuration
│       │   ├── __init__.py
│       │   ├── loader.py
│       │   ├── schema.py
│       │   └── experiment_config.py
│       │
│       ├── logging_/                    # MODULE 12: Logging
│       │   ├── __init__.py
│       │   └── structured_logger.py
│       │
│       ├── reproducibility/             # MODULE 13: Reproducibility
│       │   ├── __init__.py
│       │   ├── seed_manager.py
│       │   ├── env_snapshot.py
│       │   └── config_hash.py
│       │
│       └── storage/                     # MODULE 14: Results Storage
│           ├── __init__.py
│           ├── schema.py
│           ├── writer.py
│           └── reader.py
│
├── scripts/
│   ├── run_experiment.py
│   ├── run_analysis.py
│   ├── run_visualization.py
│   └── verify_environment.py
│
├── tests/
│   ├── unit/
│   │   ├── test_perturbations.py
│   │   ├── test_metrics.py
│   │   ├── test_storage.py
│   │   └── test_config.py
│   └── integration/
│       ├── test_trial_execution.py
│       └── test_end_to_end_pilot.py
│
├── results/                             # Auto-created at runtime; git-ignored
│   └── {experiment_id}/
│       ├── experiment_config.yaml
│       ├── env_manifest.json
│       ├── runs.jsonl
│       ├── metrics.jsonl
│       ├── analysis/
│       │   ├── hypothesis_tests.json
│       │   ├── effect_sizes.json
│       │   └── glmm_results.json
│       └── figures/
│           ├── sensitivity_heatmap.png
│           ├── distribution_plots.png
│           └── report.html
│
├── pyproject.toml
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## 3. Module Responsibilities

### 3.1 `apsa/data/` — Dataset Management

**Responsibility**: Load, validate, and yield standardized dataset items from benchmark corpora.

- `BaseDataset`: Abstract class with `load(split, sample_size, seed) → list[DatasetItem]` and a `task_category` property.
- Each concrete loader fetches from HuggingFace `datasets` or a local cache and normalizes fields into `DatasetItem`.
- Gold labels for functional evaluation are included in `DatasetItem.gold_answer`.
- `registry.py` provides a `get_dataset(name: str) → BaseDataset` factory.

**Typed Output**:
```
DatasetItem(id, task_category, input_text, gold_answer, metadata)
```

---

### 3.2 `apsa/prompts/` — Prompt Generation

**Responsibility**: Convert a raw `DatasetItem` into a formatted prompt string using a standardized template per task category.

- `BaseFormatter`: Abstract class with `format(item: DatasetItem, system_prompt: str) → PromptRecord`.
- Formatters enforce the fixed system prompt `"You are a precise academic assistant. Follow instructions exactly."`.
- `registry.py` provides `get_formatter(task_category: str) → BaseFormatter`.

**Typed Output**:
```
PromptRecord(original_prompt, system_prompt, task_category, dataset_item_id)
```

---

### 3.3 `apsa/perturbations/` — Prompt Perturbation

**Responsibility**: Apply a single, typed perturbation operator to a prompt string and return the perturbed string. Operators are stateless and budget-aware.

- `BasePerturbation`: Abstract class with `apply(prompt: str, config: PerturbationConfig) → str | None`. Returns `None` if the perturbation cannot be applied (e.g., no applicable words found).
- Budget enforcement happens in `execution/budget_enforcer.py` after metric computation, not inside the perturbation operator.
- `random_edit.py` implements the `C_random` control condition.
- `registry.py`: `get_perturbation(name: str) → BasePerturbation`.

**Operator Taxonomy**:

| Tier | Type | Class |
|:---|:---|:---|
| Surface | `capitalization` | `surface/capitalization.py` |
| Surface | `whitespace` | `surface/whitespace.py` |
| Surface | `punctuation` | `surface/punctuation.py` |
| Lexical | `synonym` | `lexical/synonym.py` |
| Lexical | `substitution` | `lexical/substitution.py` |
| Lexical | `addition` | `lexical/addition.py` |
| Lexical | `deletion` | `lexical/deletion.py` |
| Syntactic | `rephrasing` | `syntactic/rephrasing.py` |
| Structural | `reordering` | `structural/reordering.py` |
| Control | `random_edit` | `random_edit.py` |

---

### 3.4 `apsa/providers/` — LLM Providers

**Responsibility**: Provide a uniform `generate(messages, config) → GenerationResult` interface over all LLM backends. All provider-specific API logic (authentication, retries, rate limiting) is isolated here.

- `BaseLLMProvider`: Abstract with `generate()`, `get_model_id()`, `count_tokens()`.
- `HuggingFaceProvider`: Wraps `transformers` / `vllm`. Handles device placement, tokenizer, and seed.
- `GeminiProvider`: Wraps `google-generativeai`. Reads `GEMINI_API_KEY` from environment — **never from config files**.
- `OpenAIProvider`: Stub for future OpenAI-compatible endpoints. Reads `OPENAI_API_KEY` from environment.
- All providers use `tenacity` for automatic retry with exponential backoff on transient API errors.
- `registry.py`: `get_provider(model_config: ModelConfig) → BaseLLMProvider`.

**Typed Output**:
```
GenerationResult(output_text, model_name, gen_config, token_count, latency_ms)
```

---

### 3.5 `apsa/execution/` — Experiment Execution

**Responsibility**: Orchestrate the complete experiment. The `ExperimentEngine` coordinates datasets, perturbations, providers, and metric computation without containing any domain logic itself.

**`ExperimentEngine.run(config: ExperimentConfig)`** sequence:
1. Snapshot environment → `results/{experiment_id}/env_manifest.json`
2. Freeze and write config → `results/{experiment_id}/experiment_config.yaml`
3. Set global random seed via `SeedManager`
4. Enumerate all `(dataset_item, model, perturbation_type)` trial combinations via `Scheduler`
5. For each trial, call `TrialRunner.execute()`
6. Write `ExperimentRun` to JSONL via `ResultWriter`
7. Save checkpoint after every N trials

**`TrialRunner.execute()`** sequence:
1. Format prompt → `PromptRecord`
2. Generate baseline output `Y = M(X)` at T=0.0 and N=5 repeats at T=0.7
3. Apply perturbation operator → candidate `X'`
4. Compute input distance metrics `(d_lex_in, d_syn_in, d_sem_in)`
5. Validate against epsilon budget (discard and log if violated)
6. Generate perturbed output `Y' = M(X')`
7. Compute all output distance metrics
8. Run functional evaluation
9. Compute composite `D_out` and sensitivity coefficient `S`
10. Return complete `ExperimentRun` record

**`Scheduler`**: Generates the Cartesian product trial queue from the experiment config matrix. Supports concurrent execution via `concurrent.futures.ThreadPoolExecutor`.

**`CheckpointManager`**: Tracks completed `run_id`s in `results/{experiment_id}/checkpoint.txt`; skips on resume.

**`BudgetEnforcer`**: Takes computed `InputDistanceMetrics` and `EpsilonBudget`; returns `bool`. Logs violations at `WARNING`.

---

### 3.6 `apsa/metrics/input_distance/` — Input-Distance Calculation

**Responsibility**: Compute the three-dimensional input distance vector between an original and perturbed prompt.

- `lexical.py` — `LexicalDistanceCalculator`:
  - Normalized character Levenshtein: `edit(X, X') / max(|X|, |X'|)`
  - Normalized word Levenshtein: `word_edit(X, X') / max(|X_w|, |X'_w|)`
  - Bigram Jaccard distance: `1 - |G(X) ∩ G(X')| / |G(X) ∪ G(X')|`
- `syntactic.py` — reserved interface/stub; `compute()` is not implemented. Its composite-input weight is zero until a validated tree-distance implementation is available.
- `semantic.py` — `SemanticDistanceCalculator`: Cosine distance between `sentence-transformers` embeddings (`all-mpnet-base-v2`).

**Typed Output**:
```
InputDistanceMetrics(
  lexical_char_levenshtein,
  lexical_word_levenshtein,
  lexical_jaccard_bigram,
  syntactic_tree_edit_distance,
  semantic_cosine_distance
)
```

---

### 3.7 `apsa/metrics/output_distance/` — Output Distance Calculation

**Responsibility**: Compute the multi-level output divergence between `Y` and `Y'`.

- `textual.py` — `TextualDistanceCalculator`: Normalized Levenshtein, ROUGE-1/2/L, BLEU, token Jaccard.
- `semantic.py` — `SemanticOutputDistanceCalculator`: BERTScore F1 disparity (1 − BERTScore_F1), sentence-embedding cosine distance.
- `llm_judge.py` — `LLMJudgeScorer`: Calls a judge model (via `providers/` abstraction) to rate semantic divergence 1–5. Default judge is a local model to avoid external API cost.

**Typed Output**:
```
OutputDistanceMetrics(
  textual_levenshtein, rouge_1_f1, rouge_2_f1, rouge_l_f1,
  bleu_score, token_jaccard,
  semantic_bertscore_f1_disparity, semantic_embedding_cosine,
  llm_judge_score_delta
)
```

---

### 3.8 `apsa/metrics/functional/` — Output Evaluation

**Responsibility**: Task-specific functional evaluation — did the perturbation cause a categorical failure?

- `exact_match.py`: Extracts numerical/short-form answers from `Y` and `Y'`; computes EM failure indicator for math/QA.
- `code_execution.py`: Sandboxes Python code from `Y` and `Y'` in a subprocess with timeout; returns Pass@1 delta.
- `schema_validation.py`: Validates `Y'` as JSON against the expected schema when `Y` is valid JSON.

**Typed Output**:
```
FunctionalMetrics(applicable, original_pass, perturbed_pass, functional_failure)
```

---

### 3.9 `apsa/metrics/sensitivity.py` & `composite.py`

- `SensitivityCalculator.compute(input_dist, output_dist, weights) → float`:
  - Computes `S = D_out / max(η, d_input_composite)`
  - `d_input_composite = α·d_lex + β·d_sem + γ·d_syn`
- `CompositeOutputDivergence.compute(output_metrics, functional, weights) → float`:
  - `D_out = w1·d_text + w2·d_sem + w3·Δf_task`

---

### 3.10 `apsa/analysis/` — Statistical Analysis

**Responsibility**: All statistical analysis over aggregated `runs.jsonl` data. Runs post-hoc; does not require re-running experiments.

- `hypothesis_testing.py`: Wilcoxon Signed-Rank tests (paired baseline vs. treatment); Kruskal-Wallis H across perturbation categories and task domains. Uses `scipy.stats`.
- `effect_size.py`: Cliff's Delta and Cohen's d.
- `regression.py`: GLMM fitting: `D_out ~ β0 + β1·d_lex + β2·d_sem + β3·Type + β4·Task + β5·Model + (Type×Model) + u_prompt + ε`. Uses `statsmodels` or `pymer4`.
- `extreme_value.py`: Fits Generalized Extreme Value (GEV) distribution to top-5th-percentile `S` values using `scipy.stats.genextreme`.

---

### 3.11 `apsa/visualization/` — Visualization

**Responsibility**: Produce all publication-quality figures from results and analysis outputs.

- `sensitivity_heatmap.py`: Model × perturbation-type heatmap of mean `S` values.
- `distribution_plots.py`: Violin/box plots of `S` distributions per model and per task.
- `phase_transition.py`: Scatter plots of `d_input_composite` vs. `D_out` per model.
- `task_comparison.py`: Cross-task functional failure rate bar charts.
- `report_generator.py`: Assembles all figures + statistical tables into a self-contained HTML report via `jinja2`.

Uses `matplotlib`, `seaborn`, and `plotly`.

---

### 3.12 `apsa/config/` — Configuration

**Responsibility**: Load, merge, and validate all YAML configs into typed Python objects.

- `loader.py`: Loads YAML, deep-merges with defaults, supports `${ENV_VAR}` substitution for values.
- `schema.py`: Pydantic `BaseModel` definitions for `ModelConfig`, `PerturbationConfig`, `GenerationConfig`, `MetricWeights`, `EpsilonBudget`.
- `experiment_config.py`: Top-level `ExperimentConfig` aggregating all sub-configs.

---

### 3.13 `apsa/logging_/` — Logging

**Responsibility**: Single structured JSON logger used across all modules. Trailing underscore avoids collision with stdlib `logging`.

- `structured_logger.py`: Configures stdlib `logging` with a JSON formatter. Provides `get_logger(name) → Logger` factory. Every log record includes `timestamp`, `level`, `module`, `experiment_id`, `run_id`, `event`.

---

### 3.14 `apsa/reproducibility/` — Reproducibility

**Responsibility**: Guarantee full experimental reproducibility.

- `seed_manager.py`: `set_global_seed(seed)` — calls `random.seed`, `numpy.random.seed`, `torch.manual_seed`, `torch.cuda.manual_seed_all`, passes `seed` to API calls.
- `env_snapshot.py`: `capture_environment() → dict` — Python version, OS, all pip packages, CUDA version, GPU info, Git commit hash.
- `config_hash.py`: `hash_config(config) → str` — SHA-256 of the fully-resolved, sorted ExperimentConfig JSON. First 8 hex chars used in `experiment_id`.

---

### 3.15 `apsa/storage/` — Results Storage

**Responsibility**: Serialize, persist, and read experiment results.

- `schema.py`: Pydantic model `ExperimentRun` matching the JSONL schema from methodology §14 (extended with additional fields).
- `writer.py`: `ResultWriter` — append-only JSONL writer; each `write(run)` call serializes and flushes one line. Thread-safe via `threading.Lock`.
- `reader.py`: `ResultReader` — streams `ExperimentRun` records from a JSONL file; supports filtering by `model_name`, `task_category`, `perturbation_type`.

---

## 4. Data Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     ExperimentEngine.run()                                  │
│                                                                             │
│  Config Load → Env Snapshot → Seed Set → Trial Queue → Execute Trials      │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                               TrialRunner.execute()
                                       │
    ┌──────────────┐          ┌────────▼──────────┐
    │ DataLoader   │─DataItem▶│ PromptFormatter   │
    └──────────────┘          └────────┬──────────┘
                                       │ PromptRecord
                              ┌────────▼──────────┐
                              │  LLM Provider     │─── Y = M(X)
                              └────────┬──────────┘
                                       │
                              ┌────────▼──────────┐
                              │  Perturbation     │─── X'
                              │  Operator         │
                              └────────┬──────────┘
                                       │
                              ┌────────▼──────────┐
                              │ Input Distance    │─── d_lex, d_syn, d_sem
                              │ Calculator        │
                              └────────┬──────────┘
                                       │
                              ┌────────▼──────────┐
                              │ Budget Enforcer   │─── reject if ε violated
                              └────────┬──────────┘
                                       │ valid X'
                              ┌────────▼──────────┐
                              │  LLM Provider     │─── Y' = M(X')
                              └────────┬──────────┘
                                       │
          ┌─────────────────────────── │ ──────────────────────────────┐
          │  Metric Pipeline           │                               │
          │  ┌──────────────┐  ┌───────▼──────────┐  ┌─────────────┐  │
          │  │ OutputDist.  │  │ FunctionalEval   │  │ Sensitivity │  │
          │  │ (text+sem+   │  │ (EM/code/schema) │  │ Coefficient │  │
          │  │  llm_judge)  │  └──────────────────┘  └─────────────┘  │
          │  └──────────────┘                                          │
          └───────────────────────────────────────────────────────────┘
                                       │ ExperimentRun
                              ┌────────▼──────────┐
                              │ ResultWriter      │─── results/{id}/runs.jsonl
                              └───────────────────┘


─── POST-EXPERIMENT ANALYSIS (separate CLI call) ────────────────────────────

  ResultReader
      │
      ├── StatisticalAnalysis → analysis/*.json
      ├── VisualizationEngine → figures/*.png
      └── ReportGenerator    → report.html
```

---

## 5. Configuration Design

### 5.1 Top-Level `config/default.yaml`

```yaml
experiment:
  name: "adversarial_prompt_sensitivity"
  description: ""
  seed: 42
  max_workers: 4

generation:
  temperature_deterministic: 0.0
  temperature_stochastic: 0.7
  top_p: 0.95
  max_tokens: 1024
  n_stochastic_repeats: 5

epsilon_budget:
  lexical_char_normalized: 0.10
  lexical_word_normalized: 0.15
  semantic_cosine: 0.05
  syntactic_ted_normalized: 0.20

metric_weights:
  w1_textual: 0.33
  w2_semantic: 0.34
  w3_functional: 0.33
  eta: 0.0001

composite_input_weights:
  alpha_lexical: 0.50
  beta_semantic: 0.50
  gamma_syntactic: 0.00

datasets:
  - name: gsm8k
    split: test
    sample_size: 100
  - name: humaneval
    split: test
    sample_size: 50

models:
  - config_file: config/models/gemini_1_5_flash.yaml
  - config_file: config/models/llama_3_1_8b.yaml

perturbations:
  - type: capitalization
    config_file: config/perturbations/surface.yaml
  - type: synonym
    config_file: config/perturbations/lexical.yaml
  - type: random_edit

system_prompt: "You are a precise academic assistant. Follow instructions exactly."

storage:
  results_dir: "results"
  log_level: "INFO"

judge_model:
  provider: huggingface
  model_id: "mistralai/Mistral-7B-Instruct-v0.3"
```

### 5.2 Model Config Example — `config/models/gemini_1_5_flash.yaml`

```yaml
model_id: "gemini-1.5-flash"
display_name: "Gemini 1.5 Flash"
provider: gemini
api_key_env_var: "GEMINI_API_KEY"   # Key read from environment — never stored here
context_window: 1000000
parameter_scale: "undisclosed"
type: frontier_light
tokenizer_id: null
```

### 5.3 Model Config Example — `config/models/llama_3_1_8b.yaml`

```yaml
model_id: "meta-llama/Meta-Llama-3.1-8B-Instruct"
display_name: "LLaMA 3.1 8B Instruct"
provider: huggingface
api_key_env_var: "HF_TOKEN"
device: "auto"
dtype: "bfloat16"
context_window: 131072
parameter_scale: "8B"
type: dense_instruct
tokenizer_id: "meta-llama/Meta-Llama-3.1-8B-Instruct"
vllm: false
```

---

## 6. Result Schema

Each line in `results/{experiment_id}/runs.jsonl` is one JSON object:

```jsonc
{
  // ── Identity ──────────────────────────────────────────────────────────────
  "experiment_id":      "apsa_20260911_abc12def_42",
  "run_id":             "run_00001_llama8b_cap_gsm8k_item042",
  "timestamp":          "2026-09-11T14:32:10.123Z",
  "condition":          "treatment",   // "baseline" | "random_control" | "treatment"

  // ── Provenance ────────────────────────────────────────────────────────────
  "model_name":         "meta-llama/Meta-Llama-3.1-8B-Instruct",
  "task_category":      "mathematical_reasoning",
  "perturbation_type":  "capitalization",
  "dataset_item_id":    "gsm8k_test_042",

  // ── Generation Config (frozen snapshot) ───────────────────────────────────
  "generation_config": {
    "temperature": 0.0,
    "top_p": 0.95,
    "max_tokens": 1024,
    "seed": 42
  },

  // ── Prompts ───────────────────────────────────────────────────────────────
  "original_prompt":    "Solve: Janet's ducks lay 16 eggs...",
  "perturbed_prompt":   "SOLVE: Janet's ducks LAY 16 eggs...",

  // ── Raw Outputs ───────────────────────────────────────────────────────────
  "original_output":    "Janet has 16 - 3 - 4 = 9 eggs...",
  "perturbed_output":   "I cannot assist with that.",
  "original_token_count":  128,
  "perturbed_token_count": 12,

  // ── Input Distance Vector ─────────────────────────────────────────────────
  "input_distance": {
    "lexical_char_levenshtein":       0.032,
    "lexical_word_levenshtein":       0.045,
    "lexical_jaccard_bigram":         0.051,
    "syntactic_tree_edit_distance":   0.0,
    "semantic_cosine_distance":       0.008
  },

  // ── Output Distance Vector ────────────────────────────────────────────────
  "output_distance": {
    "textual_levenshtein":            0.710,
    "rouge_1_f1":                     0.210,
    "rouge_2_f1":                     0.095,
    "rouge_l_f1":                     0.200,
    "bleu_score":                     0.063,
    "token_jaccard":                  0.780,
    "semantic_bertscore_f1_disparity":0.340,
    "semantic_embedding_cosine":      0.298,
    "llm_judge_score_delta":          3.0
  },

  // ── Functional Evaluation ─────────────────────────────────────────────────
  "functional_metrics": {
    "applicable":           true,
    "original_pass":        true,
    "perturbed_pass":       false,
    "functional_failure":   true
  },

  // ── Composite Scores ──────────────────────────────────────────────────────
  "composite_output_divergence":  0.449,
  "sensitivity_coefficient":      14.03,

  // ── Runtime Metadata ──────────────────────────────────────────────────────
  "original_latency_ms":  1230,
  "perturbed_latency_ms": 1185,
  "epsilon_budget_used": {
    "lexical_char_normalized":  0.032,
    "semantic_cosine":          0.008
  }
}
```

---

## 7. Experiment ID Strategy

```
apsa_{date}_{config_hash_8chars}_{seed}
```

| Component | Description | Example |
|:---|:---|:---|
| `apsa` | Fixed namespace prefix | `apsa` |
| `{date}` | `YYYYMMDD` of run start (UTC) | `20260911` |
| `{config_hash_8chars}` | First 8 hex chars of SHA-256 of the fully-resolved, serialized `ExperimentConfig` | `abc12def` |
| `{seed}` | Integer seed from config | `42` |

**Full example**: `apsa_20260911_abc12def_42`

**`run_id`** within an experiment:
```
run_{index:05d}_{model_short}_{perturbation_type}_{dataset}_{item_id}
```

**Properties**:
- **Collision detection**: Two runs with identical config + seed produce the same `experiment_id`, flagging accidental duplication.
- **Resume safety**: Interrupted runs append to the same JSONL under the same `experiment_id`.
- **Human-readability**: `run_id` is sortable and self-describing.

---

## 8. Logging Strategy

### 8.1 Log Levels

| Level | Usage |
|:---|:---|
| `DEBUG` | Intermediate perturbation candidates, token-level details |
| `INFO` | Trial start/end, metric values, checkpoint saves |
| `WARNING` | Budget violations (perturbation rejected), API retries |
| `ERROR` | API call failures, metric errors (run skipped with record written) |
| `CRITICAL` | Unrecoverable state (results directory write failure) |

### 8.2 Log Format (Structured JSON per line)

```json
{
  "timestamp": "2026-09-11T14:32:10.123Z",
  "level": "INFO",
  "module": "apsa.execution.trial",
  "experiment_id": "apsa_20260911_abc12def_42",
  "run_id": "run_00001_llama8b_cap_gsm8k_item042",
  "event": "trial_completed",
  "sensitivity_coefficient": 14.03,
  "duration_ms": 2415
}
```

### 8.3 Log Destinations

| Destination | Level Filter | Format |
|:---|:---|:---|
| Console (stdout) | `INFO`+ | Human-readable, colorized via `rich` |
| `results/{id}/experiment.log` | `DEBUG`+ | Structured JSON, one record per line |
| `results/{id}/errors.log` | `ERROR`+ | Structured JSON, for rapid post-run inspection |

### 8.4 Observability Invariant

Every `TrialRunner.execute()` call emits exactly:
1. `trial_started` — `INFO` — with `run_id`, model name, perturbation type, dataset item.
2. `trial_completed` or `trial_failed` — `INFO` / `ERROR` — with duration, key metric values.

This guarantees a complete audit trail even if the process is killed mid-run.

---

## 9. Abstract Interfaces

### `BaseLLMProvider`
```python
class BaseLLMProvider(ABC):
    @abstractmethod
    def generate(self, messages: list[Message], config: GenerationConfig) -> GenerationResult: ...
    @abstractmethod
    def get_model_id(self) -> str: ...
    @abstractmethod
    def count_tokens(self, text: str) -> int: ...
```

### `BaseDataset`
```python
class BaseDataset(ABC):
    @abstractmethod
    def load(self, split: str, sample_size: int | None, seed: int) -> list[DatasetItem]: ...
    @property
    @abstractmethod
    def task_category(self) -> TaskCategory: ...
```

### `BasePerturbation`
```python
class BasePerturbation(ABC):
    @abstractmethod
    def apply(self, prompt: str, config: PerturbationConfig) -> str | None: ...
    @property
    @abstractmethod
    def perturbation_type(self) -> str: ...
```

### `BaseFormatter`
```python
class BaseFormatter(ABC):
    @abstractmethod
    def format(self, item: DatasetItem, system_prompt: str) -> PromptRecord: ...
```

---

## 10. Dependency Overview

| Library | Purpose | Module |
|:---|:---|:---|
| `pydantic` | Config & schema validation | `config/`, `storage/` |
| `pyyaml` | YAML loading | `config/loader.py` |
| `datasets` (HF) | Dataset loading | `data/` |
| `transformers` | HuggingFace model inference | `providers/huggingface_provider.py` |
| `vllm` (optional) | Fast local LLM inference | `providers/huggingface_provider.py` |
| `google-generativeai` | Gemini API | `providers/gemini_provider.py` |
| `openai` | OpenAI-compatible API | `providers/openai_provider.py` |
| `python-Levenshtein` | Edit distance | `metrics/input_distance/lexical.py` |
| `nltk` | Tokenization, BLEU | `metrics/` |
| `spacy` | Dependency parsing | `metrics/input_distance/syntactic.py` |
| `sentence-transformers` | Semantic embeddings | `metrics/*/semantic.py` |
| `bert-score` | BERTScore F1 | `metrics/output_distance/semantic.py` |
| `rouge-score` | ROUGE metrics | `metrics/output_distance/textual.py` |
| `scipy` | Statistical tests, EVT | `analysis/` |
| `statsmodels` | GLMM regression | `analysis/regression.py` |
| `matplotlib` / `seaborn` | Static publication plots | `visualization/` |
| `plotly` | Interactive figures | `visualization/` |
| `jinja2` | HTML report templating | `visualization/report_generator.py` |
| `rich` | Console log colorization | `logging_/structured_logger.py` |
| `click` | CLI argument parsing | `scripts/` |
| `tenacity` | API retry with backoff | `providers/` |
| `pytest` | Unit & integration tests | `tests/` |

---

## 11. Extension Points

| Concern | How to Extend | Files Touched |
|:---|:---|:---|
| New LLM provider | Subclass `BaseLLMProvider` | New file in `providers/`; add to `providers/registry.py` |
| New perturbation type | Subclass `BasePerturbation` | New file in appropriate `perturbations/` tier subfolder; add to `perturbations/registry.py` |
| New dataset | Subclass `BaseDataset` | New file in `data/`; add to `data/registry.py` |
| New metric | Add function/class | Appropriate `metrics/` subpackage; call from `execution/trial.py` |
| New statistical test | Add function | `analysis/hypothesis_testing.py` |
| New visualization | Add module | `visualization/`; call from `report_generator.py` |

> **No changes to `ExperimentEngine` or `TrialRunner` are required for any of the above extensions.**
