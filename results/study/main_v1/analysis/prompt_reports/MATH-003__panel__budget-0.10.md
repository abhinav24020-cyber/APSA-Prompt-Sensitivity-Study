# Perturbation operator result: MATH-003 · Mathematical reasoning

**Status:** `selected` · **Rule:** budget mode, d_in_char ≤ 0.10 · **Model scope:** fixed panel of 5 models, equal weights · **Evidence:** retrospective

## 1. Category recommendation

- Recommended: **char_substitution** (exploratory (main_v1 discovery ranking); source: category_operator_rankings.csv (mathematical_reasoning, budget 0.10))
- Category score 0.0853, coverage 8/8 complete prompts
- Why: A typo in prose changes how the task is rendered while leaving quantities and the requested result intact.
- A category recommendation is not a measurement of this prompt; the measured result follows.

## 2. Measured result for this prompt

punctuation produced the largest control-adjusted change (+0.1003) among 7 eligible, measured edits within budget 0.10. The next best eligible edit was char_substitution (+0.0964). Preservation evidence: not flagged by the retrospective audit (operator audited by a sample of 5 candidates).

| Field | Result |
|---|---|
| Prompt and category | `MATH-003` · Mathematical reasoning |
| Original prompt | Calculate the volume of a right circular cylinder with radius r = 4 cm and height h = 10 cm. Express the exact answer in terms of pi. |
| Perturbed prompt | Calculate the volume of a right circular cylinder with radius r = 4 cm and height h = 10 cm. Express the exact answer in terms of pi |
| Operator | `punctuation`: `pi.` → `pi` |
| Input change | **1 character edit(s)**, normalised distance **0.0075**, semantic input distance 0.0032 |
| Model and comparison | fixed panel of 5 models, equal weights; 5 matched model–prompt pair(s) from `main_v1` |
| Output change | Semantic distance **0.1014**, mean unchanged control distance **0.0010**, excess distance **+0.1003** |
| Functional result | Qwen 3.8 27B: correct → correct; same final answer; response length 698 → 604 characters; GPT-OSS-120B: correct → correct; same final answer; response length 261 → 332 characters; GPT-OSS-20B: correct → correct; same final answer; response length 24 → 24 characters; ALLaM-2-7B: correct → correct; final answer text changed; response length 55 → 342 characters; Gemini 3.1 Flash-Lite: correct → correct; final answer text changed; response length 246 → 214 characters |
| Tie status | unique |
| Evidence status | Measured retrospectively from stored main_v1 outputs; this prompt belongs to the discovery set that produced the category ranking, so the result is exploratory. |

### Responses of ALLaM-2-7B (largest effect in the panel)

**Original prompt response**

```text
Final answer: π * (4^2) * 10 = 160π cubic centimeters.
```

**Perturbed prompt response**

```text
To calculate the volume of a right circular cylinder, use the formula:

Volume = π * r^2 * h

In this case, the radius (r) is 4 cm and the height (h) is 10 cm. Plug the values into the formula:

Volume = π * (4 cm)^2 * 10 cm
Volume = π * 16 cm^2 * 10 cm
Volume = 160π cm^3

Final answer: The volume of the cylinder is 160π cubic centimeters.
```

## 3. All operators

| Operator | Status | Char edits | d_in_char | Raw | Control | Excess | Correctness (before → after) |
|---|---|---:|---:|---:|---:|---:|---|
| `punctuation` **(selected)** | measured | 1 | 0.0075 | 0.1014 | 0.0010 | +0.1003 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `char_substitution` | measured | 1 | 0.0075 | 0.0975 | 0.0010 | +0.0964 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `word_insertion` | measured | 10 | 0.0699 | 0.0967 | 0.0010 | +0.0957 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `synonym` | measured | 7 | 0.0519 | 0.0561 | 0.0010 | +0.0551 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→incorrect; Gemini 3.1 Flash-Lite correct→correct |
| `word_substitution` | measured | 5 | 0.0376 | 0.0135 | 0.0010 | +0.0125 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `word_deletion` | measured | 4 | 0.0301 | 0.0126 | 0.0010 | +0.0116 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `capitalization` | measured | 1 | 0.0075 | 0.0080 | 0.0010 | +0.0070 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `instruction_reordering` | over_budget: d_in_char 0.6165 exceeds budget 0.10 | 82 | 0.6165 |  |  |  |  |
| `whitespace` | over_budget: d_in_char 0.1688 exceeds budget 0.10 | 27 | 0.1688 |  |  |  |  |

## 4. Input–output trade-off

Eligible edits not dominated by another edit with no more character edits and at least as much excess change:

- `punctuation`: 1 character edit(s) → excess +0.1003

## 5. Source records

Full responses, per-model scores and record IDs are in the JSON file next to this report.

- `qwen/qwen3.8-27b|MATH-003|treatment|punctuation|1`: anchor record `f7e6cb30-d7dc-4d6b-8fcd-15ebe58cad1d`, comparison record `2b2672db-d1f9-428b-ac80-fc32cf29c4c2`
- `openai/gpt-oss-120b|MATH-003|treatment|punctuation|1`: anchor record `96ce98f5-e877-4304-8c3d-dd98347c6cb1`, comparison record `e52297f6-22d2-47cc-b129-ff705721655b`
- `openai/gpt-oss-20b|MATH-003|treatment|punctuation|1`: anchor record `f40f1b56-6407-4f75-9078-aa7366d0ee60`, comparison record `aea4809c-bec9-47cc-af86-d1c62f496bf8`
- `allam-2-7b|MATH-003|treatment|punctuation|1`: anchor record `4e3424c7-439c-4502-9a86-b4e9057aead2`, comparison record `3129ca77-d633-46dd-9fe3-23bfcb3016af`
- `gemini-3.1-flash-lite|MATH-003|treatment|punctuation|1`: anchor record `4f0e4843-90ab-4765-ab1c-1d2f1e353990`, comparison record `c8f3d87d-9643-4540-b5a2-f4e618d04b75`
