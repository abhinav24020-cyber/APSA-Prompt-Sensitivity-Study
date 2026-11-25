# Perturbation operator result: QA-003 · Question answering

**Status:** `selected` · **Rule:** budget mode, d_in_char ≤ 0.10 · **Model scope:** fixed panel of 5 models, equal weights · **Evidence:** retrospective

## 1. Category recommendation

- Recommended: **punctuation** (exploratory (main_v1 discovery ranking); source: category_operator_rankings.csv (question_answering, budget 0.10))
- Category score 0.0426, coverage 10/10 complete prompts
- Why: Editing the question's final delimiter can change the form or length of the answer while keeping the requested fact fixed.
- A category recommendation is not a measurement of this prompt; the measured result follows.

## 2. Measured result for this prompt

punctuation produced the largest control-adjusted change (+0.0185) among 4 eligible, measured edits within budget 0.10. The next best eligible edit was char_substitution (+0.0146). Preservation evidence: not flagged by the retrospective audit (operator audited by a sample of 5 candidates).

| Field | Result |
|---|---|
| Prompt and category | `QA-003` · Question answering |
| Original prompt | In what year did the French Revolution begin with the storming of the Bastille? |
| Perturbed prompt | In what year did the French Revolution begin with the storming of the Bastille |
| Operator | `punctuation`: `Bastille?` → `Bastille` |
| Input change | **1 character edit(s)**, normalised distance **0.0127**, semantic input distance 0.0407 |
| Model and comparison | fixed panel of 5 models, equal weights; 5 matched model–prompt pair(s) from `main_v1` |
| Output change | Semantic distance **0.0185**, mean unchanged control distance **0.0000**, excess distance **+0.0185** |
| Functional result | Qwen 3.8 27B: correct → correct; same final answer; response length 99 → 281 characters; GPT-OSS-120B: correct → correct; same final answer; response length 94 → 95 characters; GPT-OSS-20B: correct → correct; same final answer; response length 95 → 95 characters; ALLaM-2-7B: correct → correct; same final answer; response length 100 → 100 characters; Gemini 3.1 Flash-Lite: correct → correct; same final answer; response length 99 → 90 characters |
| Tie status | unique |
| Evidence status | Measured retrospectively from stored main_v1 outputs; this prompt belongs to the discovery set that produced the category ranking, so the result is exploratory. |

### Responses of Qwen 3.8 27B (largest effect in the panel)

**Original prompt response**

```text
The French Revolution began with the storming of the Bastille on July 14, 1789.

Final answer: 1789
```

**Perturbed prompt response**

```text
The French Revolution is widely considered to have begun on July 14, 1789, with the storming of the Bastille in Paris. This event marked a pivotal moment in the overthrow of the French monarchy and the start of a period of radical social and political upheaval.

Final answer: 1789
```

## 3. All operators

| Operator | Status | Char edits | d_in_char | Raw | Control | Excess | Correctness (before → after) |
|---|---|---:|---:|---:|---:|---:|---|
| `punctuation` **(selected)** | measured | 1 | 0.0127 | 0.0185 | 0.0000 | +0.0185 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `char_substitution` | measured | 1 | 0.0127 | 0.0146 | 0.0000 | +0.0146 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `word_deletion` | measured | 4 | 0.0506 | 0.0093 | 0.0000 | +0.0093 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `capitalization` | measured | 1 | 0.0127 | 0.0000 | 0.0000 | +0.0000 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `instruction_reordering` | inapplicable: inapplicable_or_no_op |  |  |  |  |  |  |
| `synonym` | inapplicable: inapplicable_or_no_op |  |  |  |  |  |  |
| `whitespace` | over_budget: d_in_char 0.1413 exceeds budget 0.10 | 13 | 0.1413 |  |  |  |  |
| `word_insertion` | over_budget: d_in_char 0.1124 exceeds budget 0.10 | 10 | 0.1124 |  |  |  |  |
| `word_substitution` | inapplicable: inapplicable_or_no_op |  |  |  |  |  |  |

## 4. Input–output trade-off

Eligible edits not dominated by another edit with no more character edits and at least as much excess change:

- `punctuation`: 1 character edit(s) → excess +0.0185

## 5. Source records

Full responses, per-model scores and record IDs are in the JSON file next to this report.

- `qwen/qwen3.8-27b|QA-003|treatment|punctuation|1`: anchor record `8c6a8ec4-7676-47a3-a468-8425769644df`, comparison record `c7a8ce10-0f87-4d2c-bbdf-4971374e44bf`
- `openai/gpt-oss-120b|QA-003|treatment|punctuation|1`: anchor record `e2988bcc-53ec-4785-8945-472b1aca00e5`, comparison record `0126280e-afd1-4046-819c-acd37b62636d`
- `openai/gpt-oss-20b|QA-003|treatment|punctuation|1`: anchor record `8de94c55-95fd-4e8c-9918-3821c4f93d0f`, comparison record `20790614-e8f0-4d53-a7cd-36aac9412a01`
- `allam-2-7b|QA-003|treatment|punctuation|1`: anchor record `1760aecd-ba83-461f-81d8-6344b445cd9c`, comparison record `e240398f-2bb0-4c5b-a12f-2c7426530f76`
- `gemini-3.1-flash-lite|QA-003|treatment|punctuation|1`: anchor record `5387d253-507d-4449-87e5-5b9dca00c78f`, comparison record `be924b39-ee99-49af-9a7e-1a49ae79ae35`
