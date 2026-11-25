# Perturbation operator result: MATH-006 · Mathematical reasoning

**Status:** `selected` · **Rule:** budget mode, d_in_char ≤ 0.10 · **Model scope:** fixed panel of 5 models, equal weights · **Evidence:** retrospective

## 1. Category recommendation

- Recommended: **char_substitution** (exploratory (main_v1 discovery ranking); source: category_operator_rankings.csv (mathematical_reasoning, budget 0.10))
- Category score 0.0853, coverage 8/8 complete prompts
- Why: A typo in prose changes how the task is rendered while leaving quantities and the requested result intact.
- A category recommendation is not a measurement of this prompt; the measured result follows.

## 2. Measured result for this prompt

capitalization produced the largest control-adjusted change (+0.0921) among 4 eligible, measured edits within budget 0.10. The next best eligible edit was word_deletion (+0.0378). Preservation evidence: not flagged by the retrospective audit (operator audited by a sample of 5 candidates).

| Field | Result |
|---|---|
| Prompt and category | `MATH-006` · Mathematical reasoning |
| Original prompt | Find the remainder when 7^100 is divided by 5. |
| Perturbed prompt | find the remainder when 7^100 is divided by 5. |
| Operator | `capitalization`: `Find` → `find` |
| Input change | **1 character edit(s)**, normalised distance **0.0217**, semantic input distance 0.0000 |
| Model and comparison | fixed panel of 5 models, equal weights; 5 matched model–prompt pair(s) from `main_v1` |
| Output change | Semantic distance **0.0921**, mean unchanged control distance **0.0000**, excess distance **+0.0921** |
| Functional result | Qwen 3.8 27B: correct → correct; same final answer; response length 1167 → 1238 characters; GPT-OSS-120B: correct → correct; same final answer; response length 36 → 37 characters; GPT-OSS-20B: correct → correct; same final answer; response length 18 → 37 characters; ALLaM-2-7B: incorrect → incorrect; final answer text changed; response length 551 → 636 characters; Gemini 3.1 Flash-Lite: correct → correct; same final answer; response length 569 → 548 characters |
| Tie status | unique |
| Evidence status | Measured retrospectively from stored main_v1 outputs; this prompt belongs to the discovery set that produced the category ranking, so the result is exploratory. |

### Responses of GPT-OSS-20B (largest effect in the panel)

**Original prompt response**

```text
1

Final answer: 1
```

**Perturbed prompt response**

```text
The remainder is 1.  
Final answer: 1
```

## 3. All operators

| Operator | Status | Char edits | d_in_char | Raw | Control | Excess | Correctness (before → after) |
|---|---|---:|---:|---:|---:|---:|---|
| `capitalization` **(selected)** | measured | 1 | 0.0217 | 0.0921 | 0.0000 | +0.0921 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→incorrect; Gemini 3.1 Flash-Lite correct→correct |
| `word_deletion` | measured | 4 | 0.0870 | 0.0378 | 0.0000 | +0.0378 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→incorrect; Gemini 3.1 Flash-Lite correct→correct |
| `punctuation` | measured | 1 | 0.0217 | 0.0324 | 0.0000 | +0.0324 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→incorrect; Gemini 3.1 Flash-Lite correct→correct |
| `char_substitution` | measured | 1 | 0.0217 | 0.0304 | 0.0000 | +0.0304 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→incorrect; Gemini 3.1 Flash-Lite correct→correct |
| `instruction_reordering` | inapplicable: inapplicable_or_no_op |  |  |  |  |  |  |
| `synonym` | over_budget: d_in_char 0.1250 exceeds budget 0.10 | 6 | 0.1250 |  |  |  |  |
| `whitespace` | over_budget: d_in_char 0.1481 exceeds budget 0.10 | 8 | 0.1481 |  |  |  |  |
| `word_insertion` | over_budget: d_in_char 0.1786 exceeds budget 0.10 | 10 | 0.1786 |  |  |  |  |
| `word_substitution` | over_budget: d_in_char 0.1373 exceeds budget 0.10 | 7 | 0.1373 |  |  |  |  |

## 4. Input–output trade-off

Eligible edits not dominated by another edit with no more character edits and at least as much excess change:

- `capitalization`: 1 character edit(s) → excess +0.0921

## 5. Source records

Full responses, per-model scores and record IDs are in the JSON file next to this report.

- `qwen/qwen3.8-27b|MATH-006|treatment|capitalization|1`: anchor record `86aa54e5-76be-488c-a948-573396eba454`, comparison record `9da3ed3c-4215-42af-a7bb-2fbff60add5c`
- `openai/gpt-oss-120b|MATH-006|treatment|capitalization|1`: anchor record `94a7b134-3a1a-4ff3-acf2-4bcb8ae44643`, comparison record `21ff3504-cc52-45a6-8296-3c24383b3d50`
- `openai/gpt-oss-20b|MATH-006|treatment|capitalization|1`: anchor record `ca16b998-1c9c-4352-b40f-0978ee0ec746`, comparison record `74bff761-1ba8-46f9-83dc-1320105abb32`
- `allam-2-7b|MATH-006|treatment|capitalization|1`: anchor record `5b4671fc-7ec2-4788-9f04-bd0fd7dda8fd`, comparison record `95433de2-e7cd-4de6-9b0a-3da6fa6ce3c7`
- `gemini-3.1-flash-lite|MATH-006|treatment|capitalization|1`: anchor record `2e68b3f0-614c-4f88-bbe9-a8b0d92a8b1f`, comparison record `ba335ab9-5155-435d-923f-e7ecdca24f3e`
