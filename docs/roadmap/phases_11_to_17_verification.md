# APSA Phases 11–17 — Verification Report

**Date:** 2026-11-20 · **Base commit:** `067a63d` (this work is committed on top of it) · **Study:** `main_v1`
**Environment:** Windows 10, Python 3.12.10, `.venv` with `requirements-lock.txt`
**Status labels:** PASS · PASS WITH LIMITATIONS · BLOCKED · FAIL · NOT STARTED · NOT APPLICABLE

## Summary

| Phase | Engineering | Empirical (real data) | Decision |
|---|---|---|---|
| 11 Statistical analysis | PASS | PASS WITH LIMITATIONS | Complete with accepted limitations |
| 12 Robustness and reliability | PASS | PASS WITH LIMITATIONS | Complete with accepted limitations |
| 13 Adversarial perturbation analysis | PASS | PASS WITH LIMITATIONS (no token-level search) | Complete with accepted limitations |
| 14 Comparative evaluation | PASS | PASS WITH LIMITATIONS (observational) | Complete with accepted limitations |
| 15 Explainability and error analysis | PASS | PASS WITH LIMITATIONS (no human annotators) | Complete with accepted limitations |
| 16 Reproducibility and reporting | PASS | PASS WITH LIMITATIONS | Complete with accepted limitations |
| 17 Integration, demo, release | PASS WITH LIMITATIONS | — | Software-complete; presentation slides not produced |

**Overall:** the framework is **software-complete**. The planned main study is **empirically completed** for its declared scope: 5 models × 50 prompts, temperature 0. Every limitation below is disclosed in the paper (§6) and needs the user's acceptance (decision 2, "complete with accepted limitations").

## Test evidence

| Command | Result |
|---|---|
| `.\.venv\Scripts\python.exe -m pytest -q` | **231 passed, 0 failed, 0 skipped** (≈60 s) |
| of which pre-existing Phase 1–10 tests | 198 passed (regression check: nothing broken) |
| of which new tests (`tests/unit/test_study_pipeline.py`) | 33 passed: statistics helpers against hand calculations and scipy, answer key, code execution, rate-limit parsing, runner selection and 429 handling, mock end-to-end with resume, effect size, hypothesis tests, mixed model, EVT |
| `experiments/run_study.py --mock` | 2,875 mock generations; resume adds 0 duplicates (mock data stored separately in `results/mock_runs`) |
| `experiments/analyze_study.py` | Completes; the 6 built-in consistency checks are all zero |

## Data and experiment evidence

| Item | Value | Evidence |
|---|---|---|
| Real LLM generations | **2,870 live** (575 × 4 models + 570) | `results/study/main_v1/raw/generations__*.jsonl`, unique `record_id` per generation |
| Failed requests | 7 recorded: 5 GPT-OSS-20B HTTP 400 "tool_use_failed" (not retried successfully, not imputed); 2 Gemini (1 timeout, 1 daily quota), both later succeeded on resume | `raw/failures__*.jsonl` |
| Mock executions | Separate directory; filtered out by `execution_mode == "live"` | `results/mock_runs/` |
| Synthetic fixtures | Unit tests only; never in study outputs | `tests/unit/test_study_pipeline.py` |
| Exclusions | 0 pairs (no anchor missing); 0 duplicates; 0 malformed lines | `analysis/results.json → data_integrity` |
| Analysis pairs | 2,620 (2,120 treatment, 500 control) | `processed/analysis_pairs.csv` |
| Provenance | Config SHA-256, dataset SHA-256, selected prompt IDs, per-run model status, raw-file SHA-256 | `study_manifest.json`, `results.json → data_integrity.raw_files` |

## Phase 11 — Statistical analysis

| Checkpoint | Status | Evidence / notes |
|---|---|---|
| CP11.1 Raw-data integrity | PASS | Raw JSONL is append-only and never rewritten by the analysis. Checksums and line counts are recorded. Duplicates, malformed lines and failures are counted separately. Nothing is imputed. |
| CP11.2 Analysis plan | PASS WITH LIMITATIONS | `docs/roadmap/analysis_plan.md`. The primary outcome, unit, clustering, tests, corrections and exclusions are all specified. **Limitation:** the plan was written during data collection, after a partial look at early results; this is disclosed. |
| CP11.3 Analysis dataset | PASS | Deterministic transformation. Every pair links to its `anchor_record_id` and `comparison_record_id`. Counts reconcile per model (`reconciliation`). |
| CP11.4 Metric review | PASS WITH LIMITATIONS | Metric definitions are in the plan and paper §3.1. Near-zero denominators are flagged (534 pairs). Absolute deviation is reported beside the ratio. Phase 10 `confidence_interval_output_deviation` was inspected and **not reused**: it is record-level and returns (0, 0) for empty input. Syntactic distance is unimplemented. |
| CP11.5 Descriptive statistics | PASS | `results.json → descriptive`. Every summary reports *n*. Figures 1–7. |
| CP11.6 Confidence intervals | PASS | Prompt-level cluster bootstrap (4,000 resamples). Tested against hand-computed means, empty and single-cluster inputs, and shown to widen under within-cluster correlation. |
| CP11.7 Inferential analysis | PASS | Wilcoxon (Pratt) at the model–prompt unit, Holm across operators, Kruskal–Wallis, Friedman, McNemar and a mixed model. Effect sizes: rank-biserial, Cliff's δ, ε², Kendall's *W*. The mixed model initially returned a **degenerate lbfgs fit**; it was refitted with Powell (agreeing with Nelder–Mead). |
| CP11.8 Control comparison | PASS | 2 controls per model–prompt with identical settings and the same anchor. Control repeatability is reported per model. |
| CP11.9 Statistical report | PASS | `analysis/results_tables.md`, paper §4. Every number traces to `results.json`. Null results are reported (H1, H5 not supported). |

## Phase 12 — Robustness and reliability

| Checkpoint | Status | Evidence / notes |
|---|---|---|
| CP12.1 Repeatability | PASS WITH LIMITATIONS | 500 control pairs: 93% identical, 0 correctness flips. Determinism is not claimed. Only 2 repeats per unit and temperature 0 only. |
| CP12.2 Control coverage | PASS | All 5 models × 50 prompts × 2 controls; the same strata as the treatments. |
| CP12.3 Metric edge cases | PASS | Identical, empty and missing outputs, values outside [0, 1] and NaN are checked on every run. A **bug was found and fixed**: pandas stores missing final answers as NaN and NaN ≠ NaN, so they were counted as answer changes. The check now aborts the analysis if this recurs. |
| CP12.4 Semantic validity | PASS WITH LIMITATIONS | `config/experiments/main_study_semantic_audit.yaml`: 5 operators fully audited (175 candidates), the others sampled. **15 meaning-altering candidates found**, and an audit-valid robustness specification was added. **Limitation:** not validated by independent human annotators. |
| CP12.5 Robustness of conclusions | PASS | Specification curve: 5 specifications × 4 metrics. The treatment > control direction and significance hold in all 20 (`robustness.specification_curve`). |
| CP12.6 Closeout | PASS | Limitations listed in paper §6. |

## Phase 13 — Adversarial perturbation analysis

| Checkpoint | Status | Evidence / notes |
|---|---|---|
| CP13.1 Operator inventory | PASS WITH LIMITATIONS | 10 operators used, with inapplicable candidates logged. `formatting_modification` was excluded because it duplicates insertion. No syntactic operator exists. |
| CP13.2 Budgets | PASS | Character and semantic budgets ε ∈ {0.01, 0.02, 0.05, 0.10}. Budget compliance is computed per candidate before analysis. Semantic risk is a separate field. |
| CP13.3 Candidate traceability | PASS | `candidates.jsonl`: all 500 candidates, accepted and rejected (with reason), with input distances and IDs linked to generations. |
| CP13.4 Search-budget controls | PASS | One candidate per operator per prompt (seed 42), with a fixed and disclosed budget. No paid calls (free tiers). |
| CP13.5 Ranking | PASS | `budget_maxima` reports absolute deviation and input distance together, with an argmax link to the pair. |
| CP13.6 Search validity | PASS WITH LIMITATIONS | The oracle best-of-9 selection is reported with a winner's-curse caveat. A **held-out** discovery/validation split was run. **No token-level greedy or beam search**, so RQ5 is only a proxy. |
| CP13.7 Report | PASS | Paper §4.8–4.9: maxima are labelled as observed within the evaluated set. |

## Phase 14 — Comparative evaluation

| Checkpoint | Status | Evidence / notes |
|---|---|---|
| CP14.1 Design | PASS | Exact model IDs and settings are in the config and manifest. All models get the same prompts and candidates. Differences in providers' sampling stacks are disclosed. |
| CP14.2 Matched data | PASS | The Friedman test uses complete blocks (50/50 prompts). The 5 missing GPT-OSS-20B pairs are reported. |
| CP14.3–14.5 Comparisons and reporting | PASS WITH LIMITATIONS | Friedman test, Holm pairwise tests and the mixed model. Conclusions are observational: model families are confounded with size. |

## Phase 15 — Explainability and error analysis

| Checkpoint | Status | Evidence / notes |
|---|---|---|
| CP15.1 Taxonomy | PASS | 8 mutually exclusive labels ordered by severity (`taxonomy()` in `analyze_study.py`). |
| CP15.2 Case selection | PASS | Rule-based: smallest-input audit-valid flips, meaning-altering flips, largest change without a flip, changed controls, and I→C flips (`case_studies.json`). |
| CP15.3 Comparison tooling | PASS | `scripts/build_output_viewer.py` builds an HTML viewer of all 2,620 pairs with word diffs, untruncated outputs and metrics. `experiments/demo.py` shows a single pair end to end. |
| CP15.4 Evaluation validity | PASS WITH LIMITATIONS | Answer key: the self-check accepts all references, and an audit of 40 randomly sampled verdicts found 39 correct; the one error was fixed with a regression test. Code: all 10 reference solutions pass. The answer-string metric is documented as an upper bound (9 of 14 sampled changes were rewordings). |
| CP15.5 Human annotation | NOT STARTED | No independent human annotators. A blinded annotation sheet is recommended. |
| CP15.6 Error report | PASS | Paper §4.5 and §4.10. All 18 audit-valid C→I flips were reviewed: 14 genuine, 3 format, 1 truncation. |

## Phase 16 — Reproducibility and reporting

| Checkpoint | Status | Evidence / notes |
|---|---|---|
| CP16.1 Metadata | PASS | Each generation stores the model, provider, request config (system prompt in the config), finish reason, tokens, latency, timestamp and record ID. No secrets are stored (the `.env` is git-ignored). |
| CP16.2 Reproduction procedure | PASS WITH LIMITATIONS | Command-line, config-driven and resumable runs (README). Provider non-determinism is disclosed. The full study was not re-run a second time (quota). |
| CP16.3 Lineage | PASS | Raw → processed → analysis directories, checksums, and processed data rebuilt from raw on every analysis run. |
| CP16.4 Environment | PASS | `requirements-lock.txt` (including the torch metadata quirk). Environment variable names are documented in `.env.example`. |
| CP16.5 Documentation | PASS WITH LIMITATIONS | README, analysis plan, baseline audit, this report and the paper. Older Phase 1–10 documents are kept as historical records; some of their statements are superseded, as noted in the baseline audit. |
| CP16.6 Research-claim audit | PASS | Every empirical claim in the paper was cross-checked against `results.json`. Two drafting errors (72% → 66%, and the flip-review counts) were corrected. References verified, including web checks for the four most recent. |

## Phase 17 — Final integration

| Checkpoint | Status | Evidence / notes |
|---|---|---|
| CP17.1 End-to-end traceability | PASS | `demo.py` traces dataset → perturbation → distances → raw outputs → metrics → pair ID. |
| CP17.2 Test suites | PASS | 231 passed, none skipped. |
| CP17.3 Real experiment audit | PASS | Scheduled 2,875 vs succeeded 2,870 vs failed 5 (reconciled per model). |
| CP17.4 RQ evidence matrix | PASS | See below. |
| CP17.5 Demo | PASS | `demo.py` defaults to recorded data (labelled as such). `--live` is clearly separated. No keys are printed. |
| CP17.6 Presentation | NOT STARTED | Slides not yet produced. |
| CP17.7 Release | PASS WITH LIMITATIONS | Released as a new GitHub repository at the user's request. No credentials are committed. The study data is included. |

## Research-question evidence matrix (CP17.4)

| RQ | Data and analysis | Result | Supported? |
|---|---|---|---|
| RQ1 perturbation type | 2,120 treatment pairs; per-operator Wilcoxon (Holm), Kruskal–Wallis, mixed model | All operators exceed controls. Reordering is largest (0.121) and deletion smallest (0.040). Surface edits are **not** the most disruptive. | Answered; **H1 not supported** |
| RQ2 task category | Prompt-level Kruskal–Wallis (*p* = 0.004, ε² = 0.31); flip rates | Reasoning is most sensitive and code least. Mathematics has the highest flip rate. | Answered; **H2 partly supported** |
| RQ3 model scale and alignment | Friedman test (*p* = 0.0006), Holm pairwise, mixed model | The 7B model is most fragile; strong models flip 0.9–3.1%. GPT-OSS 120B vs 20B: not significant. | Partly answered (observational); **H3 consistent, not established** |
| RQ4 input–output relation | Spearman (ρ ≤ 0.14), binned means, budget maxima, EVT tail | Weak dependence: 39% of pairs show no change, others jump from one-character edits | Answered descriptively; **H4 consistent**, no formal change-point test |
| RQ5 search vs random | Oracle best-of-9 (1.64×), held-out selection (not better than random) | No evidence that fixed operator selection generalises | Proxy only; **H5 not supported**; token search is future work |

## Open issues

| Issue | Severity | Blocks the gate? |
|---|---|---|
| Semantic audit and evaluator audit not validated by independent human annotators | Medium | No (disclosed); recommended before publication |
| No temperature 0.7 condition; only 2 control repeats | Medium | No (disclosed) |
| No token-level adversarial search (RQ5) | Medium | No (disclosed as future work) |
| 50 of 100 prompts used | Low | No |
| Syntactic input distance unimplemented | Low | No |
| Presentation slides not produced | Low | No |

## Final decision

**PHASE COMPLETE WITH ACCEPTED LIMITATIONS — USER DECISION REQUIRED** for Phases 11–16. Phase 17 is **software-complete**, with presentation slides outstanding. No synthetic data is reported as real, and no raw data was overwritten.
