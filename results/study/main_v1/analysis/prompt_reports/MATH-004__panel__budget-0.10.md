# Perturbation operator result: MATH-004 · Mathematical reasoning

**Status:** `selected` · **Rule:** budget mode, d_in_char ≤ 0.10 · **Model scope:** fixed panel of 5 models, equal weights · **Evidence:** retrospective

## 1. Category recommendation

- Recommended: **char_substitution** (exploratory (main_v1 discovery ranking); source: category_operator_rankings.csv (mathematical_reasoning, budget 0.10))
- Category score 0.0853, coverage 8/8 complete prompts
- Why: A typo in prose changes how the task is rendered while leaving quantities and the requested result intact.
- A category recommendation is not a measurement of this prompt; the measured result follows.

## 2. Measured result for this prompt

char_substitution produced the largest control-adjusted change (+0.1223) among 6 eligible, measured edits within budget 0.10. The next best eligible edit was punctuation (+0.1120). Preservation evidence: not flagged by the retrospective audit (every candidate of this operator was audited).

| Field | Result |
|---|---|
| Prompt and category | `MATH-004` · Mathematical reasoning |
| Original prompt | A committee of 3 members is to be randomly chosen from a group of 5 men and 4 women. What is the probability that the committee consists of exactly 2 men and 1 woman? Express your answer as a simplified fraction. |
| Perturbed prompt | A committee of 3 members is to be randomly chosen from a group of 5 men and 4 women. What is the probability that the committee consists of exactly 2 men and 1 woman? 3xpress your answer as a simplified fraction. |
| Operator | `char_substitution`: `Express` → `3xpress` |
| Input change | **1 character edit(s)**, normalised distance **0.0047**, semantic input distance 0.0073 |
| Model and comparison | fixed panel of 5 models, equal weights; 5 matched model–prompt pair(s) from `main_v1` |
| Output change | Semantic distance **0.1294**, mean unchanged control distance **0.0071**, excess distance **+0.1223** |
| Functional result | Qwen 3.8 27B: correct → correct; same final answer; response length 1558 → 1538 characters; GPT-OSS-120B: correct → correct; final answer text changed; response length 391 → 405 characters; GPT-OSS-20B: correct → correct; response length 5 → 19 characters; ALLaM-2-7B: incorrect → incorrect; final answer text changed; response length 901 → 725 characters; Gemini 3.1 Flash-Lite: correct → correct; same final answer; response length 775 → 755 characters |
| Tie status | unique |
| Evidence status | Measured retrospectively from stored main_v1 outputs; this prompt belongs to the discovery set that produced the category ranking, so the result is exploratory. |

### Responses of GPT-OSS-20B (largest effect in the panel)

**Original prompt response**

```text
10/21
```

**Perturbed prompt response**

```text
\[
\frac{10}{21}
\]
```

## 3. All operators

| Operator | Status | Char edits | d_in_char | Raw | Control | Excess | Correctness (before → after) |
|---|---|---:|---:|---:|---:|---:|---|
| `char_substitution` **(selected)** | measured | 1 | 0.0047 | 0.1294 | 0.0071 | +0.1223 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→incorrect; Gemini 3.1 Flash-Lite correct→correct |
| `punctuation` | measured | 1 | 0.0047 | 0.1191 | 0.0071 | +0.1120 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→incorrect; Gemini 3.1 Flash-Lite correct→correct |
| `word_insertion` | measured | 10 | 0.0450 | 0.1040 | 0.0071 | +0.0969 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→incorrect; Gemini 3.1 Flash-Lite correct→correct |
| `synonym` | measured | 7 | 0.0327 | 0.0451 | 0.0071 | +0.0380 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→incorrect; Gemini 3.1 Flash-Lite correct→correct |
| `capitalization` | measured | 1 | 0.0047 | 0.0094 | 0.0071 | +0.0023 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→incorrect; Gemini 3.1 Flash-Lite correct→correct |
| `word_deletion` | measured | 4 | 0.0189 | 0.0058 | 0.0071 | -0.0012 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→incorrect; Gemini 3.1 Flash-Lite correct→correct |
| `instruction_reordering` | over_budget: d_in_char 0.4340 exceeds budget 0.10 | 92 | 0.4340 |  |  |  |  |
| `whitespace` | over_budget: d_in_char 0.1587 exceeds budget 0.10 | 40 | 0.1587 |  |  |  |  |
| `word_substitution` | inapplicable: inapplicable_or_no_op |  |  |  |  |  |  |

## 4. Input–output trade-off

Eligible edits not dominated by another edit with no more character edits and at least as much excess change:

- `char_substitution`: 1 character edit(s) → excess +0.1223

## 5. Source records

Full responses, per-model scores and record IDs are in the JSON file next to this report.

- `qwen/qwen3.8-27b|MATH-004|treatment|char_substitution|1`: anchor record `d4b55dd3-9b78-44b7-93a7-8fd11211debd`, comparison record `88424ad6-b651-4151-b8b2-9dab9d2e7d5b`
- `openai/gpt-oss-120b|MATH-004|treatment|char_substitution|1`: anchor record `2fba0059-f5dd-4e5d-a9e1-85892d4eb66f`, comparison record `8f674a4e-9991-4f1b-9647-772e222b9e94`
- `openai/gpt-oss-20b|MATH-004|treatment|char_substitution|1`: anchor record `89ab775d-061b-44fc-8de2-4f6c2110205a`, comparison record `39be6774-e69b-46b7-b60b-4cd662a1ced3`
- `allam-2-7b|MATH-004|treatment|char_substitution|1`: anchor record `6a8ef7af-5c21-49a0-af6e-3f00d455c71a`, comparison record `c1386524-8a4f-451f-8b8e-f14956a578c7`
- `gemini-3.1-flash-lite|MATH-004|treatment|char_substitution|1`: anchor record `b7728429-d20b-4171-9731-df60c1febdae`, comparison record `5cb98034-4581-45b2-8d18-994be5454992`
