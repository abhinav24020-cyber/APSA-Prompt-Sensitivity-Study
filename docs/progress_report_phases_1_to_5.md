# Project Progress Report: Phases 1–5

**Project Title:** Adversarial Prompt Sensitivity Analysis (APSA): Studying Maximum LLM Output Changes from Minimal Prompt Perturbations  
**Date:** September 2026  
**Status:** Phases 1–5 Completed (Research, Architecture, Dataset, Perturbation Engine, & Input Distance Metrics)  
**Target Audience:** Project Supervisor / Evaluation Committee  

---

## 1. Executive Summary

Large Language Models (LLMs) are increasingly integrated into critical applications ranging from automated code generation and mathematical problem solving to medical and legal reasoning. However, these models exhibit a fundamental vulnerability: **prompt sensitivity**, where minor, seemingly trivial modifications to an input prompt can induce significant, unintended shifts in model outputs.

The **Adversarial Prompt Sensitivity Analysis (APSA)** project introduces a systematic, quantitative methodology to evaluate LLM brittleness under controlled input modifications. By viewing input prompts through an adversarial lens, we formulate prompt perturbation as a constrained optimization problem: finding the smallest possible input alteration $P \to P'$ that maximizes output divergence $D_{\text{out}}(M(P), M(P'))$.

To date, **Phases 1 through 5** of the project have been fully completed, successfully constructing the entire theoretical, architectural, baseline dataset, perturbation generation, and input measurement infrastructure. The system is verified with **146 passing unit tests** and automated dataset validation, placing the project in an ideal position for final experimental execution in Phase 6.

---

## 2. Overall Research Framework & Mathematical Formulation

### 2.1 Optimization Objective
We model prompt sensitivity as finding an adversarial perturbation $P'$ of an original prompt $P$ for a model $M$:

$$\max_{P'} D_{\text{out}}\left(M(P), M(P')\right) \quad \text{subject to} \quad d_{\text{input}}(P, P') \le \epsilon$$

Where:
* $P$: Original baseline prompt.
* $P'$: Perturbed prompt candidate.
* $M$: Target Large Language Model.
* $d_{\text{input}}(P, P')$: Multi-dimensional input perturbation distance (lexical, semantic, syntactic).
* $\epsilon$: Maximum allowable perturbation budget vector.
* $D_{\text{out}}$: Output divergence measure between generated outputs $M(P)$ and $M(P')$.

### 2.2 Sensitivity Coefficient
To measure sensitivity per edit unit, we define the **Sensitivity Coefficient** $\mathcal{S}(P, P'; M)$:

$$\mathcal{S}(P, P'; M) = \frac{D_{\text{out}}\left(M(P), M(P')\right)}{\max\left(\eta, d_{\text{input}}(P, P')\right)}$$

where $\eta > 0$ is a small smoothing constant preventing division by zero for identical inputs.

---

## 3. Phase-by-Phase Summary of Completed Work

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                    PROJECT ROADMAP                                     │
├────────────────────────────────────────────────────────────────────────────────────────┤
│  Phase 1: Research Methodology & Formulations                  [COMPLETED ✓]           │
│  Phase 2: Modular Software Architecture (apsa v0.1.0)          [COMPLETED ✓]           │
│  Phase 3: Curated Baseline Benchmark Dataset (100 Prompts)     [COMPLETED ✓]           │
│  Phase 4: Adversarial Perturbation Engine (10 Operators)       [COMPLETED ✓]           │
│  Phase 5: Input Perturbation Distance System                   [COMPLETED ✓]           │
│ ────────────────────────────────────────────────────────────────────────────────────── │
│  Phase 6: LLM Execution, Output Divergence & Statistical Analysis [UPCOMING]          │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### Phase 1 — Research Methodology & Theoretical Foundation

* **Objective:** Establish formal research questions, hypotheses, experimental variables, and evaluation protocols.
* **Core Research Questions:**
  * **RQ1 (Perturbation Type Susceptibility):** Which perturbation categories (surface, lexical, structural, formatting) trigger the largest output shifts?
  * **RQ2 (Task Domain Vulnerability):** How does sensitivity vary across deterministic reasoning (math/logic/code) vs. non-deterministic tasks (QA/classification)?
  * **RQ3 (Model Robustness & Scale):** Does increased parameter scale (e.g., 70B vs 8B) or specialized training improve prompt stability?
  * **RQ4 (Scaling Behavior):** Does output divergence follow smooth linear decay or step-function performance collapse as prompt edits accumulate?
  * **RQ5 (Adversarial Optimization):** Can targeted perturbation strategies locate higher-impact prompt variations than random editing?
* **Hypotheses Formulated:** Five testable hypotheses ($H_1$--$H_5$) corresponding directly to RQ1--RQ5.
* **Model Selection:** Designated 7 representative models spanning parameter scales and architectures (Llama 3.1 8B/70B, Qwen 2.5 7B/Coder-32B, Mistral 7B, Gemini 1.5 Flash/Pro).

---

### Phase 2 — Modular Software Architecture (`apsa` v0.1.0)

* **Objective:** Architect a modular, production-grade Python package to execute experiments reproducibly.
* **System Design:** Created `src/apsa`, structured around decoupled subsystems:
  * `apsa.config`: Schema validation and experiment configuration via Pydantic and YAML.
  * `apsa.dataset`: Dataset parsing, record validation, and category filtering.
  * `apsa.perturbations`: Operator registry, transform engines, and semantic risk checkers.
  * `apsa.metrics`: Input distance calculators and composite divergence formulas.
  * `apsa.reproducibility`: Environment logging and global random seed management (Python, NumPy, PyTorch).
  * `apsa.providers`: Unified API interfaces for OpenAI, Google Gemini, and HuggingFace/vLLM backends.
  * `apsa.storage`: Structured JSONL serializing schemas (`ExperimentRun`, `OutputPairRecord`).
* **Documentation & Standards:** Full architecture documented in `docs/software_architecture.md`.

---

### Phase 3 — Baseline Benchmark Dataset

* **Objective:** Build a standardized, high-quality benchmark dataset of original baseline prompts.
* **Dataset Characteristics:**
  * Hand-curated 100 baseline prompts across 5 balanced core task categories (20 prompts per category):
    1. **Mathematical Reasoning:** Multi-step arithmetic and word problems.
    2. **Logical Reasoning:** Syllogisms, truth tables, and conditional deduction.
    3. **Question Answering:** Closed-domain fact extraction and text retrieval.
    4. **Text Classification:** Sentiment analysis and multi-class categorizations.
    5. **Code Generation:** Short Python function implementations.
  * 92 prompts represent deterministic tasks with verifiable ground-truth expected answers.
* **Automated Quality Assurance:** Created `scripts/validate_baseline_dataset.py`, enforcing 8 automated checks (category balance, non-emptiness, zero duplicates, character lengths, valid JSON metadata). All 8 checks passed cleanly.

---

### Phase 4 — Adversarial Prompt Perturbation Engine

* **Objective:** Design and implement controlled operators capable of generating bounded, intent-preserving prompt modifications.
* **10 Implemented Operators (`src/apsa/perturbations/operators.py`):**
  1. `char_substitution`: Keyboard/visual typo injection on non-essential tokens.
  2. `capitalization`: Casing variations (lowercasing, title case, ALL CAPS).
  3. `punctuation`: Insertion, deletion, or swapping of structural punctuation marks.
  4. `whitespace`: Injection/compression of spaces, tabs, and line breaks.
  5. `word_insertion`: Adding conversational filler words ("please", "kindly", "just").
  6. `word_deletion`: Omitting non-essential articles/adverbs ("the", "a").
  7. `word_substitution`: Swapping words using a predefined replacement dictionary.
  8. `synonym_replacement`: Context-aware synonym substitution via lookup tables.
  9. `instruction_reordering`: Sentence-level clause swapping for multi-sentence prompts.
  10. `formatting_modification`: Converting list formats (numbered/bulleted to prose) and instruction prefixes.
* **Levels of Minimality:** Categorized perturbations across Surface-Level, Lexical, and Semantic dimensions.
* **Semantic Risk Detector (`SemanticFlagDetector`):** Implemented a rule-based safety monitor flagging modifications as `MINIMAL` (green), `MODERATE` (yellow), or `HIGH` (red) risk (e.g., catching negations or removal of core question tokens).

---

### Phase 5 — Input Perturbation Measurement System

* **Objective:** Implement mathematical input distance metrics $d_{\text{input}}(P, P')$ to precisely quantify prompt changes prior to model execution.
* **1. Lexical Subsystem (`src/apsa/metrics/input_distance/lexical.py`):**
  * Computes 6 distinct lexical distance metrics in a single dynamic programming pass:
    * Character Levenshtein Distance ($d_{\text{char}}$)
    * Normalized Character Distance ($d_{\text{char\_norm}} \in [0, 1]$)
    * Word Levenshtein Distance ($d_{\text{word}}$)
    * Number of Words Changed
    * Number of Characters Changed
    * Percentage Prompt Modification ($\%$)
* **2. Semantic Subsystem (`src/apsa/metrics/input_distance/semantic.py`):**
  * Evaluates semantic drift using cosine distance over dense vector representations:
    $$D_{\text{semantic}}(P, P') = 1 - \frac{E(P) \cdot E(P')}{\|E(P)\| \|E(P')\|}$$
  * Built an abstract `EmbeddingModel` base class with a concrete `SentenceTransformerEmbedder` backend utilizing the state-of-the-art `all-mpnet-base-v2` model (768-dimensional normalized embeddings).
  * Includes string deduplication and batching to optimize computation speed.
* **3. Syntactic Interface (`src/apsa/metrics/input_distance/syntactic.py`):**
  * Scaffolded interface stubs for tree edit distance over dependency parse trees.

---

## 4. Verification & Quality Assurance

To guarantee system stability, reliability, and reproducibility, the project maintains a comprehensive automated testing suite:

* **Pytest Test Suite:** **146 passed tests out of 146** (100% pass rate).
  * `test_baseline_dataset.py`: Validates dataset parsing, line counts, and category filtering.
  * `test_config.py`: Verifies configuration merging and schema validation.
  * `test_perturbations.py` & `test_perturbation_engine.py`: Tests operator determinism, edge-case resilience, seed locking, and semantic flag detection.
  * `test_metrics.py` & `test_input_distance.py`: Validates lexical and semantic distance calculation accuracy.
* **Automated Data Validation:** All 100 baseline prompts pass full metadata and format verification.

---

## 5. Deliverables & Progress Summary

| Phase | Phase Name | Status | Key Deliverables |
| :---: | :--- | :---: | :--- |
| **Phase 1** | Research Methodology | **Completed** | Formal math formulation ($\max D_{\text{out}}$), RQs (1–5), Hypotheses (1–5), `docs/research_methodology.md` |
| **Phase 2** | Software Architecture | **Completed** | `apsa` Python package (v0.1.0), Pydantic schemas, modular structure, `docs/software_architecture.md` |
| **Phase 3** | Baseline Dataset | **Completed** | 100 curated prompts across 5 categories, 92 deterministic tasks, `data/baseline_prompts.csv`, dataset card |
| **Phase 4** | Perturbation Engine | **Completed** | 10 transformation operators, 3 minimality levels, `SemanticFlagDetector`, `docs/perturbation_methodology.md` |
| **Phase 5** | Input Distance System | **Completed** | Lexical DP metrics (6 types), Semantic distance (`all-mpnet-base-v2`), `docs/phase_5_documentation.md` |
| **Phase 6** | Model Execution & Analysis | **Planned** | LLM API execution, output divergence metrics, statistical analysis, final research paper |

---

## 6. Next Steps (Phase 6 Roadmap)

With the entire foundation built and thoroughly verified, the final phase (**Phase 6**) will execute the main empirical experiments:

1. **LLM API & Provider Integration:** Connect candidate LLMs (Gemini, HuggingFace, OpenAI) to run automated prompt batches.
2. **Output Divergence Calculation:** Compute task-specific output divergence $D_{\text{out}}$ (Exact Match, Code Execution pass/fail, BLEU/ROUGE, and LLM-as-a-Judge semantic scoring).
3. **Statistical Analysis & Visualization:** Aggregate results to evaluate Hypotheses $H_1$--$H_5$, produce publication-quality visualizations, and publish the final findings report.

---

*Detailed phase technical documentations are available in [`docs/phase_1_to_4_documentation.md`](file:///c:/Users/Aditya%20Giri/.gemini/antigravity-ide/scratch/adversarial-prompt-sensitivity/docs/phase_1_to_4_documentation.md) and [`docs/phase_5_documentation.md`](file:///c:/Users/Aditya%20Giri/.gemini/antigravity-ide/scratch/adversarial-prompt-sensitivity/docs/phase_5_documentation.md).*
