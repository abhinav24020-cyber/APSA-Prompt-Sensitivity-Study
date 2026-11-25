# Perturbation operator result: CLASS-003 · Classification

**Status:** `selected` · **Rule:** budget mode, d_in_char ≤ 0.10 · **Model scope:** fixed panel of 5 models, equal weights · **Evidence:** retrospective

## 1. Category recommendation

- Recommended: **synonym** (exploratory (main_v1 discovery ranking); source: category_operator_rankings.csv (classification, budget 0.10))
- Category score 0.0761, coverage 10/10 complete prompts
- Why: Replacing an instruction verb (e.g. Classify -> Categorize) changes the cue used to request a label while preserving the label set and evidence.
- A category recommendation is not a measurement of this prompt; the measured result follows.

## 2. Measured result for this prompt

word_insertion produced the largest control-adjusted change (+0.1001) among 6 eligible, measured edits within budget 0.10. The next best eligible edit was char_substitution (+0.0815). Preservation evidence: not flagged by the retrospective audit (operator audited by a sample of 5 candidates).

| Field | Result |
|---|---|
| Prompt and category | `CLASS-003` · Classification |
| Original prompt | Classify the user intent of the message 'I was charged twice on my invoice this month' into one of [Billing_Issue, Account_Cancellation, Product_Inquiry, General_Feedback]. |
| Perturbed prompt | Carefully Classify the user intent of the message 'I was charged twice on my invoice this month' into one of [Billing_Issue, Account_Cancellation, Product_Inquiry, General_Feedback]. |
| Operator | `word_insertion`: `∅` → `Carefully` |
| Input change | **10 character edit(s)**, normalised distance **0.0549**, semantic input distance 0.0168 |
| Model and comparison | fixed panel of 5 models, equal weights; 5 matched model–prompt pair(s) from `main_v1` |
| Output change | Semantic distance **0.1001**, mean unchanged control distance **0.0000**, excess distance **+0.1001** |
| Functional result | Qwen 3.8 27B: correct → correct; same final answer; response length 182 → 192 characters; GPT-OSS-120B: correct → correct; same final answer; response length 27 → 41 characters; GPT-OSS-20B: correct → correct; same final answer; response length 42 → 43 characters; ALLaM-2-7B: correct → correct; response length 153 → 88 characters; Gemini 3.1 Flash-Lite: correct → correct; same final answer; response length 141 → 138 characters |
| Tie status | unique |
| Evidence status | Measured retrospectively from stored main_v1 outputs; this prompt belongs to the discovery set that produced the category ranking, so the result is exploratory. |

### Responses of Gemini 3.1 Flash-Lite (largest effect in the panel)

**Original prompt response**

```text
The user intent for the message "I was charged twice on my invoice this month" is classified as a billing issue.

Final answer: Billing_Issue
```

**Perturbed prompt response**

```text
The user is reporting a discrepancy regarding a payment, which falls under the category of a billing problem.

Final answer: Billing_Issue
```

## 3. All operators

| Operator | Status | Char edits | d_in_char | Raw | Control | Excess | Correctness (before → after) |
|---|---|---:|---:|---:|---:|---:|---|
| `word_insertion` **(selected)** | measured | 10 | 0.0549 | 0.1001 | 0.0000 | +0.1001 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `char_substitution` | measured | 1 | 0.0058 | 0.0815 | 0.0000 | +0.0815 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `punctuation` | measured | 1 | 0.0058 | 0.0691 | 0.0000 | +0.0691 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `capitalization` | measured | 1 | 0.0058 | 0.0368 | 0.0000 | +0.0368 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `synonym` | measured | 8 | 0.0460 | 0.0328 | 0.0000 | +0.0328 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `word_deletion` | measured | 4 | 0.0233 | 0.0202 | 0.0000 | +0.0202 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `instruction_reordering` | inapplicable: inapplicable_or_no_op |  |  |  |  |  |  |
| `whitespace` | over_budget: d_in_char 0.1134 exceeds budget 0.10 | 22 | 0.1134 |  |  |  |  |
| `word_substitution` | inapplicable: inapplicable_or_no_op |  |  |  |  |  |  |

## 4. Input–output trade-off

Eligible edits not dominated by another edit with no more character edits and at least as much excess change:

- `char_substitution`: 1 character edit(s) → excess +0.0815
- `word_insertion`: 10 character edit(s) → excess +0.1001

## 5. Source records

Full responses, per-model scores and record IDs are in the JSON file next to this report.

- `qwen/qwen3.8-27b|CLASS-003|treatment|word_insertion|1`: anchor record `98021f7e-4e93-43cd-abdb-e76a13fc3c6c`, comparison record `115e1e34-58e2-4e48-991c-8ac7569191a3`
- `openai/gpt-oss-120b|CLASS-003|treatment|word_insertion|1`: anchor record `cd985336-c8f3-45bc-a98d-df3a03b918bd`, comparison record `6ef791d9-2176-4117-b388-d5a809a7fd83`
- `openai/gpt-oss-20b|CLASS-003|treatment|word_insertion|1`: anchor record `2f495313-8ff0-40de-b4d7-19f97ec92477`, comparison record `af732136-cf9d-4516-ac3b-5afea054f0ab`
- `allam-2-7b|CLASS-003|treatment|word_insertion|1`: anchor record `3b8a1a08-55e5-4c2b-9552-45331fe45c2d`, comparison record `0a6dc286-eb68-463c-bc0f-fc4c399e0658`
- `gemini-3.1-flash-lite|CLASS-003|treatment|word_insertion|1`: anchor record `78936776-8370-4ae6-922d-f10d86675726`, comparison record `6956e2b9-3c4d-4b69-8304-3cf1ed8c816a`
