# Perturbation operator result: MATH-005 · Mathematical reasoning

**Status:** `incomplete` · **Rule:** budget mode, d_in_char ≤ 0.10 · **Model scope:** fixed panel of 5 models, equal weights · **Evidence:** retrospective

## 1. Category recommendation

- Recommended: **char_substitution** (exploratory (main_v1 discovery ranking); source: category_operator_rankings.csv (mathematical_reasoning, budget 0.10))
- Category score 0.0853, coverage 8/8 complete prompts
- Why: A typo in prose changes how the task is rendered while leaving quantities and the requested result intact.
- A category recommendation is not a measurement of this prompt; the measured result follows.

## 2. Measured result for this prompt

3 eligible operator(s) lack complete matched measurements (char_substitution, punctuation, word_deletion), so no maximum is claimed. Among the 2 fully measured edits the largest excess is +0.0432 (capitalization), which is provisional.

## 3. All operators

| Operator | Status | Char edits | d_in_char | Raw | Control | Excess | Correctness (before → after) |
|---|---|---:|---:|---:|---:|---:|---|
| `capitalization` | measured | 1 | 0.0055 | 0.0432 | 0.0000 | +0.0432 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→incorrect; Gemini 3.1 Flash-Lite correct→correct |
| `word_insertion` | measured | 10 | 0.0524 | 0.0033 | 0.0000 | +0.0033 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→incorrect; Gemini 3.1 Flash-Lite correct→correct |
| `char_substitution` | incomplete (GPT-OSS-20B: treatment_missing) | 1 | 0.0055 |  |  |  | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; ALLaM-2-7B incorrect→incorrect; Gemini 3.1 Flash-Lite correct→correct |
| `instruction_reordering` | over_budget: d_in_char 0.3204 exceeds budget 0.10 | 58 | 0.3204 |  |  |  |  |
| `punctuation` | incomplete (GPT-OSS-20B: treatment_missing) | 1 | 0.0055 |  |  |  | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; ALLaM-2-7B incorrect→incorrect; Gemini 3.1 Flash-Lite correct→correct |
| `synonym` | inapplicable: inapplicable_or_no_op |  |  |  |  |  |  |
| `whitespace` | over_budget: d_in_char 0.1422 exceeds budget 0.10 | 30 | 0.1422 |  |  |  |  |
| `word_deletion` | incomplete (GPT-OSS-20B: treatment_missing) | 4 | 0.0221 |  |  |  | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; ALLaM-2-7B incorrect→incorrect; Gemini 3.1 Flash-Lite correct→correct |
| `word_substitution` | inapplicable: inapplicable_or_no_op |  |  |  |  |  |  |

## 4. Input–output trade-off

Eligible edits not dominated by another edit with no more character edits and at least as much excess change:

- `capitalization`: 1 character edit(s) → excess +0.0432

## 5. Source records

Full responses, per-model scores and record IDs are in the JSON file next to this report.

