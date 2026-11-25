# Perturbation operator result: MATH-009 · Mathematical reasoning

**Status:** `selected` · **Rule:** budget mode, d_in_char ≤ 0.10 · **Model scope:** fixed panel of 5 models, equal weights · **Evidence:** retrospective

## 1. Category recommendation

- Recommended: **char_substitution** (exploratory (main_v1 discovery ranking); source: category_operator_rankings.csv (mathematical_reasoning, budget 0.10))
- Category score 0.0853, coverage 8/8 complete prompts
- Why: A typo in prose changes how the task is rendered while leaving quantities and the requested result intact.
- A category recommendation is not a measurement of this prompt; the measured result follows.

## 2. Measured result for this prompt

char_substitution produced the largest control-adjusted change (+0.1267) among 5 eligible, measured edits within budget 0.10. The next best eligible edit was word_insertion (+0.1231). Preservation evidence: not flagged by the retrospective audit (every candidate of this operator was audited).

| Field | Result |
|---|---|
| Prompt and category | `MATH-009` · Mathematical reasoning |
| Original prompt | Two trains start from stations 300 miles apart and travel towards each other on parallel tracks. Train A travels at 60 mph and Train B travels at 90 mph. How many hours will it take for the two trains to meet? |
| Perturbed prompt | Two trains start from stations 300 miles apart and travel towards each other on parallel tracks. Train A travels at 60 mph and Train B travels at 90 mph. How m@ny hours will it take for the two trains to meet? |
| Operator | `char_substitution`: `many` → `m@ny` |
| Input change | **1 character edit(s)**, normalised distance **0.0048**, semantic input distance 0.0711 |
| Model and comparison | fixed panel of 5 models, equal weights; 5 matched model–prompt pair(s) from `main_v1` |
| Output change | Semantic distance **0.1300**, mean unchanged control distance **0.0033**, excess distance **+0.1267** |
| Functional result | Qwen 3.8 27B: correct → correct; same final answer; response length 673 → 710 characters; GPT-OSS-120B: correct → correct; same final answer; response length 200 → 213 characters; GPT-OSS-20B: correct → correct; same final answer; response length 24 → 66 characters; ALLaM-2-7B: correct → correct; same final answer; response length 277 → 277 characters; Gemini 3.1 Flash-Lite: correct → correct; same final answer; response length 479 → 242 characters |
| Tie status | unique |
| Evidence status | Measured retrospectively from stored main_v1 outputs; this prompt belongs to the discovery set that produced the category ranking, so the result is exploratory. |

### Responses of GPT-OSS-20B (largest effect in the panel)

**Original prompt response**

```text
2 hours

Final answer: 2
```

**Perturbed prompt response**

```text
It will take 2 hours for the two trains to meet.  
Final answer: 2
```

## 3. All operators

| Operator | Status | Char edits | d_in_char | Raw | Control | Excess | Correctness (before → after) |
|---|---|---:|---:|---:|---:|---:|---|
| `char_substitution` **(selected)** | measured | 1 | 0.0048 | 0.1300 | 0.0033 | +0.1267 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `word_insertion` | measured | 10 | 0.0457 | 0.1264 | 0.0033 | +0.1231 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→incorrect; Gemini 3.1 Flash-Lite correct→correct |
| `word_deletion` | measured | 4 | 0.0191 | 0.0302 | 0.0033 | +0.0269 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `capitalization` | measured | 1 | 0.0048 | 0.0215 | 0.0033 | +0.0182 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `punctuation` | measured | 1 | 0.0048 | 0.0030 | 0.0033 | -0.0003 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `instruction_reordering` | over_budget: d_in_char 0.5359 exceeds budget 0.10 | 112 | 0.5359 |  |  |  |  |
| `synonym` | inapplicable: inapplicable_or_no_op |  |  |  |  |  |  |
| `whitespace` | over_budget: d_in_char 0.1606 exceeds budget 0.10 | 40 | 0.1606 |  |  |  |  |
| `word_substitution` | inapplicable: inapplicable_or_no_op |  |  |  |  |  |  |

## 4. Input–output trade-off

Eligible edits not dominated by another edit with no more character edits and at least as much excess change:

- `char_substitution`: 1 character edit(s) → excess +0.1267

## 5. Source records

Full responses, per-model scores and record IDs are in the JSON file next to this report.

- `qwen/qwen3.8-27b|MATH-009|treatment|char_substitution|1`: anchor record `20e02cbb-4268-4202-8533-a9af8d00bba1`, comparison record `1f462a17-eeb9-4b49-ae64-9f10a857b3da`
- `openai/gpt-oss-120b|MATH-009|treatment|char_substitution|1`: anchor record `786f7511-5095-424f-adf0-2215cc6a63d8`, comparison record `9a25d8a6-84e0-4aa9-86e9-ea1a40fb694c`
- `openai/gpt-oss-20b|MATH-009|treatment|char_substitution|1`: anchor record `fbb24064-2255-4fbd-a2d9-9ad00352be95`, comparison record `9f7befcf-85d7-458d-9792-1610cf6fc8c9`
- `allam-2-7b|MATH-009|treatment|char_substitution|1`: anchor record `cc0a6cdd-1bdf-434d-a9d8-13125ccfb316`, comparison record `ed1f7569-0268-409a-a3ac-1d743d741cfc`
- `gemini-3.1-flash-lite|MATH-009|treatment|char_substitution|1`: anchor record `2aa4531a-7f3b-4727-85ca-43ad40b246fa`, comparison record `de50e795-859f-4ca9-98d1-4655150c55ac`
