# Perturbation operator result: QA-008 · Question answering

**Status:** `selected` · **Rule:** budget mode, d_in_char ≤ 0.10 · **Model scope:** fixed panel of 5 models, equal weights · **Evidence:** retrospective

## 1. Category recommendation

- Recommended: **punctuation** (exploratory (main_v1 discovery ranking); source: category_operator_rankings.csv (question_answering, budget 0.10))
- Category score 0.0426, coverage 10/10 complete prompts
- Why: Editing the question's final delimiter can change the form or length of the answer while keeping the requested fact fixed.
- A category recommendation is not a measurement of this prompt; the measured result follows.

## 2. Measured result for this prompt

char_substitution produced the largest control-adjusted change (+0.0623) among 5 eligible, measured edits within budget 0.10. The next best eligible edit was word_insertion (+0.0294). Preservation evidence: not flagged by the retrospective audit (every candidate of this operator was audited).

| Field | Result |
|---|---|
| Prompt and category | `QA-008` · Question answering |
| Original prompt | Passage: 'Company X reported revenue of $4.2 billion in Q3 2024, representing an 8% increase year-over-year. Operating costs rose to $2.9 billion due to expansion in R&D.' Question: What was the Q3 2024 revenue, the year-over-year growth rate, and the operating cost? |
| Perturbed prompt | Passage: 'Company X reported revenue of $4.2 billion in Q3 2024, representing an 8% increase year-over-year. Operating costs rose to $2.9 billion due to expansion in R&D.' Question: What was the Q3 2024 r3venue, the year-over-year growth rate, and the operating cost? |
| Operator | `char_substitution`: `revenue,` → `r3venue,` |
| Input change | **1 character edit(s)**, normalised distance **0.0037**, semantic input distance 0.0219 |
| Model and comparison | fixed panel of 5 models, equal weights; 5 matched model–prompt pair(s) from `main_v1` |
| Output change | Semantic distance **0.0623**, mean unchanged control distance **0.0000**, excess distance **+0.0623** |
| Functional result | Qwen 3.8 27B: correct → correct; same final answer; response length 191 → 191 characters; GPT-OSS-120B: correct → correct; same final answer; response length 141 → 135 characters; GPT-OSS-20B: correct → correct; same final answer; response length 141 → 131 characters; ALLaM-2-7B: correct → correct; final answer text changed; response length 90 → 105 characters; Gemini 3.1 Flash-Lite: correct → correct; same final answer; response length 163 → 163 characters |
| Tie status | unique |
| Evidence status | Measured retrospectively from stored main_v1 outputs; this prompt belongs to the discovery set that produced the category ranking, so the result is exploratory. |

### Responses of GPT-OSS-20B (largest effect in the panel)

**Original prompt response**

```text
Q3 2024 revenue: $4.2 billion  
Year‑over‑year growth rate: 8 %  
Operating cost: $2.9 billion  

Final answer: 4.2 billion, 8 %, 2.9 billion
```

**Perturbed prompt response**

```text
Revenue: $4.2 billion  
Year‑over‑year growth rate: 8%  
Operating cost: $2.9 billion  

Final answer: 4.2 billion, 8%, 2.9 billion
```

## 3. All operators

| Operator | Status | Char edits | d_in_char | Raw | Control | Excess | Correctness (before → after) |
|---|---|---:|---:|---:|---:|---:|---|
| `char_substitution` **(selected)** | measured | 1 | 0.0037 | 0.0623 | 0.0000 | +0.0623 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `word_insertion` | measured | 10 | 0.0361 | 0.0294 | 0.0000 | +0.0294 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `word_deletion` | measured | 4 | 0.0150 | 0.0015 | 0.0000 | +0.0015 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `punctuation` | measured | 1 | 0.0037 | 0.0004 | 0.0000 | +0.0004 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `capitalization` | measured | 1 | 0.0037 | 0.0000 | 0.0000 | +0.0000 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `instruction_reordering` | over_budget: d_in_char 0.8165 exceeds budget 0.10 | 218 | 0.8165 |  |  |  |  |
| `synonym` | inapplicable: inapplicable_or_no_op |  |  |  |  |  |  |
| `whitespace` | over_budget: d_in_char 0.1331 exceeds budget 0.10 | 41 | 0.1331 |  |  |  |  |
| `word_substitution` | inapplicable: inapplicable_or_no_op |  |  |  |  |  |  |

## 4. Input–output trade-off

Eligible edits not dominated by another edit with no more character edits and at least as much excess change:

- `char_substitution`: 1 character edit(s) → excess +0.0623

## 5. Source records

Full responses, per-model scores and record IDs are in the JSON file next to this report.

- `qwen/qwen3.8-27b|QA-008|treatment|char_substitution|1`: anchor record `acd18ab7-291d-4461-8dfe-a947ee72e1be`, comparison record `1796c79e-8b42-4e05-a75a-a12d9bf6dffa`
- `openai/gpt-oss-120b|QA-008|treatment|char_substitution|1`: anchor record `12a8049c-88f3-45e5-8146-7da157f26642`, comparison record `3890482d-7b6e-4ced-a18f-e68d1f2a2d15`
- `openai/gpt-oss-20b|QA-008|treatment|char_substitution|1`: anchor record `a6aabc79-ecdc-4abb-a66f-4e4911dde026`, comparison record `8dc9611d-ee85-41dd-a41a-1916607e5298`
- `allam-2-7b|QA-008|treatment|char_substitution|1`: anchor record `f83b59fb-cc45-4604-95c8-abddfc7ead97`, comparison record `52c399a5-1d63-467b-bff8-1e0174bd8029`
- `gemini-3.1-flash-lite|QA-008|treatment|char_substitution|1`: anchor record `8fbd9242-d537-40ab-bb24-7bb52997632d`, comparison record `c0e12ca5-eb6c-4319-8f8d-47e677b68e2e`
