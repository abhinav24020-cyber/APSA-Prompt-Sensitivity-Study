# Perturbation operator result: LOGIC-005 · Logical reasoning

**Status:** `selected` · **Rule:** budget mode, d_in_char ≤ 0.10 · **Model scope:** fixed panel of 5 models, equal weights · **Evidence:** retrospective

## 1. Category recommendation

- Recommended: **punctuation** (exploratory (main_v1 discovery ranking); source: category_operator_rankings.csv (logical_reasoning, budget 0.10))
- Category score 0.0744, coverage 9/9 complete prompts
- Why: A terminal punctuation edit changes the cue at the end of the prompt while leaving premises and the requested conclusion intact.
- A category recommendation is not a measurement of this prompt; the measured result follows.

## 2. Measured result for this prompt

punctuation produced the largest control-adjusted change (+0.0392) among 6 eligible, measured edits within budget 0.10. The next best eligible edit was word_deletion (+0.0380). Preservation evidence: not flagged by the retrospective audit (operator audited by a sample of 5 candidates).

| Field | Result |
|---|---|
| Prompt and category | `LOGIC-005` · Logical reasoning |
| Original prompt | An applicant qualifies for a loan if they earn over $50,000 OR (they earn over $35,000 AND have a credit score above 700). John earns $40,000 and has a credit score of 720. Does John qualify? Answer Yes or No and state the rule satisfied. |
| Perturbed prompt | An applicant qualifies for a loan if they earn over $50,000 OR (they earn over $35,000 AND have a credit score above 700). John earns $40,000 and has a credit score of 720. Does John qualify? Answer Yes or No and state the rule satisfied |
| Operator | `punctuation`: `satisfied.` → `satisfied` |
| Input change | **1 character edit(s)**, normalised distance **0.0042**, semantic input distance 0.0133 |
| Model and comparison | fixed panel of 5 models, equal weights; 5 matched model–prompt pair(s) from `main_v1` |
| Output change | Semantic distance **0.0392**, mean unchanged control distance **0.0000**, excess distance **+0.0392** |
| Functional result | Qwen 3.8 27B: correct → correct; final answer text changed; response length 901 → 807 characters; GPT-OSS-120B: correct → correct; same final answer; response length 101 → 101 characters; GPT-OSS-20B: correct → correct; response length 98 → 98 characters; ALLaM-2-7B: correct → correct; response length 301 → 310 characters; Gemini 3.1 Flash-Lite: correct → correct; same final answer; response length 148 → 265 characters |
| Tie status | unique |
| Evidence status | Measured retrospectively from stored main_v1 outputs; this prompt belongs to the discovery set that produced the category ranking, so the result is exploratory. |

### Responses of Gemini 3.1 Flash-Lite (largest effect in the panel)

**Original prompt response**

```text
John qualifies because he satisfies the second condition: he earns over $35,000 ($40,000) and has a credit score above 700 (720).

Final answer: Yes
```

**Perturbed prompt response**

```text
John earns $40,000, which is not over $50,000. However, he earns over $35,000 and has a credit score of 720 (which is above 700), satisfying the second condition.

Yes, he satisfies the rule: (earns over $35,000 AND has a credit score above 700).

Final answer: Yes
```

## 3. All operators

| Operator | Status | Char edits | d_in_char | Raw | Control | Excess | Correctness (before → after) |
|---|---|---:|---:|---:|---:|---:|---|
| `punctuation` **(selected)** | measured | 1 | 0.0042 | 0.0392 | 0.0000 | +0.0392 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `word_deletion` | measured | 4 | 0.0168 | 0.0380 | 0.0000 | +0.0380 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `word_insertion` | measured | 10 | 0.0403 | 0.0269 | 0.0000 | +0.0269 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `char_substitution` | measured | 1 | 0.0042 | 0.0134 | 0.0000 | +0.0134 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `capitalization` | measured | 1 | 0.0042 | 0.0100 | 0.0000 | +0.0100 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `synonym` | measured | 7 | 0.0292 | 0.0041 | 0.0000 | +0.0041 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `instruction_reordering` | over_budget: d_in_char 0.3950 exceeds budget 0.10 | 94 | 0.3950 |  |  |  |  |
| `whitespace` | over_budget: d_in_char 0.1560 exceeds budget 0.10 | 44 | 0.1560 |  |  |  |  |
| `word_substitution` | inapplicable: inapplicable_or_no_op |  |  |  |  |  |  |

## 4. Input–output trade-off

Eligible edits not dominated by another edit with no more character edits and at least as much excess change:

- `punctuation`: 1 character edit(s) → excess +0.0392

## 5. Source records

Full responses, per-model scores and record IDs are in the JSON file next to this report.

- `qwen/qwen3.8-27b|LOGIC-005|treatment|punctuation|1`: anchor record `2f3063e2-576e-4ca9-bff8-e6ddcb7d6e66`, comparison record `971ad1d4-6393-421a-9b0e-cc9c66bf29bb`
- `openai/gpt-oss-120b|LOGIC-005|treatment|punctuation|1`: anchor record `2a47aa14-b447-458c-b55d-da7f3e639bc1`, comparison record `3c322223-0e8d-48a0-9102-238eaa4dc67e`
- `openai/gpt-oss-20b|LOGIC-005|treatment|punctuation|1`: anchor record `bdea137c-9c59-4727-b402-96c01a559178`, comparison record `d52ce1ca-cc4f-468b-8244-1f0895fa3509`
- `allam-2-7b|LOGIC-005|treatment|punctuation|1`: anchor record `ff95de9e-0807-47f6-ab82-365b9783b16b`, comparison record `5a3ab9a5-be0d-4163-b69b-8e6092546083`
- `gemini-3.1-flash-lite|LOGIC-005|treatment|punctuation|1`: anchor record `e529ff1b-bafa-4902-a553-d5648c8a2329`, comparison record `bd690bbd-c127-4ceb-ae2b-f226cca2a798`
