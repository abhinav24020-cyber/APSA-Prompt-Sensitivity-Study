# Perturbation operator result: QA-002 · Question answering

**Status:** `selected` · **Rule:** budget mode, d_in_char ≤ 0.10 · **Model scope:** fixed panel of 5 models, equal weights · **Evidence:** retrospective

## 1. Category recommendation

- Recommended: **punctuation** (exploratory (main_v1 discovery ranking); source: category_operator_rankings.csv (question_answering, budget 0.10))
- Category score 0.0426, coverage 10/10 complete prompts
- Why: Editing the question's final delimiter can change the form or length of the answer while keeping the requested fact fixed.
- A category recommendation is not a measurement of this prompt; the measured result follows.

## 2. Measured result for this prompt

capitalization produced the largest control-adjusted change (+0.0596) among 5 eligible, measured edits within budget 0.10. The next best eligible edit was word_insertion (+0.0134). Preservation evidence: not flagged by the retrospective audit (operator audited by a sample of 5 candidates).

| Field | Result |
|---|---|
| Prompt and category | `QA-002` · Question answering |
| Original prompt | Passage: 'The James Webb Space Telescope (JWST) was launched on December 25, 2021. It operates primarily in the infrared spectrum and is located near the Sun-Earth L2 Lagrange point.' Question: On what date was JWST launched and at what Lagrange point is it stationed? |
| Perturbed prompt | passage: 'The James Webb Space Telescope (JWST) was launched on December 25, 2021. It operates primarily in the infrared spectrum and is located near the Sun-Earth L2 Lagrange point.' Question: On what date was JWST launched and at what Lagrange point is it stationed? |
| Operator | `capitalization`: `Passage:` → `passage:` |
| Input change | **1 character edit(s)**, normalised distance **0.0037**, semantic input distance 0.0000 |
| Model and comparison | fixed panel of 5 models, equal weights; 5 matched model–prompt pair(s) from `main_v1` |
| Output change | Semantic distance **0.0596**, mean unchanged control distance **0.0000**, excess distance **+0.0596** |
| Functional result | Qwen 3.8 27B: correct → correct; same final answer; response length 231 → 192 characters; GPT-OSS-120B: correct → correct; same final answer; response length 144 → 170 characters; GPT-OSS-20B: correct → correct; same final answer; response length 96 → 96 characters; ALLaM-2-7B: correct → correct; response length 88 → 88 characters; Gemini 3.1 Flash-Lite: correct → correct; same final answer; response length 180 → 180 characters |
| Tie status | unique |
| Evidence status | Measured retrospectively from stored main_v1 outputs; this prompt belongs to the discovery set that produced the category ranking, so the result is exploratory. |

### Responses of GPT-OSS-120B (largest effect in the panel)

**Original prompt response**

```text
JWST was launched on December 25, 2021, and it is stationed at the Sun‑Earth L2 Lagrange point.  
Final answer: December 25, 2021; Sun‑Earth L2.
```

**Perturbed prompt response**

```text
The James Webb Space Telescope was launched on December 25, 2021, and it is stationed at the Sun‑Earth L2 Lagrange point.  
Final answer: December 25, 2021; Sun‑Earth L2.
```

## 3. All operators

| Operator | Status | Char edits | d_in_char | Raw | Control | Excess | Correctness (before → after) |
|---|---|---:|---:|---:|---:|---:|---|
| `capitalization` **(selected)** | measured | 1 | 0.0037 | 0.0596 | 0.0000 | +0.0596 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `word_insertion` | measured | 10 | 0.0360 | 0.0134 | 0.0000 | +0.0134 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `char_substitution` | measured | 1 | 0.0037 | 0.0074 | 0.0000 | +0.0074 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `punctuation` | measured | 1 | 0.0037 | 0.0033 | 0.0000 | +0.0033 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `word_deletion` | measured | 4 | 0.0149 | 0.0014 | 0.0000 | +0.0014 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `instruction_reordering` | over_budget: d_in_char 0.6194 exceeds budget 0.10 | 166 | 0.6194 |  |  |  |  |
| `synonym` | inapplicable: inapplicable_or_no_op |  |  |  |  |  |  |
| `whitespace` | over_budget: d_in_char 0.1383 exceeds budget 0.10 | 43 | 0.1383 |  |  |  |  |
| `word_substitution` | inapplicable: inapplicable_or_no_op |  |  |  |  |  |  |

## 4. Input–output trade-off

Eligible edits not dominated by another edit with no more character edits and at least as much excess change:

- `capitalization`: 1 character edit(s) → excess +0.0596

## 5. Source records

Full responses, per-model scores and record IDs are in the JSON file next to this report.

- `qwen/qwen3.8-27b|QA-002|treatment|capitalization|1`: anchor record `d779dbe3-702d-4ca6-92bd-2341e7bcc7cf`, comparison record `deeb512e-c8db-4ba7-94ee-f993fac2057c`
- `openai/gpt-oss-120b|QA-002|treatment|capitalization|1`: anchor record `b6af1a5d-60d5-4512-9a63-9a025d178778`, comparison record `86c0d983-c297-4df1-91a3-3cfef77db768`
- `openai/gpt-oss-20b|QA-002|treatment|capitalization|1`: anchor record `95ad27d3-c79d-474f-be3f-e1485dfa6c14`, comparison record `23c04c53-73a0-43f4-8166-1b46ecf701b0`
- `allam-2-7b|QA-002|treatment|capitalization|1`: anchor record `cdfabecc-2262-46b3-a70b-bd3d4843d0c4`, comparison record `59b9f445-86bc-4a4f-a4bd-f65ce3f60ca0`
- `gemini-3.1-flash-lite|QA-002|treatment|capitalization|1`: anchor record `1144c002-d535-4759-b796-67446f11ed73`, comparison record `b7762347-9d39-4112-ad00-cf5168e1f4b8`
