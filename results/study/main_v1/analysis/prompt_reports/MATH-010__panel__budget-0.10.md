# Perturbation operator result: MATH-010 · Mathematical reasoning

**Status:** `selected` · **Rule:** budget mode, d_in_char ≤ 0.10 · **Model scope:** fixed panel of 5 models, equal weights · **Evidence:** retrospective

## 1. Category recommendation

- Recommended: **char_substitution** (exploratory (main_v1 discovery ranking); source: category_operator_rankings.csv (mathematical_reasoning, budget 0.10))
- Category score 0.0853, coverage 8/8 complete prompts
- Why: A typo in prose changes how the task is rendered while leaving quantities and the requested result intact.
- A category recommendation is not a measurement of this prompt; the measured result follows.

## 2. Measured result for this prompt

synonym produced the largest control-adjusted change (+0.2839) among 6 eligible, measured edits within budget 0.10. The next best eligible edit was capitalization (+0.1755). Exact tie retained: synonym, word_substitution are indistinguishable on score, character edits and input distance. Preservation evidence: not flagged by the retrospective audit (every candidate of this operator was audited).

| Field | Result |
|---|---|
| Prompt and category | `MATH-010` · Mathematical reasoning |
| Original prompt | Compute the determinant of the 3x3 matrix: [[2, 0, 1], [3, 4, -2], [1, 5, 0]]. |
| Perturbed prompt | Calculate the determinant of the 3x3 matrix: [[2, 0, 1], [3, 4, -2], [1, 5, 0]]. |
| Operator | `synonym`: `Compute` → `Calculate` |
| Input change | **5 character edit(s)**, normalised distance **0.0625**, semantic input distance 0.0077 |
| Model and comparison | fixed panel of 5 models, equal weights; 5 matched model–prompt pair(s) from `main_v1` |
| Output change | Semantic distance **0.2839**, mean unchanged control distance **0.0000**, excess distance **+0.2839** |
| Functional result | Qwen 3.8 27B: correct → correct; same final answer; response length 1144 → 1215 characters; GPT-OSS-120B: correct → correct; same final answer; response length 16 → 315 characters; GPT-OSS-20B: correct → correct; final answer text changed; response length 2 → 41 characters; ALLaM-2-7B: incorrect → incorrect; final answer text changed; response length 431 → 328 characters; Gemini 3.1 Flash-Lite: correct → correct; same final answer; response length 653 → 642 characters |
| Tie status | unresolved_tie |
| Evidence status | Measured retrospectively from stored main_v1 outputs; this prompt belongs to the discovery set that produced the category ranking, so the result is exploratory. |

### Responses of GPT-OSS-120B (largest effect in the panel)

**Original prompt response**

```text
Final answer: 31
```

**Perturbed prompt response**

```text
The determinant is  

\[
\begin{vmatrix}
2 & 0 & 1\\
3 & 4 & -2\\
1 & 5 & 0
\end{vmatrix}
= 2\begin{vmatrix}4 & -2\\5 & 0\end{vmatrix}
-0\begin{vmatrix}3 & -2\\1 & 0\end{vmatrix}
+1\begin{vmatrix}3 & 4\\1 & 5\end{vmatrix}
= 2(4\cdot0-(-2)\cdot5)+1(3\cdot5-4\cdot1)
= 2(10)+ (15-4)
= 20+11 = 31.
\]

Final answer: 31
```

## 3. All operators

| Operator | Status | Char edits | d_in_char | Raw | Control | Excess | Correctness (before → after) |
|---|---|---:|---:|---:|---:|---:|---|
| `synonym` **(selected)** | measured | 5 | 0.0625 | 0.2839 | 0.0000 | +0.2839 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→incorrect; Gemini 3.1 Flash-Lite correct→correct |
| `word_substitution` **(selected)** | measured | 5 | 0.0625 | 0.2839 | 0.0000 | +0.2839 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→incorrect; Gemini 3.1 Flash-Lite correct→correct |
| `capitalization` | measured | 1 | 0.0128 | 0.1755 | 0.0000 | +0.1755 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→incorrect; Gemini 3.1 Flash-Lite correct→correct |
| `word_deletion` | measured | 4 | 0.0513 | 0.1519 | 0.0000 | +0.1519 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→incorrect; Gemini 3.1 Flash-Lite correct→correct |
| `char_substitution` | measured | 1 | 0.0128 | 0.1225 | 0.0000 | +0.1225 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→incorrect; Gemini 3.1 Flash-Lite correct→correct |
| `punctuation` | measured | 1 | 0.0128 | 0.0891 | 0.0000 | +0.0891 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→incorrect; Gemini 3.1 Flash-Lite correct→correct |
| `instruction_reordering` | inapplicable: inapplicable_or_no_op |  |  |  |  |  |  |
| `whitespace` | over_budget: d_in_char 0.1613 exceeds budget 0.10 | 15 | 0.1613 |  |  |  |  |
| `word_insertion` | over_budget: d_in_char 0.1136 exceeds budget 0.10 | 10 | 0.1136 |  |  |  |  |

## 4. Input–output trade-off

Eligible edits not dominated by another edit with no more character edits and at least as much excess change:

- `capitalization`: 1 character edit(s) → excess +0.1755
- `synonym`: 5 character edit(s) → excess +0.2839
- `word_substitution`: 5 character edit(s) → excess +0.2839

## 5. Source records

Full responses, per-model scores and record IDs are in the JSON file next to this report.

- `qwen/qwen3.8-27b|MATH-010|treatment|synonym|1`: anchor record `ae3d0814-3588-4e00-afd0-5276c8ee1c32`, comparison record `3b7868ba-e4d5-4cde-a276-16a0a0151b7d`
- `openai/gpt-oss-120b|MATH-010|treatment|synonym|1`: anchor record `aad22ac2-1e6a-44d4-a82f-4d0917592603`, comparison record `456be029-996d-4650-a40e-8c5183c201e8`
- `openai/gpt-oss-20b|MATH-010|treatment|synonym|1`: anchor record `708fb0e6-f6a1-4c90-8a11-080f73955b1d`, comparison record `603bc153-3cb0-4e31-8975-60e692b44ad1`
- `allam-2-7b|MATH-010|treatment|synonym|1`: anchor record `2bc9da4e-549f-4595-ace2-8c0889d861b8`, comparison record `a4934c17-a333-4b3e-a671-3ab6acfe0cc9`
- `gemini-3.1-flash-lite|MATH-010|treatment|synonym|1`: anchor record `a197e1e0-4748-43a3-89cf-f4d06c13c6e4`, comparison record `7ecf7b56-76f6-4b2c-84f3-48c6393c61f3`
- `qwen/qwen3.8-27b|MATH-010|treatment|word_substitution|1`: anchor record `ae3d0814-3588-4e00-afd0-5276c8ee1c32`, comparison record `e9efa176-acce-4aa3-8110-0065d3ebc780`
- `openai/gpt-oss-120b|MATH-010|treatment|word_substitution|1`: anchor record `aad22ac2-1e6a-44d4-a82f-4d0917592603`, comparison record `6cc39a42-405c-45a9-a9eb-2cad94783a07`
- `openai/gpt-oss-20b|MATH-010|treatment|word_substitution|1`: anchor record `708fb0e6-f6a1-4c90-8a11-080f73955b1d`, comparison record `a1305402-94e8-4054-95f6-8cd3d0ffc479`
- `allam-2-7b|MATH-010|treatment|word_substitution|1`: anchor record `2bc9da4e-549f-4595-ace2-8c0889d861b8`, comparison record `930ac3c5-a18a-46ac-b5ed-3488c2a6c5bd`
- `gemini-3.1-flash-lite|MATH-010|treatment|word_substitution|1`: anchor record `a197e1e0-4748-43a3-89cf-f4d06c13c6e4`, comparison record `3eb15c8e-5ac6-4a04-87c0-ccf361f62503`
