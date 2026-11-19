# Repository Baseline Audit — Phases 1–10 (before Phase 11 work)

**Date:** 2026-11-19 · **Commit audited:** `067a63d` (branch `main`, clean working tree)
**Method:** the source, configuration, tests, data and docs were inspected; the test suite was run; and the audit probed the providers' model-list endpoints plus one 1-token request per candidate model to confirm availability. Claims in older documents were not accepted without evidence.

Status labels: PASS · PASS WITH LIMITATIONS · BLOCKED · FAIL · NOT STARTED · NOT APPLICABLE.

| Phase | Claimed status | Actual status | Evidence | Gaps / risks found | Action taken |
|---|---|---|---|---|---|
| 1 Methodology | Completed | **PASS** | `docs/research_methodology.md` defines RQ1–RQ5, H1–H5, variables, objective | RQ wording assumes a summarisation task and syntactic operators that the dataset/operators do not have | RQ scope limits stated in `analysis_plan.md` |
| 2 Architecture | Completed | **PASS WITH LIMITATIONS** | `src/apsa/*` modules, typed records | Two parallel provider packages (`llm_providers/`, `providers/`) and two runners. Several stub modules (`data/cnn_dailymail.py`, `mbpp.py`, …) raise `NotImplementedError` | Main study uses `llm_providers/`; stubs left untouched and documented |
| 3 Dataset | 246 prompts (old report) / 100 (newer) | **PASS WITH LIMITATIONS** | `data/baseline_prompts.csv`: **100 rows, 20 per category**, 5 categories; 88 items `exact_match`/`code_execution` | The 246 figure is wrong. References are not expert-reviewed | All 10 sampled code references now pass execution tests; 40 sampled answers have explicit regex keys |
| 4 Perturbation engine | Completed | **PASS WITH LIMITATIONS** | 11 registered operators, 198 tests passing | `formatting_modification` = "Please " prefix (duplicates insertion). Insertions do not re-case the following word. `random_edit` can corrupt numbers (e.g. "20%"→"2h%"), flagged high-risk | Main study uses 10 operators; skipped candidates logged with reasons |
| 5 Input distance | Char/word/semantic done; syntactic planned | **PASS WITH LIMITATIONS** | Lexical (Levenshtein) and semantic (MiniLM cosine) implemented and tested | `syntactic.py` tree-edit distance raises `NotImplementedError` (not done, correctly documented) | Not used; listed in limitations |
| 6 LLM providers | Gemini/OpenAI/Groq done | **FAIL → fixed** | `llm_providers/*` | (a) **Groq runner aborted on any HTTP 429, including 8,000 tokens-per-minute limits**: the root cause of the 9-pair live run. (b) Gemini provider used the deprecated `google-generativeai` SDK, and the configured `gemini-1.5-*` models are no longer served. (c) No system-prompt support. (d) No HTTP timeout on Gemini (a request hung indefinitely). | 429s classified (minute/day) with parsed retry delays, and the runner waits out short limits. Gemini ported to `google-genai` with a 90 s timeout. System prompt and `reasoning_effort` supported |
| 7 Control experiment | Infrastructure done, execution pending | **BLOCKED → resolved** | `results/` is git-ignored and absent on this machine, so **0 real control records were available** | Earlier pilot artifacts cited in docs cannot be inspected here | New live study collects 2 unchanged-prompt controls per (model, prompt) |
| 8 Pilot | 9 pairs live (rate-limited) | **BLOCKED → resolved** | Same as above | Pilot design re-generated the original prompt for every perturbation, doubling calls | New anchor/control/treatment design; resumable runner |
| 9 Output deviation | Completed | **PASS WITH LIMITATIONS** | `metrics/output_distance.py` tested | `semantic_similarity()` silently returns *string* similarity when semantic mode is off (mislabelled metric). Pilot correctness looked only at the last output line | New analysis computes embedding distance explicitly. Correctness via answer key and unit tests |
| 10 Sensitivity | Completed, with CI | **PASS WITH LIMITATIONS** | `analysis/sensitivity.py` tested | `confidence_interval_output_deviation` is a record-level *t* interval (it ignores prompt clustering) and returns `(0.0, 0.0)` for empty input, a fabricated value | Not reused for inference. Replaced by the prompt-cluster bootstrap in `analysis/study_statistics.py` |

**Environment findings.** The system Python had no `pytest`, `Levenshtein`, `rouge-score` or `sentence-transformers`. The latest `transformers` is incompatible with the installed torch. I created a project `.venv` (`--system-site-packages`) and pinned `transformers==4.46.3` and `sentence-transformers==3.3.1`. In that venv the original suite gives **198 passed**.

**Provider availability (2026-11-19).** Groq: `qwen/qwen3.8-27b`, `openai/gpt-oss-120b`, `openai/gpt-oss-20b`, `allam-2-7b` (free tier: 1,000 requests/day, 6,000–8,000 tokens/min per model). Gemini: `gemini-3.1-flash-lite` available. `gemini-2.5-flash-lite` returned 404 for new users, and `gemma-4-26b` returned 503.

## Decision

**READY FOR REAL CONTROL/PILOT EXECUTION**, after the provider fixes above. Phase 11 engineering could proceed in parallel against clearly separated mock fixtures, and the empirical components would remain blocked until live data existed. Live data was then collected in study `main_v1` (see `phases_11_to_17_verification.md`).
