# Adversarial Prompt Sensitivity Analysis (APSA)
## Comprehensive Research Progress, Technical Methodology, and Empirical Results Report (Phases 1–10)

**Project Title:** Adversarial Prompt Sensitivity Analysis: Studying Maximum Output Changes from Minimal Prompt Perturbations  
**Author / Researcher:** Aditya Giri  
**Supervisor / Professor:** Academic Research Advisor  
**Project Repository:** `adversarial-prompt-sensitivity`  
**Current Milestone:** Phase 1–10 framework implemented; main empirical study remains pending  
**Date:** November 6, 2026  
**Status:** Software tests, mock pipeline checks, and limited live-pilot evidence are reported separately; no new research phase is started here.

---

## Executive Summary

APSA investigates how LLM outputs respond to controlled prompt changes. A change that appears small is not automatically semantically inconsequential; the framework must measure input differences and assess semantic risk rather than assume equivalence.

The project is designed to study prompt sensitivity as a constrained search problem: maximize output divergence while bounding input distance. The current finite perturbation engine generates candidates; it does not yet optimize or guarantee a worst-case perturbation.

Across **Phases 1 through 10**, the repository now contains the following implemented components and research artifacts:
1. **Theoretical Formalization (Phase 1):** Formulated the primary research question, five sub-questions (RQ1–RQ5), and formal hypotheses ($H_1$–$H_5$) governing perturbation susceptibility, task vulnerability, and non-linear phase transitions.
2. **Modular Software Architecture (Phase 2):** Implemented a modular Python research codebase (`apsa`) with distinct perturbation, metric, provider, execution, and analysis components.
3. **Baseline Dataset (Phase 3):** The repository contains **100 prompts** across 5 task domains with expected answers and metadata. A structural audit confirms 20 rows per category and no missing fields; targeted answer review corrected five prompt/reference issues. Code snippets parse but have not been execution-tested, and independent expert review remains pending.
4. **Perturbation Engine (Phase 4):** Developed **10 programmatic perturbation operators** spanning surface-level (punctuation, capitalization, whitespace), lexical-level (addition, deletion, substitution, synonymy), and structural-level (instruction reordering) edits, supported by rule-based heuristic semantic preservation risk detectors.
5. **Input Distance Metrics & Budget Enforcement (Phase 5):** Implemented multi-dimensional input distance calculators—normalized Wagner-Fischer character edit distance, token-level Levenshtein distance, and high-dimensional SentenceTransformer embedding cosine distance—enforced by a multi-constraint `BudgetEnforcer`.
6. **Multi-Provider LLM Interface (Phase 6):** Constructed a unified, credential-isolated provider abstraction supporting commercial and open-weight models (`OpenAIProvider`, `GeminiProvider`, `GroqProvider`, and an offline `MockProvider`) featuring exponential backoff retries via `tenacity`.
7. **Control Experimentation (Phase 7):** Control-run tooling and selected repeated-prompt records exist. They are exploratory and do not establish a universal noise threshold.
8. **Pilot Experimentation Pipeline (Phase 8):** One live-model artifact contains **150 successful paired records** from `openai/gpt-oss-20b`. Separate mock runs exercise the pipeline but are not model observations. Several operator/prompt combinations were inapplicable and returned no perturbation.
9. **Output Deviation Metrics (Phase 9):** The current evaluator measures normalized character output distance, optional output semantics, and supported-category correctness transitions. The historical live-pilot analysis below does not include correctness flips or embedding-based semantic input distance.
10. **Sensitivity Scoring (Phase 10):** Sensitivity ratios and budget-filtered maxima are implemented. The current pilot uses measured character and embedding input distances with zero syntactic weight; statistics remain descriptive, not inferential or baseline-corrected.
11. **Software Verification:** Automated tests cover unit and mock-pipeline behavior. A passing test suite verifies software behavior, not scientific validity.

### Highlight Empirical Findings
- **Observed classification output change:** One pilot case (`CLASS-002`, punctuation) had character input distance 0.00588, character output distance 0.8333, and descriptive sensitivity ratio 139.31. This is a single-model observation, not a general causal conclusion.
- **Descriptive live-pilot statistics:** Across 150 paired records, mean normalized character output distance was 0.2816 (median 0.1821; record-level 95% interval [0.2301, 0.3331]). Of the 300 responses, 167 report exactly the configured 256-token ceiling (81 original, 86 perturbed); finish reasons were not stored, so truncation is possible but cannot be confirmed. These statistics may therefore be censored and must be re-measured with a higher output limit and finish-reason capture. The interval also does not adjust for repeated prompts, semantic validity, or control variation.
- **Character-distance budget maxima:** The maximum observed normalized output character distance was 1.0000 among records with normalized character input distance ≤ 0.10 and ≤ 0.05. These thresholds do not enforce semantic preservation or correctness, and the output ceiling may affect these maxima.

The live-only reanalysis is stored at `results/pilot_experiment/analysis/live_model_pilot_1793047745/sensitivity_analysis_summary.json`. The existing `results/pilot_experiment/analysis/sensitivity_analysis_summary.json` analyzes 1,152 mock records and must not be cited as live-model evidence. Historical risk labels in raw pilot records use the earlier heuristic and are not semantic-equivalence judgments.

The pilot implementation has since been extended to write run-specific manifests, unchanged-prompt controls, provider finish reasons where available, semantic input distances, and category-specific heuristic correctness checks. One user-approved live run was attempted and stopped at a Groq HTTP 429 tokens-per-day limit. Its artifacts are under `results/pilot_experiment/live/pilot_live_cf5a4c9f/` with analysis under `results/pilot_experiment/analysis/live_pilot_cf5a4c9f/`. It recorded 7 treatment pairs and 2 controls across only two math prompts before the limit; all 18 finish reasons were `stop`, and none of the responses reached the 1,024-token cap. One response from the incomplete pair was not retained by that run's writer; the current code now preserves one-sided responses with failed trials, but the missing historical response cannot be reconstructed. This is a partial pipeline observation, not the planned expanded replication or a basis for general conclusions. See [the pilot workflow guide](./pilot_study_workflow.md) for current behavior and run commands.

---

## 1. Theoretical Framework & Research Objectives (Phase 1)

### 1.1 Mathematical Formulation of the Optimization Objective

Let $\mathcal{X}$ denote the space of natural language prompt strings. Let $P \in \mathcal{X}$ represent an unperturbed baseline prompt, and let $P' \in \mathcal{X}$ represent a perturbed prompt variant. Let $M$ denote a target Large Language Model operating under generation decoding parameters $\theta$ (with temperature fixed at $T = 0.0$ to minimize sampling noise). The generated output strings are denoted by $Y = M(P; \theta)$ and $Y' = M(P'; \theta)$.

The **Adversarial Prompt Sensitivity Problem** is formulated as a constrained non-linear optimization:

$$\max_{P' \in \mathcal{P}(P, \mathbf{\epsilon})} D_{\text{out}}\left( M(P; \theta), M(P'; \theta) \right)$$

subject to the multi-dimensional minimal perturbation constraint space $\mathcal{P}(P, \mathbf{\epsilon})$:

$$\mathcal{P}(P, \mathbf{\epsilon}) = \left\{ P' \in \mathcal{X} \;\middle|\; d_{\text{lex}}(P, P') \le \epsilon_{\text{lex}} \;\land\; d_{\text{sem}}(P, P') \le \epsilon_{\text{sem}} \;\land\; P' \neq P \right\}$$

Where:
- $d_{\text{lex}}(P, P') \in [0, 1]$ is the normalized Wagner-Fischer character edit distance:
  $$d_{\text{lex}}(P, P') = \frac{\text{Levenshtein}(P, P')}{\max(|P|, |P'|, 1)}$$
- $d_{\text{sem}}(P, P') \in [0, 1]$ is the semantic cosine distance between sentence embeddings $\mathbf{e}(P), \mathbf{e}(P')$:
  $$d_{\text{sem}}(P, P') = 1 - \frac{\mathbf{e}(P) \cdot \mathbf{e}(P')}{\|\mathbf{e}(P)\| \|\mathbf{e}(P')\|}$$
- $\mathbf{\epsilon} = (\epsilon_{\text{lex}}, \epsilon_{\text{sem}})$ is the strict perturbation budget (e.g., $\epsilon_{\text{lex}} \le 0.10$, $\epsilon_{\text{sem}} \le 0.05$).

### 1.2 Primary Research Questions & Hypotheses

| Research Question | Description | Formal Hypothesis |
| :--- | :--- | :--- |
| **RQ1: Perturbation Vulnerability** | Which perturbation category causes the highest mean and maximum output divergence? | **$H_1$:** Surface-level edits (punctuation, formatting) induce disproportionately high divergence in rigid instruction tasks due to tokenizer sensitivity. |
| **RQ2: Task Domain Fragility** | How does prompt sensitivity vary across reasoning, code generation, classification, and QA? | **$H_2$:** Tasks requiring structured or deterministic answers exhibit higher rates of functional failure than open-ended text generation. |
| **RQ3: Architectural Robustness** | Do larger model scales or reasoning-tuned architectures exhibit superior stability? | **$H_3$:** Parameter scale reduces average semantic drift, but instruction-reordering triggers localized fragility spikes in reasoning models. |
| **RQ4: Scaling Laws & Phase Transitions** | Does output divergence scale continuously or via non-linear phase transitions? | **$H_4$:** Divergence follows a step-function (phase transition) where isolated critical tokens flip outputs even when $d_{in} \le 0.01$. |
| **RQ5: Adversarial Search Optimization** | Can directed discrete search discover worse-case perturbations than random edits? | **$H_5$:** Targeted discrete search yields $\ge 3\times$ greater output divergence than randomized perturbation operators. |

---

## 2. Software Architecture & Engineering Design (Phase 2)

The software architecture is engineered under strict software design principles: separation of concerns, dependency injection, declarative YAML configuration, and interface-based polymorphism.

```
adversarial-prompt-sensitivity/
├── config/                  # Declarative configurations
│   ├── config.yaml          # Master configuration
│   ├── models.yaml          # LLM endpoints, temperatures, token limits
│   ├── perturbations.yaml   # Operator parameters & epsilon budgets
│   └── tasks.yaml           # Task category definitions & evaluation metrics
├── data/
│   └── baseline_prompts.csv # 100 curated benchmark prompts across 5 domains
├── docs/                    # Research documentation, formal specs, and reports
├── experiments/             # Execution pipelines
│   ├── control_experiment.py   # Baseline stochastic variance profiler
│   ├── pilot_experiment.py     # End-to-end pilot trial execution runner
│   └── evaluate_experiment.py  # Phases 9 & 10 metric evaluation processor
├── results/                 # Segregated experimental output artifacts
│   ├── control_experiment/  # Empirical baseline variance logs & statistics
│   └── pilot_experiment/    # Raw JSONL trial logs and processed analysis JSON
├── src/apsa/                # Core modular research package
│   ├── analysis/            # Sensitivity calculation & cohort statistics
│   ├── config/              # Robust Pydantic loader with BOM & modular support
│   ├── execution/           # Trial execution orchestrator & BudgetEnforcer
│   ├── llm_providers/       # OpenAI, Gemini, Groq, and Mock API abstraction
│   ├── metrics/             # Input Wagner-Fischer & Output deviation metrics
│   └── perturbations/       # 10 perturbation operators & registry engine
└── tests/                   # Automated pytest suite (171 tests)
    ├── integration/         # Offline end-to-end pipeline verification
    └── unit/                # Granular component verification
```

---

## 3. Benchmark Dataset Construction (Phase 3)

Reliable sensitivity measurement requires a clean, standardized, multi-task dataset. We curated `data/baseline_prompts.csv` containing exactly **100 baseline prompts** stratified uniformly into 5 core task domains (20 prompts each):

1. **Mathematical Reasoning (`MATH-001` to `MATH-020`):** Arithmetic, modular arithmetic, algebra, linear systems, geometry, combinatorics, and probability.
2. **Logical Reasoning (`LOGIC-001` to `LOGIC-020`):** Categorical syllogisms, propositional logic, Knights & Knaves puzzles, De Morgan's laws, and spatial reasoning.
3. **Question Answering (`QA-001` to `QA-020`):** Fact retrieval, historical events, scientific mechanisms, and reading comprehension.
4. **Text Classification (`CLASS-001` to `CLASS-020`):** Sentiment classification, news domain labeling, intent detection, and toxicity screening.
5. **Code Generation (`CODE-001` to `CODE-020`):** Python algorithm implementations (recursion, binary search, tree traversals, string parsing, dynamic programming).

Each entry contains:
- `prompt_id`: Unique identifier (e.g., `MATH-001`, `CLASS-002`).
- `task_category`: Standardized category enum.
- `original_prompt`: The pristine, human-crafted instruction.
- `expected_answer`: Ground-truth reference for functional correctness verification.
- `difficulty_level`: Stratified as `easy`, `medium`, or `hard`.
- `metadata`: JSON-encoded dictionary specifying evaluation criteria (e.g., `is_deterministic: true`, `eval_metric: exact_match`).

---

## 4. Perturbation Engine & Transformations (Phase 4)

The Perturbation Engine (`src/apsa/perturbations/`) implements a dynamic registry pattern, supporting deterministic seed-controlled modifications across three grammatical tiers:

```
                            Perturbation Operators
                                      │
         ┌────────────────────────────┼────────────────────────────┐
         ▼                            ▼                            ▼
   Surface-Level                Lexical-Level                Structural-Level
  ─────────────────            ─────────────────            ──────────────────
  • Punctuation                • Word Insertion             • Instruction Reordering
  • Capitalization             • Word Deletion              • Clause Permutation
  • Whitespace / Spacing       • Word Substitution
  • Char Substitution (Typos)  • Word Synonymy
```

### Heuristic Semantic Risk Detection
`SemanticFlagDetector` assigns a risk label and human-readable rule reasons for known edits (negation/contractions, polarity pairs, critical quantifiers, and numeric values). Other lexical and punctuation changes are at least `MODERATE`; only case/whitespace-only changes receive `MINIMAL`. These are conservative heuristics, not semantic-equivalence checks. A risk flag does not itself block a candidate or enforce an input budget; budget gating and task-specific assessment remain separate requirements.

---

## 5. Input Distance Metrics & Budget Enforcement (Phase 5)

`src/apsa/metrics/input_distance/` computes lexical and optional embedding-based distance metrics. These measurements quantify prompt changes; they do not prove semantic preservation:

1. **Wagner-Fischer Character Edit Distance:**
   $$d_{\text{char\_norm}} = \frac{\text{Levenshtein}(P, P')}{\max(|P|, |P'|, 1)}$$
2. **Word-Level Token Edit Distance:**
   $$d_{\text{word\_norm}} = \frac{\text{WordLevenshtein}(P, P')}{\max(\text{len}(P_{\text{tokens}}), \text{len}(P'_{\text{tokens}}), 1)}$$
3. **Semantic Cosine Distance:**
   Calculated using sentence embeddings from `sentence-transformers/all-MiniLM-L6-v2`:
   $$d_{\text{sem}} = 1 - \cos(\mathbf{e}(P), \mathbf{e}(P'))$$

### Multi-Constraint `BudgetEnforcer`
The primary `TrialRunner` now checks character, word, and embedding-based semantic budgets before making model requests. A missing semantic encoder raises an error rather than substituting lexical distance. Syntactic tree edit distance remains an unimplemented stub and is not enforced:
$$\text{IsValid}(P, P') \iff (d_{\text{char\_norm}} \le \epsilon_{\text{lex}}) \land (d_{\text{word\_norm}} \le \epsilon_{\text{word}}) \land (d_{\text{sem}} \le \epsilon_{\text{sem}})$$
Do not treat a trial as satisfying a dimension whose metric was not computed. The configured syntactic budget remains unsupported; the main study must not claim enforcement of the full three-dimensional budget.

---

## 6. Model Provider Abstraction (Phase 6)

A unified abstraction (`BaseLLMProvider`) shields the research pipeline from API idiosyncrasies:
- **`OpenAIProvider`:** Integrates OpenAI-compatible endpoints with support for models such as `openai/gpt-oss-20b`.
- **`GeminiProvider`:** Integrates Google Generative AI (`gemini-1.5-flash`, `gemini-1.5-pro`).
- **`GroqProvider`:** High-throughput inference for open-weight models (`llama-3.3-70b-versatile`, `qwen/qwen3.8-27b`).
- **`MockProvider`:** Deterministic, offline provider for lightning-fast testing and integration CI/CD without API consumption.
- **Reliability:** Built-in `tenacity` retry handler with exponential backoff on HTTP 429/503 errors.
- **Credential Protection:** Zero API keys are hardcoded; all secrets are dynamically injected from environment variables (`OPENAI_API_KEY`, `GROQ_API_KEY`, `GEMINI_API_KEY`).

---

## 7. Control Experiment: Baseline Stochastic Variance (Phase 7)

### 7.1 The Cutoff Fallacy in LLM Sensitivity Research
A fundamental methodological flaw in existing prompt sensitivity literature is the **Cutoff Fallacy**: assuming that any observed difference between an original output $Y$ and a perturbed output $Y'$ is caused entirely by the prompt modification. Modern LLMs exhibit non-zero stochastic variance even under greedy decoding ($T = 0.0$) due to floating-point non-associativity across distributed GPU tensor parallelism.

The repository includes control-experiment tooling and recorded repeated-prompt runs ($N = 3$ for the examples below). These observations are limited to the recorded prompts and settings; they do not establish a general noise floor or by themselves make the pilot causally attributable to perturbations.

### 7.2 Control Experiment Empirical Results

| Target Model | Task Category | Prompts Tested | Mean Levenshtein Distance | Mean Normalized Distance | Exact Match Ratio |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **`qwen/qwen3.8-27b`** | Mathematical Reasoning | 3 | **0.00** | **0.0000** | **100.0%** |
| **`openai/gpt-oss-20b`** | Mathematical Reasoning | 3 | **41.67** | **0.1074** | **66.7%** |

#### Control Experiment Analysis:
1. **`qwen/qwen3.8-27b`:** Exhibited **perfect determinism** ($D = 0.0000$, 100% exact match). Under identical prompts, every token matched bit-for-bit.
2. **`openai/gpt-oss-20b`:** Exhibited minor formatting stochasticity in multi-step arithmetic (`MATH-001`), producing different markdown layout choices while arriving at the identical numerical result (`$7.20`). Prompts `MATH-002` and `MATH-003` exhibited 100% exact matches ($0.0$ distance).
3. **No universal threshold:** The observed distances are descriptive for these small samples. A value near 0.10 is not a validated cutoff for other prompts, tasks, models, or runs.

---

## 8. Pilot Experiment Execution (Phase 8)

The Pilot Experiment (`experiments/pilot_experiment.py`) was conducted on live LLM infrastructure to test all system components under real operating conditions:

### 8.1 Pilot Execution Parameters
- **Target Model:** `openai/gpt-oss-20b`
- **Benchmark Prompts:** 50 sampled prompts (10 prompts across each of the 5 task domains)
- **Perturbation Operators Applied:** 5 operators (`punctuation`, `word_insertion`, `word_deletion`, `word_substitution`, `instruction_reordering`)
- **Execution Architecture:** Paired trial design (each trial executes an unperturbed baseline query and a perturbed query)
- **Potential prompt/operator combinations:** 250 (50 prompts × 5 operators)
- **Recorded successful paired trials:** **150** in the live JSONL; the remaining combinations yielded no applicable candidate in this run and must not be counted as successful trials.
- **Recorded provider failures:** 0 among the 150 stored records. This is not a 100% completion rate for all 250 potential combinations.
- **Inference outputs represented:** 300 (original and perturbed response in each paired record)
- **Data file:** `results/pilot_experiment/raw/pilot_raw_results_1793047745.jsonl`, with response text, latency, token counts, and lexical input distances.
- **Perturbation coverage:** 50 word insertions, 50 deletions, 18 reorderings, 24 substitutions, and 8 punctuation variants. The distribution is not balanced across operators.

---

## 9. Output Deviation Metrics (Phase 9)

Output divergence between the original model response $Y$ and perturbed response $Y'$ is computed across complementary dimensions in `src/apsa/metrics/output_distance.py`:

1. **Normalized Output Character Distance ($D_{\text{out\_char}}$):**
   $$D_{\text{out\_char}} = \frac{\text{Levenshtein}(Y, Y')}{\max(|Y|, |Y'|, 1)} \in [0, 1]$$
2. **Token-Level Jaccard Distance ($D_{\text{jaccard}}$):**
   $$D_{\text{jaccard}} = 1 - \frac{|T(Y) \cap T(Y')|}{|T(Y) \cup T(Y')|} \in [0, 1]$$
3. **Semantic Output Divergence ($D_{\text{out\_sem}}$):**
   $$D_{\text{out\_sem}} = 1 - \cos(\mathbf{e}(Y), \mathbf{e}(Y')) \in [0, 1]$$
4. **Functional Correctness Flip Indicator:**
   $$\Delta f_{\text{correct}} = \begin{cases} 1, & \text{if } \text{IsCorrect}(Y) \neq \text{IsCorrect}(Y') \\ 0, & \text{otherwise} \end{cases}$$

---

## 10. Sensitivity Scoring & Analysis Formulations (Phase 10)

To quantify sensitivity per unit of perturbation, we compute two standardized sensitivity formulations in `src/apsa/analysis/sensitivity.py`:

1. **Smoothed Sensitivity Ratio ($S$):**
   $$S(P, P') = \frac{D_{\text{out}}(Y, Y')}{D_{\text{in}}(P, P') + \eta}$$
   where $\eta = 10^{-4}$ is a small regularizer preventing division-by-zero when $D_{\text{in}} \to 0$.
2. **Bounded Sensitivity Ratio (Methodology §4.3):**
   $$S_{\text{bounded}}(P, P') = \frac{D_{\text{out}}(Y, Y')}{\max(\eta, D_{\text{in}}(P, P'))}$$
3. **Budget-Constrained Maximum Output Deviation:**
   $$\mathcal{M}(\epsilon) = \max \left\{ D_{\text{out}}(Y, Y') \;\middle|\; D_{\text{in}}(P, P') \le \epsilon \right\}$$
   *Note: In empirical adversarial vulnerability analysis, the budget-constrained maximum output deviation $\mathcal{M}(\epsilon)$ represents the primary risk metric, while the ratio $S$ serves as a complementary rate-of-change indicator.*

---

## 11. Empirical Results & Findings

The live raw records were re-evaluated with `experiments/evaluate_experiment.py`. The live-only summary is saved at `results/pilot_experiment/analysis/live_model_pilot_1793047745/sensitivity_analysis_summary.json`. The separate `results/pilot_experiment/analysis/sensitivity_analysis_summary.json` contains 1,152 mock records and is not the source of the live statistics below.

### 11.1 Global Distribution of Output Deviation

```
  Metric                           Empirical Value
  ─────────────────────────────────────────────────
  Total Valid Trials Analyzed      150
  Mean Output Deviation (D_out)    0.2816 (28.16%)
  Median Output Deviation          0.1821 (18.21%)
  Record-level 95% interval         [0.2301, 0.3331]
  Max Deviation (Budget ≤ 0.10)    1.0000 (100.0%)
  Max Deviation (Budget ≤ 0.05)    1.0000 (100.0%)
```

**Interpretation:** The 150 paired records have a mean normalized character distance of 0.2816. This is a descriptive output-string difference, not a measure of semantic change or correctness. The interval is record-level and does not adjust for repeated prompts, control variation, or possible response truncation; it does not prove a causal effect or generalize to other models.

---

### 11.2 Sensitivity Vulnerability by Task Domain

```
Task Category                 Peak Sensitivity (S)   Vulnerability Profile
──────────────────────────────────────────────────────────────────────────
Classification                139.31                 Extreme (Discrete label flips)
Code Generation                55.58                 Severe (Syntactic & logic rewrites)
Logical Reasoning              39.98                 High (Step re-sequencing)
Mathematical Reasoning         38.52                 High (Formula notation drift)
Question Answering             18.96                 Moderate (Lexical rewrites)
```

**Pilot observation:** Classification had the highest observed character-distance sensitivity ratio among task categories in this single-model run. This ranking is descriptive, may be affected by the small input-distance denominator and output ceiling, and is not evidence that classification is generally the most fragile task domain.

---

### 11.3 Sensitivity Vulnerability by Perturbation Operator

```
Perturbation Operator         Peak Sensitivity (S)   Possible Interpretation (Not Measured)
─────────────────────────────────────────────────────────────────────────────
Punctuation                   139.31                 Output-label change; mechanism unknown
Word Deletion                  55.58                 Candidate omitted one token; effect unisolated
Word Substitution              50.41                 Candidate changed one table-mapped word
Word Insertion                 18.62                 Candidate added one token
Instruction Reordering          1.97                 Sentence-order change; mechanism unknown
```

**Pilot observation:** The largest observed character-distance sensitivity ratio was associated with a punctuation candidate. The ratio is sensitive to its small character-distance denominator and potentially capped outputs; it should not be read as a general perturbation ranking.

---

### 11.4 Top 5 Sensitivity Cases (Empirical Vulnerability Highlights)

| Rank | Prompt ID | Task Category | Perturbation | Input Distance ($d_{in}$) | Output Distance ($D_{out}$) | Sensitivity ($S$) |
| :---: | :---: | :--- | :--- | :---: | :---: | :---: |
| **1** | `CLASS-002` | Classification | `punctuation` | **0.00588** (0.59%) | **0.8333** | **139.31** |
| **2** | `CLASS-008` | Classification | `punctuation` | **0.00510** (0.51%) | **0.3745** | **72.00** |
| **3** | `CLASS-001` | Classification | `punctuation` | **0.00521** (0.52%) | **0.3333** | **62.80** |
| **4** | `CODE-003` | Code Generation | `word_deletion` | **0.01351** (1.35%) | **0.7567** | **55.58** |
| **5** | `CODE-001` | Code Generation | `word_substitution` | **0.01974** (1.97%) | **1.0000** | **50.41** |

---

### 11.5 Qualitative Case Studies from Live Data

#### Case Study 1: The Trailing Punctuation Label Flip (`CLASS-002`)
- **Task:** Financial News Topic Classification
- **Original Prompt:**
  ```text
  Classify the topic of this news headline into one of [Sports, Technology, Politics, Business]: 
  'Central bank raises interest rates by 50 basis points to curb inflation.'
  ```
- **Original Output:**
  ```text
  Business
  ```
- **Perturbed Prompt (`punctuation`):**
  ```text
  Classify the topic of this news headline into one of [Sports, Technology, Politics, Business]: 
  'Central bank raises interest rates by 50 basis points to curb inflation.'.
  ```
- **Perturbed Output:**
  ```text
  **Politics**
  ```
- **Observed impact:** The extra period was associated with the model returning `Politics` instead of `Business` ($d_{in} = 0.00588$, $D_{out}=0.8333$). The stored pilot evaluator does not calculate task correctness; the expected-label comparison must be run separately before calling this a correctness flip.

#### Case Study 2: Large Character-Distance Change after Word Substitution (`CODE-001`)
- **Task:** Python Algorithm Implementation
- **Perturbation Type:** `word_substitution` ($d_{in} = 0.01974$, under 2% edit distance).
- **Observed output metric:** Normalized character distance was **$D_{out} = 1.0000$**. This measures string difference, not semantic or functional change; the pilot record does not establish that the generated implementations were different in behavior. Sensitivity score: **50.41**.

#### Case Study 3: Large Character-Distance Change under Instruction Reordering (`MATH-008`)
- **Task:** Numerical Sequence Term Evaluation
- **Perturbation Type:** `instruction_reordering`
- **Observed output metric:** The normalized character distance was **$D_{out} = 1.0000$**. This does not establish a change in reasoning process, correctness, or semantic content.

---

## 12. Quality Assurance, Bug Fixes & Test Suite Verification

Prior to live execution, an intensive verification audit was conducted across the entire codebase. Ten critical architectural defects were uncovered and resolved:

| ID | Component | Defect Discovered | Engineering Correction Made |
| :---: | :--- | :--- | :--- |
| **1** | `experiments/pilot_experiment.py` | Method signature mismatch and missing attributes caused runtime crashes on all trials. | Updated to `pert_instance.perturb(...)` and integrated genuine `LexicalDistanceCalculator` metrics. |
| **2** | `src/apsa/execution/budget_enforcer.py` | Broken import of non-existent class; word distance normalization denominator trivially evaluated to 1.0. | Imported `LexicalDistanceResult`; normalized word edit distance against prompt token length. |
| **3** | `src/apsa/config/loader.py` | UTF-8 Byte Order Marks (BOM) crashed YAML parser on Windows; modular sub-configs were unexpanded. | Added `encoding="utf-8-sig"` and implemented recursive `_resolve_sub_configs` loader. |
| **4** | `src/apsa/llm_providers/` | Top-level vendor package imports caused immediate crash in offline environments lacking API SDKs. | Implemented lazy importing with clear `ConfigurationError` messages; added `MockProvider`. |
| **5** | `src/apsa/metrics/output_distance.py` | Uncaught `TypeError` on `None` outputs; empty strings falsely returned similarity 1.0 (zero distance). | Added safe `None` guards, `is_valid` flag, and explicit `is_empty_pair` indicator. |
| **6** | `experiments/control_experiment.py` | Missing `defaultdict` import; failed API calls falsely reported `exact_match_ratio: 1.0`. | Imported `defaultdict`; tracked failed calls; added `--mock` flag and per-category variance tables. |
| **7** | `tests/integration/` | End-to-end integration tests were empty `pass` placeholders. | Implemented full offline integration tests verifying the prompt-to-sensitivity lifecycle. |
| **8** | `src/apsa/analysis/sensitivity.py` | Smoothing constant named `epsilon`, colliding with perturbation budget symbol $\epsilon$. | Refactored parameter to `eta`; implemented both smoothed and bounded methodology ratios. |
| **9** | Dataset Documentation | Documentation claimed 246 baseline prompts; actual CSV contains 100 prompts. | Corrected documentation across all reports to accurately reflect the 100 benchmark prompts. |
| **10** | `src/apsa/perturbations/distance_utils.py` | Redundant consecutive variable assignment. | Removed duplicate line of dead code. |

### Automated Test Suite Execution
The full suite was re-run after the latest runner and storage changes:
```text
pytest tests -q --basetemp .apsa-pytest-temp
185 passed in 10.33s
```
The changed runner, storage, and test files pass Ruff checks (the experiment loop intentionally catches and records per-trial exceptions so one failed trial does not terminate the batch). Unit tests and mock integration tests verify software behavior only; they do not establish empirical validity.

---

## 13. Comparison with State-of-the-Art Literature

This pilot does not establish a state-of-the-art comparison or extend prior literature. Such claims require source-verified citations, aligned protocols, controls, and a larger, reproducible experiment. The observed cases should be treated as pilot examples only.

---

## 14. Remaining Work Within Phases 1–10

The project is not ready to support broad research conclusions. Before treating Phases 1–10 as experimentally complete:

1. Re-run the pilot with the corrected perturbation records and preserve the original baseline prompts unchanged.
2. Implement syntactic tree distance or remove that dimension from the declared sensitivity formula before using a positive syntactic weight; the current runner records the sensitivity score as unavailable rather than inserting a zero.
3. Keep task-specific correctness and semantic input distance in the primary runner; integrate them into the separate live-pilot evaluator, which currently reports character distance only.
4. Record generation limits and provider finish reasons, then repeat the pilot with a higher output limit to assess censoring.
5. Compare perturbation trials with matched control repeats and expand coverage across prompts, operators, and models.
6. Preserve successful runs in `results.jsonl` and failed trials in `failures.jsonl`, alongside configuration and analysis output; keep mock records out of empirical summaries.

These are completion requirements for the declared Phase 1–10 scope, not a proposal to start another phase.

---

## 15. Summary of Project Milestones (Phases 1–10)

| Phase | Milestone Name | Key Deliverables & Implementation | Verification & Results Status |
| :---: | :--- | :--- | :---: |
| **Phase 1** | Research Methodology | Research questions, hypotheses, variables, optimization objective | Specified; empirical hypotheses not tested |
| **Phase 2** | Software Architecture | Modular Python package and configuration | Implemented; unit/integration-tested portions |
| **Phase 3** | Baseline Dataset | 100 prompts across 5 task domains | Dataset present; correctness/reference quality needs domain validation |
| **Phase 4** | Perturbation Engine | 10 operators and heuristic risk flags | Implemented; tests run separately; risk flags are not equivalence checks |
| **Phase 5** | Input Distance Metrics | Character/word distance and optional embedding distance | Implemented; not all metrics used in live pilot |
| **Phase 6** | LLM Provider Interface | Provider abstraction and mock/live adapters | Implemented; mock tests and a recorded live run |
| **Phase 7** | Control Experiment | Repeated-prompt baseline variability | Tooling and selected records exist; not a universal noise threshold |
| **Phase 8** | Pilot Experiment | Paired prompt execution and raw result storage | 150 live paired records from one model; broader matrix incomplete |
| **Phase 9** | Output Deviation Metrics | Textual, optional semantic, and functional metrics | Implemented; live analysis used character distance only |
| **Phase 10** | Sensitivity Scoring | Ratios and budget-filtered output-distance maxima | Live pilot descriptive reanalysis exists; no inferential validation |

---

## 16. Conclusion

APSA has a substantial Phase 1–10 software foundation, automated tests, mock integration runs, and a recorded live pilot. The live pilot is useful for checking the experiment pipeline and identifying cases for follow-up; it is not sufficient to claim general model fragility or validated causal effects. In particular, output-distance statistics do not replace semantic-risk assessment, task correctness, and control comparisons. Continue work within the declared Phase 1–10 scope before treating the framework as ready for the main experiments.

---
*Report status corrected from repository artifacts and a separately recomputed live-only pilot summary. Software tests do not establish empirical validity.*
