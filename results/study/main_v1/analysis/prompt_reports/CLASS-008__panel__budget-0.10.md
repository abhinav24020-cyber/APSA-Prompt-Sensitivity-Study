# Perturbation operator result: CLASS-008 · Classification

**Status:** `selected` · **Rule:** budget mode, d_in_char ≤ 0.10 · **Model scope:** fixed panel of 5 models, equal weights · **Evidence:** retrospective

## 1. Category recommendation

- Recommended: **synonym** (exploratory (main_v1 discovery ranking); source: category_operator_rankings.csv (classification, budget 0.10))
- Category score 0.0761, coverage 10/10 complete prompts
- Why: Replacing an instruction verb (e.g. Classify -> Categorize) changes the cue used to request a label while preserving the label set and evidence.
- A category recommendation is not a measurement of this prompt; the measured result follows.

## 2. Measured result for this prompt

synonym produced the largest control-adjusted change (+0.2171) among 6 eligible, measured edits within budget 0.10. The next best eligible edit was punctuation (+0.1705). Preservation evidence: not flagged by the retrospective audit (every candidate of this operator was audited).

| Field | Result |
|---|---|
| Prompt and category | `CLASS-008` · Classification |
| Original prompt | Classify the severity of this software issue report as Critical, High, Medium, or Low: 'The application crashes immediately on launch for all Windows 11 users with an unhandled memory exception.' |
| Perturbed prompt | Categorize the severity of this software issue report as Critical, High, Medium, or Low: 'The application crashes immediately on launch for all Windows 11 users with an unhandled memory exception.' |
| Operator | `synonym`: `Classify` → `Categorize` |
| Input change | **8 character edit(s)**, normalised distance **0.0406**, semantic input distance 0.0082 |
| Model and comparison | fixed panel of 5 models, equal weights; 5 matched model–prompt pair(s) from `main_v1` |
| Output change | Semantic distance **0.2171**, mean unchanged control distance **0.0000**, excess distance **+0.2171** |
| Functional result | Qwen 3.8 27B: correct → correct; same final answer; response length 437 → 437 characters; GPT-OSS-120B: correct → correct; same final answer; response length 33 → 33 characters; GPT-OSS-20B: correct → correct; same final answer; response length 32 → 32 characters; ALLaM-2-7B: correct → correct; final answer text changed; response length 315 → 43 characters; Gemini 3.1 Flash-Lite: correct → correct; same final answer; response length 251 → 179 characters |
| Tie status | unique |
| Evidence status | Measured retrospectively from stored main_v1 outputs; this prompt belongs to the discovery set that produced the category ranking, so the result is exploratory. |

### Responses of ALLaM-2-7B (largest effect in the panel)

**Original prompt response**

```text
Final answer: Critical

The reported issue is classified as Critical because the application crashes immediately on launch, affecting all Windows 11 users with an unhandled memory exception. This issue prevents users from using the software and poses a severe problem that needs immediate attention and resolution.
```

**Perturbed prompt response**

```text
Category: Critical

Final answer: Critical
```

## 3. All operators

| Operator | Status | Char edits | d_in_char | Raw | Control | Excess | Correctness (before → after) |
|---|---|---:|---:|---:|---:|---:|---|
| `synonym` **(selected)** | measured | 8 | 0.0406 | 0.2171 | 0.0000 | +0.2171 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `punctuation` | measured | 1 | 0.0051 | 0.1705 | 0.0000 | +0.1705 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `word_deletion` | measured | 4 | 0.0205 | 0.0821 | 0.0000 | +0.0821 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `char_substitution` | measured | 1 | 0.0051 | 0.0472 | 0.0000 | +0.0472 | Qwen 3.8 27B correct→incorrect; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `capitalization` | measured | 1 | 0.0051 | 0.0412 | 0.0000 | +0.0412 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `word_insertion` | measured | 10 | 0.0488 | 0.0403 | 0.0000 | +0.0403 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `instruction_reordering` | inapplicable: inapplicable_or_no_op |  |  |  |  |  |  |
| `whitespace` | over_budget: d_in_char 0.1295 exceeds budget 0.10 | 29 | 0.1295 |  |  |  |  |
| `word_substitution` | inapplicable: inapplicable_or_no_op |  |  |  |  |  |  |

## 4. Input–output trade-off

Eligible edits not dominated by another edit with no more character edits and at least as much excess change:

- `punctuation`: 1 character edit(s) → excess +0.1705
- `synonym`: 8 character edit(s) → excess +0.2171

## 5. Source records

Full responses, per-model scores and record IDs are in the JSON file next to this report.

- `qwen/qwen3.8-27b|CLASS-008|treatment|synonym|1`: anchor record `3e38b2df-26ce-4b22-9725-b0cfd205c56b`, comparison record `6bc82af0-31ed-4950-a5b6-4d2575b2b4ba`
- `openai/gpt-oss-120b|CLASS-008|treatment|synonym|1`: anchor record `7b3de0c8-8afd-47e4-8c07-3c2a3117dd6a`, comparison record `6d995d53-2e1f-4959-a862-6f4fe483fa6c`
- `openai/gpt-oss-20b|CLASS-008|treatment|synonym|1`: anchor record `dc055747-6b55-404c-a2f5-5cf9c9887db6`, comparison record `4e5d53e8-c4cc-4517-a9f1-bd9152d817a8`
- `allam-2-7b|CLASS-008|treatment|synonym|1`: anchor record `480f9016-2a83-4f96-9655-eef96aeedd5d`, comparison record `15dc5c16-13d3-48ca-a5e9-40238cdc8591`
- `gemini-3.1-flash-lite|CLASS-008|treatment|synonym|1`: anchor record `9afa096c-c8eb-45f8-bc8c-e14d94603fae`, comparison record `234eca4b-3101-4f39-8bef-893d84fec9d3`
