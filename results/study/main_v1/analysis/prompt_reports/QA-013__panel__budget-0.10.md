# Perturbation operator result: QA-013 · Question answering

**Status:** `selected` · **Rule:** budget mode, d_in_char ≤ 0.10 · **Model scope:** fixed panel of 5 models, equal weights · **Evidence:** retrospective

## 1. Category recommendation

- Recommended: **punctuation** (exploratory (main_v1 discovery ranking); source: category_operator_rankings.csv (question_answering, budget 0.10))
- Category score 0.0426, coverage 10/10 complete prompts
- Why: Editing the question's final delimiter can change the form or length of the answer while keeping the requested fact fixed.
- A category recommendation is not a measurement of this prompt; the measured result follows.

## 2. Measured result for this prompt

punctuation produced the largest control-adjusted change (+0.1352) among 5 eligible, measured edits within budget 0.10. The next best eligible edit was word_insertion (+0.1346). Preservation evidence: not flagged by the retrospective audit (operator audited by a sample of 5 candidates).

| Field | Result |
|---|---|
| Prompt and category | `QA-013` · Question answering |
| Original prompt | In US constitutional law, which landmark 1803 Supreme Court case established the principle of judicial review? |
| Perturbed prompt | In US constitutional law, which landmark 1803 Supreme Court case established the principle of judicial review |
| Operator | `punctuation`: `review?` → `review` |
| Input change | **1 character edit(s)**, normalised distance **0.0091**, semantic input distance 0.0250 |
| Model and comparison | fixed panel of 5 models, equal weights; 5 matched model–prompt pair(s) from `main_v1` |
| Output change | Semantic distance **0.1352**, mean unchanged control distance **0.0000**, excess distance **+0.1352** |
| Functional result | Qwen 3.8 27B: correct → correct; same final answer; response length 410 → 398 characters; GPT-OSS-120B: correct → correct; same final answer; response length 53 → 148 characters; GPT-OSS-20B: correct → correct; final answer text changed; response length 106 → 25 characters; ALLaM-2-7B: correct → correct; same final answer; response length 170 → 169 characters; Gemini 3.1 Flash-Lite: correct → correct; same final answer; response length 145 → 145 characters |
| Tie status | unique |
| Evidence status | Measured retrospectively from stored main_v1 outputs; this prompt belongs to the discovery set that produced the category ranking, so the result is exploratory. |

### Responses of GPT-OSS-120B (largest effect in the panel)

**Original prompt response**

```text
Marbury v. Madison  
Final answer: Marbury v. Madison
```

**Perturbed prompt response**

```text
The landmark 1803 Supreme Court case that established the principle of judicial review is **Marbury v. Madison**.  
Final answer: Marbury v. Madison
```

## 3. All operators

| Operator | Status | Char edits | d_in_char | Raw | Control | Excess | Correctness (before → after) |
|---|---|---:|---:|---:|---:|---:|---|
| `punctuation` **(selected)** | measured | 1 | 0.0091 | 0.1352 | 0.0000 | +0.1352 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `word_insertion` | measured | 10 | 0.0833 | 0.1346 | 0.0000 | +0.1346 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `capitalization` | measured | 1 | 0.0091 | 0.1278 | 0.0000 | +0.1278 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `char_substitution` | measured | 1 | 0.0091 | 0.0505 | 0.0000 | +0.0505 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `word_deletion` | measured | 4 | 0.0364 | 0.0000 | 0.0000 | +0.0000 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `instruction_reordering` | inapplicable: inapplicable_or_no_op |  |  |  |  |  |  |
| `synonym` | inapplicable: inapplicable_or_no_op |  |  |  |  |  |  |
| `whitespace` | over_budget: d_in_char 0.1200 exceeds budget 0.10 | 15 | 0.1200 |  |  |  |  |
| `word_substitution` | inapplicable: inapplicable_or_no_op |  |  |  |  |  |  |

## 4. Input–output trade-off

Eligible edits not dominated by another edit with no more character edits and at least as much excess change:

- `punctuation`: 1 character edit(s) → excess +0.1352

## 5. Source records

Full responses, per-model scores and record IDs are in the JSON file next to this report.

- `qwen/qwen3.8-27b|QA-013|treatment|punctuation|1`: anchor record `e3e6f622-ed61-4825-bdab-7e06bfbcf89b`, comparison record `642eeac0-7368-4322-90a8-2e573fc8636a`
- `openai/gpt-oss-120b|QA-013|treatment|punctuation|1`: anchor record `2f0e9eb7-57b1-4d75-98db-96504a8381ad`, comparison record `b92b2d2b-4b97-4864-870a-ab5ffa05fa7f`
- `openai/gpt-oss-20b|QA-013|treatment|punctuation|1`: anchor record `0bfc907d-73a1-4a14-91a3-bd2da440f935`, comparison record `c64cf858-375b-4cdc-b75f-8f7817d56dc2`
- `allam-2-7b|QA-013|treatment|punctuation|1`: anchor record `8644e8c6-6a8b-4f79-9bee-129434ec48e9`, comparison record `7280e9a9-83d2-4373-a4ba-012cebe3cd67`
- `gemini-3.1-flash-lite|QA-013|treatment|punctuation|1`: anchor record `6a974e3b-860b-4424-b2e8-8f24909424f2`, comparison record `63521124-b4e3-434c-98e8-07ddba338822`
