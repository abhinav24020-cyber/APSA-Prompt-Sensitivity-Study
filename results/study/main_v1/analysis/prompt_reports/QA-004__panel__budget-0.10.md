# Perturbation operator result: QA-004 · Question answering

**Status:** `selected` · **Rule:** budget mode, d_in_char ≤ 0.10 · **Model scope:** fixed panel of 5 models, equal weights · **Evidence:** retrospective

## 1. Category recommendation

- Recommended: **punctuation** (exploratory (main_v1 discovery ranking); source: category_operator_rankings.csv (question_answering, budget 0.10))
- Category score 0.0426, coverage 10/10 complete prompts
- Why: Editing the question's final delimiter can change the form or length of the answer while keeping the requested fact fixed.
- A category recommendation is not a measurement of this prompt; the measured result follows.

## 2. Measured result for this prompt

word_deletion produced the largest control-adjusted change (+0.0046) among 4 eligible, measured edits within budget 0.10. The next best eligible edit was punctuation (+0.0025). Preservation evidence: not flagged by the retrospective audit (every candidate of this operator was audited).

| Field | Result |
|---|---|
| Prompt and category | `QA-004` · Question answering |
| Original prompt | What is the longest river in South America and into which ocean does it empty? |
| Perturbed prompt | What is longest river in South America and into which ocean does it empty? |
| Operator | `word_deletion`: `the` → `∅` |
| Input change | **4 character edit(s)**, normalised distance **0.0513**, semantic input distance 0.0019 |
| Model and comparison | fixed panel of 5 models, equal weights; 5 matched model–prompt pair(s) from `main_v1` |
| Output change | Semantic distance **0.0046**, mean unchanged control distance **0.0000**, excess distance **+0.0046** |
| Functional result | Qwen 3.8 27B: correct → correct; same final answer; response length 135 → 143 characters; GPT-OSS-120B: correct → correct; same final answer; response length 147 → 148 characters; GPT-OSS-20B: correct → correct; same final answer; response length 140 → 148 characters; ALLaM-2-7B: correct → correct; same final answer; response length 143 → 143 characters; Gemini 3.1 Flash-Lite: correct → correct; same final answer; response length 139 → 139 characters |
| Tie status | unique |
| Evidence status | Measured retrospectively from stored main_v1 outputs; this prompt belongs to the discovery set that produced the category ranking, so the result is exploratory. |

### Responses of Qwen 3.8 27B (largest effect in the panel)

**Original prompt response**

```text
The longest river in South America is the Amazon River. It empties into the Atlantic Ocean.

Final answer: Amazon River, Atlantic Ocean
```

**Perturbed prompt response**

```text
The longest river in South America is the **Amazon River**. It empties into the **Atlantic Ocean**.

Final answer: Amazon River; Atlantic Ocean
```

## 3. All operators

| Operator | Status | Char edits | d_in_char | Raw | Control | Excess | Correctness (before → after) |
|---|---|---:|---:|---:|---:|---:|---|
| `word_deletion` **(selected)** | measured | 4 | 0.0513 | 0.0046 | 0.0000 | +0.0046 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `punctuation` | measured | 1 | 0.0128 | 0.0025 | 0.0000 | +0.0025 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `capitalization` | measured | 1 | 0.0128 | 0.0020 | 0.0000 | +0.0020 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `char_substitution` | measured | 1 | 0.0128 | 0.0020 | 0.0000 | +0.0020 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `instruction_reordering` | inapplicable: inapplicable_or_no_op |  |  |  |  |  |  |
| `synonym` | inapplicable: inapplicable_or_no_op |  |  |  |  |  |  |
| `whitespace` | over_budget: d_in_char 0.1522 exceeds budget 0.10 | 14 | 0.1522 |  |  |  |  |
| `word_insertion` | over_budget: d_in_char 0.1136 exceeds budget 0.10 | 10 | 0.1136 |  |  |  |  |
| `word_substitution` | inapplicable: inapplicable_or_no_op |  |  |  |  |  |  |

## 4. Input–output trade-off

Eligible edits not dominated by another edit with no more character edits and at least as much excess change:

- `punctuation`: 1 character edit(s) → excess +0.0025
- `word_deletion`: 4 character edit(s) → excess +0.0046

## 5. Source records

Full responses, per-model scores and record IDs are in the JSON file next to this report.

- `qwen/qwen3.8-27b|QA-004|treatment|word_deletion|1`: anchor record `06f933ad-af0d-4389-a549-b48e58ed32b6`, comparison record `bfa2e0d0-7061-428e-8fe3-4cb150a75e5c`
- `openai/gpt-oss-120b|QA-004|treatment|word_deletion|1`: anchor record `b14fe748-d8ba-4616-89fa-6bbda2c6f8ed`, comparison record `3d82f273-6b5e-4744-8fbd-d2a3d5d96108`
- `openai/gpt-oss-20b|QA-004|treatment|word_deletion|1`: anchor record `e69fb7a3-3ed2-4564-9587-0d77799f500a`, comparison record `a8342cd2-4377-4366-9885-6c66a2d94062`
- `allam-2-7b|QA-004|treatment|word_deletion|1`: anchor record `1e1cb6f4-eea5-4188-a000-7c113420c6d7`, comparison record `9ec0bc71-607c-4b70-a19c-3ce85cb39e90`
- `gemini-3.1-flash-lite|QA-004|treatment|word_deletion|1`: anchor record `bf605c79-b867-4721-8c3a-a3d456e85a4f`, comparison record `495db2b3-7cde-4c15-b019-584c494c2218`
