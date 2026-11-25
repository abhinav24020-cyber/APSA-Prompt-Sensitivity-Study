# Perturbation operator result: MATH-002 · Mathematical reasoning

**Status:** `selected` · **Rule:** budget mode, d_in_char ≤ 0.10 · **Model scope:** fixed panel of 5 models, equal weights · **Evidence:** retrospective

## 1. Category recommendation

- Recommended: **char_substitution** (exploratory (main_v1 discovery ranking); source: category_operator_rankings.csv (mathematical_reasoning, budget 0.10))
- Category score 0.0853, coverage 8/8 complete prompts
- Why: A typo in prose changes how the task is rendered while leaving quantities and the requested result intact.
- A category recommendation is not a measurement of this prompt; the measured result follows.

## 2. Measured result for this prompt

capitalization produced the largest control-adjusted change (+0.1354) among 7 eligible, measured edits within budget 0.10. The next best eligible edit was synonym (+0.1008). Preservation evidence: not flagged by the retrospective audit (operator audited by a sample of 5 candidates).

| Field | Result |
|---|---|
| Prompt and category | `MATH-002` · Mathematical reasoning |
| Original prompt | Solve the following system of linear equations for x and y: 3x + 2y = 16 and 5x - y = 9. Provide the values as an ordered pair (x, y). |
| Perturbed prompt | solve the following system of linear equations for x and y: 3x + 2y = 16 and 5x - y = 9. Provide the values as an ordered pair (x, y). |
| Operator | `capitalization`: `Solve` → `solve` |
| Input change | **1 character edit(s)**, normalised distance **0.0075**, semantic input distance 0.0000 |
| Model and comparison | fixed panel of 5 models, equal weights; 5 matched model–prompt pair(s) from `main_v1` |
| Output change | Semantic distance **0.1872**, mean unchanged control distance **0.0518**, excess distance **+0.1354** |
| Functional result | Qwen 3.8 27B: correct → correct; same final answer; response length 1546 → 1598 characters; GPT-OSS-120B: correct → correct; same final answer; response length 101 → 28 characters; GPT-OSS-20B: correct → correct; final answer text changed; response length 45 → 14 characters; ALLaM-2-7B: incorrect → correct; final answer text changed; response length 828 → 623 characters; Gemini 3.1 Flash-Lite: correct → correct; same final answer; response length 389 → 357 characters |
| Tie status | unique |
| Evidence status | Measured retrospectively from stored main_v1 outputs; this prompt belongs to the discovery set that produced the category ranking, so the result is exploratory. |

### Responses of ALLaM-2-7B (largest effect in the panel)

**Original prompt response**

```text
First, let's multiply the first equation by 2 to make the coefficients of y in both equations the same:

2 * (3x + 2y) = 2 * 16
6x + 4y = 32

Now our system of equations is:
1) 3x + 2y = 16
2) 6x + 4y = 32

Next, we'll subtract equation 1 from equation 2 to eliminate y:

(6x + 4y) - (3x + 2y) = 32 - 16
3x + 2y = 16

Since both equations are now the same (3x + 2y = 16), we can solve for y:

2y = 16 - 3x
y = (16 - 3x) / 2

Now that we have an expression for y, we can substitute it back into one of the original equations to solve for x. Let's use equation 1:

3x + 2((16 - 3x) / 2) = 16
3x + 8 - 6x = 16
-3x + 8 = 16
-3x = 8
x = -8 / -3
x = 8/3

Now that we have the value of x, we can find y using the expression we found earlier:

y = (16 - 3(8/3)) / 2
y = (16 - 24) / 2
y = -8 / 2
y = -4

Final answer: (x, y) = (8/3, -4)
```

**Perturbed prompt response**

```text
To solve the system of linear equations, we can use the method of substitution or elimination. I'll use the substitution method. First, solve the second equation for y:

5x - y = 9
y = 5x - 9

Now substitute this expression for y into the first equation:

3x + 2(5x - 9) = 16

Now solve for x:

3x + 10x - 18 = 16
13x = 34
x = 34 / 13
x = 2.6153846154 (approximately)

Now that we have the value of x, we can find y using the expression we found earlier:

y = 5x - 9
y = 5(2.6153846154) - 9
y = 13.076923077 - 9
y = 4.076923077 (approximately)

So the solution to the system of linear equations is (x, y) = (2.615, 4.077).
```

## 3. All operators

| Operator | Status | Char edits | d_in_char | Raw | Control | Excess | Correctness (before → after) |
|---|---|---:|---:|---:|---:|---:|---|
| `capitalization` **(selected)** | measured | 1 | 0.0075 | 0.1872 | 0.0518 | +0.1354 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→correct; Gemini 3.1 Flash-Lite correct→correct |
| `synonym` | measured | 7 | 0.0522 | 0.1526 | 0.0518 | +0.1008 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→incorrect; Gemini 3.1 Flash-Lite correct→correct |
| `word_insertion` | measured | 10 | 0.0694 | 0.1279 | 0.0518 | +0.0761 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→incorrect; Gemini 3.1 Flash-Lite correct→correct |
| `word_deletion` | measured | 4 | 0.0299 | 0.1073 | 0.0518 | +0.0555 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→incorrect; Gemini 3.1 Flash-Lite correct→correct |
| `char_substitution` | measured | 1 | 0.0075 | 0.0480 | 0.0518 | -0.0038 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→incorrect; Gemini 3.1 Flash-Lite correct→correct |
| `punctuation` | measured | 1 | 0.0075 | 0.0312 | 0.0518 | -0.0206 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→incorrect; Gemini 3.1 Flash-Lite correct→correct |
| `word_substitution` | measured | 5 | 0.0373 | 0.0292 | 0.0518 | -0.0226 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→incorrect; Gemini 3.1 Flash-Lite correct→correct |
| `instruction_reordering` | over_budget: d_in_char 0.6866 exceeds budget 0.10 | 92 | 0.6866 |  |  |  |  |
| `whitespace` | over_budget: d_in_char 0.1829 exceeds budget 0.10 | 30 | 0.1829 |  |  |  |  |

## 4. Input–output trade-off

Eligible edits not dominated by another edit with no more character edits and at least as much excess change:

- `capitalization`: 1 character edit(s) → excess +0.1354

## 5. Source records

Full responses, per-model scores and record IDs are in the JSON file next to this report.

- `qwen/qwen3.8-27b|MATH-002|treatment|capitalization|1`: anchor record `d365f273-38bb-4823-9c8a-085d74659c77`, comparison record `88a09401-3e9c-4cb6-b3ae-a319af89f1eb`
- `openai/gpt-oss-120b|MATH-002|treatment|capitalization|1`: anchor record `eb141ed4-c0c5-4f4c-b676-1cb93bed704c`, comparison record `a79794b3-29f1-44b8-a452-dd00e058ac10`
- `openai/gpt-oss-20b|MATH-002|treatment|capitalization|1`: anchor record `57dd0daa-fbbd-4720-bb05-b8d73ee1e0de`, comparison record `55ddb8cc-55db-42f9-9d02-c7355a529e8e`
- `allam-2-7b|MATH-002|treatment|capitalization|1`: anchor record `55a7240f-1622-431c-866b-419799b8964a`, comparison record `86bfb432-ec16-4afb-8a0e-049139581d9e`
- `gemini-3.1-flash-lite|MATH-002|treatment|capitalization|1`: anchor record `a2e6889e-086a-428f-bb00-fae576bce0ff`, comparison record `8366b7b5-6b24-43f1-93a2-d93428eeaeaf`
