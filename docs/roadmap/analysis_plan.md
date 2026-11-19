# APSA Main Study — Statistical Analysis Plan (Phase 11, Task 11.2)

**Study ID:** `main_v1` · **Config:** `config/experiments/main_study.yaml` · **Analysis code:** `experiments/analyze_study.py`

## Timing and pre-specification status (read first)

The study design (prompts, operators, models, controls, system prompt, generation settings) was fixed in the config file **before** any live output was collected. This plan was written on 2026-11-19 **while** data collection was running. Partial results from the first ~540 pairs were viewed once while debugging the analysis pipeline. The analysis is therefore **not formally pre-registered**. To limit researcher degrees of freedom:

- every analysis listed here is reported whatever its outcome, including null and mixed results;
- the primary outcome and statistical unit below were not changed after viewing data;
- the robustness specifications (§8) are reported in full.

## 1. Research questions

The analysis addresses the original Phase 1 questions verbatim (`docs/research_methodology.md` §2):

- **RQ1:** Which category of minimal input perturbation (surface-level, lexical, syntactic, or structural/instructional) causes the highest mean and maximum output divergence across different LLMs?
- **RQ2:** How does prompt sensitivity vary across distinct task categories (e.g., deterministic reasoning, code generation, closed QA/extraction, open-ended summarization)?
- **RQ3:** Do larger parameter scales and specialized alignment paradigms (e.g., RLHF, RLAIF, chain-of-thought reasoning tuning) increase LLM robustness against minimal prompt perturbations?
- **RQ4:** What is the mathematical relationship between input perturbation distance ε and output divergence δ? Does output divergence scale continuously or via non-linear phase transitions?
- **RQ5:** Can discrete search strategies (e.g., greedy token substitution, beam search) consistently identify worst-case input perturbations that yield significantly higher output divergence than random perturbations of equal input distance?

**Scope limits that apply up front.** No syntactic-rephrasing operator is used (the `formatting_modification` operator only prepends “Please”, duplicating `word_insertion`), so RQ1 compares surface, lexical and structural families. The dataset has no summarisation category, so RQ2 covers five categories: mathematical reasoning, logical reasoning, question answering, classification and code generation. RQ3 can only be addressed observationally: the five models differ in vendor, architecture and training simultaneously, so no causal scale effect can be identified. RQ5 is only addressed through a proxy (selection among fixed operators), because no greedy or beam token search was run.

## 2. Design and unit of observation

- **Generation:** per (model, prompt): one *anchor* generation of the original prompt, two unchanged *control* re-generations, and one generation per applicable *perturbed* prompt. Temperature is 0 and the token cap is 768. A fixed system prompt asks for a final line of the form `Final answer: …` (or code only), identically in every condition.
- **Pair:** each control and each treatment generation is compared with the anchor of the same (model, prompt).
- **Statistical unit:** the **(model, prompt)** unit. For a given model, the treatment metric is averaged over operators and the control metric over the two repetitions. Their difference is the paired observation.
- **Clustering:** all observations that share an original prompt form one cluster, across models and operators. Confidence intervals use a **prompt-level cluster bootstrap** (4,000 resamples, percentile, seed 20261119). Treating pairs as independent would understate uncertainty.

## 3. Outcomes

| Role | Variable | Definition | Range |
|---|---|---|---|
| **Primary** | `d_out_sem` | 1 − cosine similarity of anchor and comparison output embeddings (`all-MiniLM-L6-v2`, normalised; identical strings = 0) | [0, 1] |
| Key secondary | correctness flip | anchor correct ≠ comparison correct, using the item answer key (40 items) or unit tests (10 code items) | {0, 1} |
| Secondary | `d_out_char` | normalised character Levenshtein distance | [0, 1] |
| Secondary | `d_out_token` | 1 − token Jaccard similarity (whitespace tokens) | [0, 1] |
| Secondary | `answer_changed` | normalised `Final answer:` text differs (code items: test pass status differs) | {0, 1}; missing if neither output has a marker |
| Descriptive | sensitivity ratio | `d_out_sem / (0.5·d_in_char + 0.5·d_in_sem + 1e-4)` | ≥ 0; near-zero denominators flagged (< 0.01) |

Absolute output deviation is always reported beside the ratio. The ratio is unstable when the input distance is tiny, so it is not used for inference.

## 4. Inferential analyses

1. **Treatment vs control (RQ main):** Wilcoxon signed-rank test (two-sided, Pratt handling of zero differences) on (model, prompt) differences, pooled and per model. Effect size: matched-pairs rank-biserial *r*. The mean difference is reported with a cluster-bootstrap 95% CI. This is run for every outcome.
2. **Per operator (RQ1):** the same paired test for each of the 10 operators against the control, with **Holm** correction across the 10 operators. Cliff's δ is computed against the pooled control distribution. Kruskal–Wallis tests (with ε²) are run across operators and across families.
3. **Correctness (RQ1/RQ2):** flip rates (C→I, I→C) by condition, model, operator and category, each with a cluster-bootstrap CI. For each operator, an exact McNemar test on discordant pairs, Holm-corrected.
4. **Task category (RQ2):** Kruskal–Wallis test on prompt-level mean `d_out_sem`, averaged over models and operators, so that each prompt counts once. Effect size: ε².
5. **Models (RQ3):** Friedman test across models on prompt-level mean `d_out_sem`, with prompts as blocks and complete blocks only. Effect size: Kendall's *W*. Pairwise Wilcoxon tests are Holm-corrected.
6. **Mixed model (methodology §12.3):** `d_out_sem ~ operator + task_category + model + d_in_char + d_in_sem + (1 | prompt_id)`, fitted by REML in statsmodels MixedLM. The reference operator is `capitalization`.
7. **Dose–response (RQ4):** Spearman ρ between input distances and `d_out_sem`, plus binned means. The tail of the sensitivity ratio gets a GEV fit to the top 5%, and the tail size is reported.
8. **Budgeted maxima (Phase 13):** the largest observed `d_out_sem`, and the C→I count, under character and semantic input budgets ε ∈ {0.01, 0.02, 0.05, 0.10}. These are *observed maxima within the evaluated candidate set*, not global optima.
9. **RQ5 proxy:** the best of 9 non-random operators per unit is compared with `random_edit`. This oracle selection is biased upward by the winner's curse and the unequal candidate budget, which is disclosed. A **held-out** check picks each model's top operator on the even-indexed (discovery) prompts and tests it against `random_edit` on the odd-indexed (validation) prompts.

Significance level: α = 0.05, two-sided. Corrected p-values are shown wherever a family of comparisons is tested. Practical importance is judged on effect sizes and flip rates, not on p-values.

## 5. Exclusions and missing data

- Generations are deduplicated on (model, prompt, condition, operator, repetition), keeping the first. Duplicates are counted.
- Pairs whose anchor is missing are excluded with the reason `anchor_missing`.
- Generations not attempted because of provider quotas are **not imputed**. They are reported per model in the reconciliation table.
- Truncated outputs (`finish_reason` = length / MAX_TOKENS) and empty outputs are kept in the primary analysis, flagged, and removed in a robustness specification.
- Mock generations are filtered out of every analysis (`execution_mode == "live"`).

## 6. Control comparison (Task 11.8)

Controls use the same model, configuration and system prompt as the treatments, and the same anchor. Control variation is summarised per model: share of identical repeats, mean and maximum `d_out_sem`, and the answer-change and flip rates. Treatment effects are always reported as **differences from the matched control**, not against a global threshold.

## 7. Correctness evaluation

- 40 items are scored with explicit regex rules in `src/apsa/metrics/functional/answer_key.py`. Each rule was written from the reference answer and self-checked so that every reference answer scores correct.
- 10 code items are executed against item-specific unit tests in an isolated subprocess (`src/apsa/metrics/functional/code_execution.py`), and every dataset reference solution passes them.
- These are automated heuristics, not human adjudication. Phase 15 reports their limitations.

## 8. Robustness specifications (Phase 12)

The treatment-minus-control analysis is repeated for all four outcomes under these specifications:

- all pairs (primary);
- excluding truncated or empty pairs;
- excluding the high-risk operators `random_edit` and `char_substitution`;
- excluding `allam-2-7b`.

Any change in direction or significance is reported.
