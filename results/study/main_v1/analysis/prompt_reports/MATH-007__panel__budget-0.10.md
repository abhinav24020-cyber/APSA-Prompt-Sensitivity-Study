# Perturbation operator result: MATH-007 · Mathematical reasoning

**Status:** `selected` · **Rule:** budget mode, d_in_char ≤ 0.10 · **Model scope:** fixed panel of 5 models, equal weights · **Evidence:** retrospective

## 1. Category recommendation

- Recommended: **char_substitution** (exploratory (main_v1 discovery ranking); source: category_operator_rankings.csv (mathematical_reasoning, budget 0.10))
- Category score 0.0853, coverage 8/8 complete prompts
- Why: A typo in prose changes how the task is rendered while leaving quantities and the requested result intact.
- A category recommendation is not a measurement of this prompt; the measured result follows.

## 2. Measured result for this prompt

char_substitution produced the largest control-adjusted change (+0.1419) among 5 eligible, measured edits within budget 0.10. The next best eligible edit was word_deletion (+0.0373). Preservation evidence: not flagged by the retrospective audit (every candidate of this operator was audited).

| Field | Result |
|---|---|
| Prompt and category | `MATH-007` · Mathematical reasoning |
| Original prompt | Alice can complete a job in 6 hours, while Bob can complete the same job in 12 hours. If they work together with Charlie, all three complete the job in 3 hours. How many hours would it take Charlie to complete the job alone? |
| Perturbed prompt | Alice can complete a job in 6 hours, while Bob c@n complete the same job in 12 hours. If they work together with Charlie, all three complete the job in 3 hours. How many hours would it take Charlie to complete the job alone? |
| Operator | `char_substitution`: `can` → `c@n` |
| Input change | **1 character edit(s)**, normalised distance **0.0045**, semantic input distance 0.0165 |
| Model and comparison | fixed panel of 5 models, equal weights; 5 matched model–prompt pair(s) from `main_v1` |
| Output change | Semantic distance **0.1539**, mean unchanged control distance **0.0120**, excess distance **+0.1419** |
| Functional result | Qwen 3.8 27B: correct → correct; same final answer; response length 1930 → 1805 characters; GPT-OSS-120B: correct → correct; final answer text changed; response length 221 → 303 characters; GPT-OSS-20B: correct → correct; same final answer; response length 73 → 20 characters; ALLaM-2-7B: incorrect → correct; final answer text changed; response length 1181 → 1069 characters; Gemini 3.1 Flash-Lite: correct → correct; same final answer; response length 703 → 670 characters |
| Tie status | unique |
| Evidence status | Measured retrospectively from stored main_v1 outputs; this prompt belongs to the discovery set that produced the category ranking, so the result is exploratory. |

### Responses of GPT-OSS-20B (largest effect in the panel)

**Original prompt response**

```text
Charlie would take 12 hours to complete the job alone.  
Final answer: 12
```

**Perturbed prompt response**

```text
12

Final answer: 12
```

## 3. All operators

| Operator | Status | Char edits | d_in_char | Raw | Control | Excess | Correctness (before → after) |
|---|---|---:|---:|---:|---:|---:|---|
| `char_substitution` **(selected)** | measured | 1 | 0.0045 | 0.1539 | 0.0120 | +0.1419 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→correct; Gemini 3.1 Flash-Lite correct→correct |
| `word_deletion` | measured | 4 | 0.0179 | 0.0493 | 0.0120 | +0.0373 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→correct; Gemini 3.1 Flash-Lite correct→correct |
| `word_insertion` | measured | 10 | 0.0427 | 0.0433 | 0.0120 | +0.0313 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→incorrect; Gemini 3.1 Flash-Lite correct→correct |
| `capitalization` | measured | 1 | 0.0045 | 0.0291 | 0.0120 | +0.0171 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→incorrect; Gemini 3.1 Flash-Lite correct→correct |
| `punctuation` | measured | 1 | 0.0045 | 0.0260 | 0.0120 | +0.0140 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→incorrect; Gemini 3.1 Flash-Lite correct→correct |
| `instruction_reordering` | over_budget: d_in_char 0.5714 exceeds budget 0.10 | 128 | 0.5714 |  |  |  |  |
| `synonym` | inapplicable: inapplicable_or_no_op |  |  |  |  |  |  |
| `whitespace` | over_budget: d_in_char 0.1610 exceeds budget 0.10 | 43 | 0.1610 |  |  |  |  |
| `word_substitution` | inapplicable: inapplicable_or_no_op |  |  |  |  |  |  |

## 4. Input–output trade-off

Eligible edits not dominated by another edit with no more character edits and at least as much excess change:

- `char_substitution`: 1 character edit(s) → excess +0.1419

## 5. Source records

Full responses, per-model scores and record IDs are in the JSON file next to this report.

- `qwen/qwen3.8-27b|MATH-007|treatment|char_substitution|1`: anchor record `62dbebad-3f60-47dd-a7d6-facc088eec3d`, comparison record `0f63651b-8b51-44b8-87be-2cac1a6ab68b`
- `openai/gpt-oss-120b|MATH-007|treatment|char_substitution|1`: anchor record `b36cbca1-9cae-4699-b07f-085724619f2f`, comparison record `f10e0182-5113-4288-8428-1754468e0527`
- `openai/gpt-oss-20b|MATH-007|treatment|char_substitution|1`: anchor record `36a55f54-42d9-4535-aa47-ee5206844724`, comparison record `dbc672b4-0765-4419-b82a-c6078e547ba1`
- `allam-2-7b|MATH-007|treatment|char_substitution|1`: anchor record `de647677-ce5b-47c8-a18c-459dc2639ed8`, comparison record `dc9fe8d3-d7ae-4cf5-846c-3977b5eefba7`
- `gemini-3.1-flash-lite|MATH-007|treatment|char_substitution|1`: anchor record `65aad97d-6e79-4d38-90b9-3821be4a285a`, comparison record `9ef3a296-4e60-47f5-8cfd-322d4603825c`
