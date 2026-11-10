# Complete Project Documentation: Phases 1 to 10

**Project Title:** Adversarial Prompt Sensitivity Analysis: Studying Maximum Output Changes from Minimal Prompt Perturbations

> **Status note (November 2026):** This phase narrative is a historical overview, not an audit or evidence of empirical validation. The current evidence and limitations are documented in [APSA_Research_Progress_and_Results_Report.md](./APSA_Research_Progress_and_Results_Report.md). In particular, the baseline contains 100 prompts, perturbation operators do not certify semantic preservation, and prior live artifacts predate the current pilot controls/manifest/semantic-distance implementation. See [the current pilot workflow](./pilot_study_workflow.md) for executable behavior.

## 1. Introduction
The advent of Large Language Models (LLMs) has introduced a paradigm where users interact with systems via natural language prompts. However, LLMs often exhibit high sensitivity to the exact phrasing of these prompts. A minor change in punctuation or the substitution of a single synonymous word can drastically alter the model's output.

This research project, titled "Adversarial Prompt Sensitivity Analysis," investigates this phenomenon from an adversarial perspective. Its objective is to study how small prompt edits relate to deviations in LLM outputs; an edit is not assumed to preserve meaning merely because it is small. The repository implements the research methodology, software architecture, baseline dataset, perturbation operators, distance metrics, provider interfaces, and pilot analysis path. Implementation and software tests do not establish semantic validity or empirical conclusions.

## 2. Research Objective and Motivation
Prompt sensitivity matters because it directly impacts the reliability, robustness, and predictability of LLMs in production environments. If a model fails or hallucinates due to a missing comma or a slight rephrasing, it cannot be fully trusted for critical applications. 

Small perturbations can help investigate model behavior, but they do not automatically isolate semantic understanding from parsing. A behavior change is an observation to assess alongside control variation, semantic risk, answer correctness, and task context; it is not alone proof of vulnerability.

Our central research question asks: *To what extent can we maximize the deviation in an LLM's output while minimizing the change to its input?*

Mathematically, this objective is framed as a constrained optimization problem:
$$
\max_{P'} D_{out}(f(P), f(P'))
$$
subject to:
$$
D_{input}(P, P') \le \epsilon
$$

In simple language, we want to find the modified prompt ($P'$) that makes the model's output ($f(P')$) as different as possible from the original output ($f(P)$), under the strict rule that the modified prompt must remain extremely similar to the original prompt ($P$), governed by a strict budget ($\epsilon$).

## 3. Phase 1 — Research Methodology
Phase 1 established the theoretical foundation of the project. We defined several core elements:
- **Research Questions (RQ1–RQ5):** Focusing on the bounds of adversarial sensitivity, the types of most damaging perturbations, and the comparative robustness of different LLMs.
- **Independent Variables:** The LLM architecture, the task category, and the specific perturbation applied.
- **Dependent Variables:** The input distance (syntactic/semantic change) and the output distance (behavioral deviation).
- **Experimental Controls:** Fixing generation parameters (e.g., temperature = 0.0) and utilizing identical system prompts.
- **Perturbation Categories:** Surface (typos, capitalization), Lexical (synonyms, word deletions), and Structural (reordering).
- **Reproducibility:** A commitment to deterministic seeds and comprehensive logging.

These decisions are intended to improve repeatability and isolate relevant variables. Their adequacy must still be assessed through implementation checks and empirical validation.

## 4. Phase 2 — Software Architecture
To support the research, we designed a modular software architecture based in Python. The repository is structured into distinct, highly decoupled modules located under `src/apsa/`:
- `perturbations/`: Houses the engine and registry for prompt modifications.
- `metrics/`: Contains both `input_distance` and `output_distance` algorithms.
- `llm_providers/`: Abstractions for communicating with external APIs.
- `analysis/`: Computes the sensitivity scores and statistical derivations.

Data flows sequentially: Baseline prompts are loaded from the `data/` directory, pushed through the `perturbations/` engine, measured by `metrics/input_distance`, sent to the LLM via `llm_providers/`, and the outputs are evaluated by `metrics/output_distance` and scored in `analysis/`. This pipeline supports scalable, automated experimentation without manual intervention.

## 5. Phase 3 — Baseline Dataset
A baseline dataset is essential because we must establish a ground-truth "expected behavior" for the LLM before applying any noise. 

The dataset is stored in `data/baseline_prompts.csv` and contains 100 baseline prompts across five task categories. Each prompt is tagged with a `prompt_id`, `task_category`, `expected_answer`, and associated metadata.

## 6. Phase 4 — Perturbation Engine
The Perturbation Engine (`src/apsa/perturbations/`) is responsible for programmatically applying controlled noise to the baseline prompts. 

We implemented a factory registry pattern supporting several operators:
- **Surface-level:** `CharSubstitutionPerturbation`, `CapitalizationPerturbation`, `PunctuationPerturbation`, `WhitespacePerturbation`. (Changes syntax without altering words).
- **Lexical-level:** `AdditionPerturbation`, `DeletionPerturbation`, `SubstitutionPerturbation`, `SynonymPerturbation`. (Changes individual words).
- **Structural-level:** `ReorderingPerturbation`, `RephrasingPerturbation`. (Changes grammatical structure).

Perturbations are generated reproducibly from controlled seeds. The operators themselves do not enforce a budget or prove intent preservation; the execution runner checks available character, word, and semantic distances, while syntactic tree edit distance remains unimplemented.

## 7. Phase 5 — Input Distance Metrics
To enforce the perturbation budget, we must precisely quantify how much a prompt was altered. 
We implemented the following metrics (`src/apsa/metrics/input_distance/`):
- **Character-level distance:** Raw Levenshtein edit distance.
- **Normalized character distance:** Levenshtein distance scaled between [0, 1].
- **Word-level distance:** Token-based edit distance.
- **Semantic Distance:** Cosine distance utilizing high-dimensional embeddings (e.g., via `sentence-transformers`).

These metrics measure input difference. A candidate is valid only for the dimensions actually computed and checked against configured thresholds. Semantic cosine distance is not semantic equivalence, and syntactic tree-edit distance remains an unimplemented stub.

## 8. Phase 6 — LLM Provider Interface
To execute our experiments, we built a model-agnostic interface (`src/apsa/llm_providers/`). A common interface prevents vendor lock-in and standardizes our output measurements.

We integrated two core providers:
- `GeminiProvider` (targeting models like `gemini-1.5-flash`)
- `OpenAIProvider` (targeting models like `gpt-3.5-turbo` and `gpt-4o`)

Prompts are sent using fixed generation configurations (temperature = 0.0) defined in `config/models.yaml`. The system includes automated `tenacity`-based retries to handle transient API rate limits. All credentials are appropriately fetched from the environment rather than hardcoded, failing gracefully if unconfigured.

## 9. Phase 7 — Control Experiment
Before measuring perturbation sensitivity, we must account for the natural stochastic variance of the LLMs. The control experiment (`experiments/control_experiment.py`) is designed to run the identical baseline prompt multiple times under identical configuration settings. 

By measuring the output variability among these identical runs, we establish a natural "baseline variance." Going forward, the methodology dictates that we cannot claim a perturbation caused an output change unless the observed deviation strictly exceeds this control variance. Currently, the infrastructure and mathematical methodology are fully implemented, ready for execution.

## 10. Phase 8 — Pilot Experiment
Phase 8 introduces a smaller-scale pilot experiment to validate the pipeline before incurring the high API costs of the full study.
The pilot script (`experiments/pilot_experiment.py`) samples exactly 5 task categories with 10 prompts each. It schedules 3 models against 5 perturbation types (`punctuation`, `word_insertion`, `word_deletion`, `word_substitution`, `instruction_reordering`), applying 3 repetitions each (totaling 2,250 runs).

The script performs a rigorous pre-flight check—validating datasets, perturbation classes, and API availability. Raw JSONL outputs are strictly segregated from processed data. As API keys were intentionally withheld from the environment for safety during development, the pilot gracefully aborts during validation, resulting in a generated `results/pilot_report.md` showing 0 successful runs (Pending Execution).

## 11. Phase 9 — Output Deviation Metrics
Phase 9 implemented the logic required to mathematically compare an original output ($Y$) with a perturbed output ($Y'$). 

Located in `src/apsa/metrics/output_distance.py`, the system calculates:
- Exact textual matches
- Character and Token-level Jaccard/Levenshtein distances
- Semantic Output Distance ($D_{\text{output}} = 1 - \text{semantic\_similarity}(Y, Y')$) utilizing sentence embeddings.
- Functional Correctness Flips (e.g., tracking when an answer shifts from `correct -> incorrect`).

The documentation heavily emphasizes that textual differences do not automatically equate to meaningful behavioral differences, which is why semantic and functional correctness flips are heavily prioritized over raw edit distance for long-form generation.

## 12. Phase 10 — Sensitivity Score
The final mathematical culmination is the Sensitivity Score, implemented in `src/apsa/analysis/sensitivity.py`. 

This module computes the primary sensitivity ratio:
$$
S = \frac{D_{\text{output}}}{D_{\text{input}} + \epsilon}
$$
It measures how much the output deviates per unit of input change. 

Because ratio metrics can be skewed by infinitesimal denominators, the implementation also supports absolute output deviations, normalized output deviations, and max output deviation under a strict semantic budget. 

The analyzer includes cohort functions to quickly aggregate and identify the highest sensitivity cases per model, task, or perturbation type. It also calculates confidence intervals based on the t-distribution to report the statistical significance of observed variabilities.

## 13. Complete System Workflow

```text
Research Methodology (Phase 1)
        ↓
Software Architecture (Phase 2)
        ↓
Baseline Dataset (Phase 3)
        ↓
Perturbation Generation (Phase 4)
        ↓
Input Distance Measurement (Phase 5)
        ↓
LLM Execution (Phase 6)
        ↓
Control Experiment (Phase 7) — [Pending Execution]
        ↓
Pilot Experiment (Phase 8) — [Pending Execution]
        ↓
Output Deviation Measurement (Phase 9)
        ↓
Sensitivity Score (Phase 10)
```
Information flows downward. Prompts are sourced, modified, mathematically constrained, executed against LLMs, evaluated for behavioral shifts, and statistically analyzed. (Execution phases are implemented but awaiting API credentials to run).

## 14. Implementation and Technology Stack
- **Language**: Python 3.11+
- **Libraries**: `pydantic`, `pyyaml`, `scipy`, `numpy`, `python-Levenshtein`
- **Machine Learning**: `sentence-transformers`, `scikit-learn`
- **Providers**: `google-generativeai`, `openai`
- **Resilience**: `tenacity`
- **Testing**: `pytest`
- **Data formats**: CSV (datasets), JSONL (raw records), YAML (configuration).

## 15. Testing and Validation
The project maintains a healthy suite of automated unit and integration tests.
- **Metrics Testing:** Validates that edit distances and semantic bounding math correctly calculate bounded `[0,1]` float outputs.
- **Sensitivity Testing:** Verifies that aggregate math (means, confidence intervals) performs as expected.
- **Pipeline Testing:** Pilot constraints ensure that LLMs instantly fail during validation if the environment is misconfigured. 
All implemented tests currently pass successfully.

## 16. Results and Observations So Far
At this juncture, the system is fully engineered, but the execution engines (Phase 7 Control and Phase 8 Pilot) have been successfully blocked by our strict pre-flight API validation constraints. As a result, 0 external API calls have been made, and we have 0 real-world LLM responses. Therefore, no preliminary patterns regarding model sensitivity have been observed yet.

## 17. Challenges and Limitations
The primary challenge revolves around enforcing semantic preservation. While cosine similarity via `sentence-transformers` is highly effective, it does not perfectly map to human semantic understanding. Certain critical words ("not") can easily slip past semantic embedding thresholds, causing false positives in adversarial vulnerability. This is a known limitation that our methodology attempts to mitigate via the $\epsilon_{sem}$ budgets.

Additionally, LLM evaluation on open-ended generation is notoriously difficult. Relying purely on Levenshtein distances for output evaluation ($D_{\text{output}}$) is insufficient, heavily relying on the more computationally expensive semantic embedding approaches.

## 18. Current Project Status

| Phase | Component | Status |
|-------|-----------|--------|
| 1 | Research Methodology | **Completed** |
| 2 | Software Architecture | **Completed** |
| 3 | Baseline Dataset | **Completed** |
| 4 | Perturbation Engine | **Completed** |
| 5 | Input Distance Metrics | **Completed** (Syntactic metrics planned) |
| 6 | LLM Provider Interface | **Completed** |
| 7 | Control Experiment | **Partially Completed** (Infrastructure built, awaiting execution) |
| 8 | Pilot Experiment | **Partially Completed** (Infrastructure built, awaiting execution) |
| 9 | Output Deviation Metrics | **Completed** |
| 10 | Sensitivity Score | **Completed** |

## 19. Next Steps
The immediate next steps involve procuring and configuring standard API keys to execute the Control and Pilot experiments. 
Following successful execution, the roadmap indicates we will:
1. Conduct extensive statistical analysis on the resulting data distributions.
2. Develop data visualization modules to graph sensitivity distributions.
3. Identify the highest-impact perturbation types.
4. Conclude the research with a robust final evaluation of model vulnerabilities.

## 20. Conclusion
Through the first ten phases, this project has successfully progressed from an abstract theoretical research question into a concrete, robust, and highly scalable software pipeline. We have engineered the ability to systematically perturb natural language prompts, mathematically bound those changes, execute them against live LLM infrastructure, and programmatically score the resulting behavioral shifts. The infrastructure is now fully primed for large-scale experimental execution and discovery.
