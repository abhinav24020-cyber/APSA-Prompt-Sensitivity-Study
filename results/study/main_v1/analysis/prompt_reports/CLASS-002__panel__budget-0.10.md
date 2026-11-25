# Perturbation operator result: CLASS-002 · Classification

**Status:** `selected` · **Rule:** budget mode, d_in_char ≤ 0.10 · **Model scope:** fixed panel of 5 models, equal weights · **Evidence:** retrospective

## 1. Category recommendation

- Recommended: **synonym** (exploratory (main_v1 discovery ranking); source: category_operator_rankings.csv (classification, budget 0.10))
- Category score 0.0761, coverage 10/10 complete prompts
- Why: Replacing an instruction verb (e.g. Classify -> Categorize) changes the cue used to request a label while preserving the label set and evidence.
- A category recommendation is not a measurement of this prompt; the measured result follows.

## 2. Measured result for this prompt

synonym produced the largest control-adjusted change (+0.1406) among 6 eligible, measured edits within budget 0.10. The next best eligible edit was word_insertion (+0.0556). Preservation evidence: not flagged by the retrospective audit (every candidate of this operator was audited).

| Field | Result |
|---|---|
| Prompt and category | `CLASS-002` · Classification |
| Original prompt | Classify the topic of this news headline into one of [Sports, Technology, Politics, Business]: 'Central bank raises interest rates by 50 basis points to curb inflation.' |
| Perturbed prompt | Categorize the topic of this news headline into one of [Sports, Technology, Politics, Business]: 'Central bank raises interest rates by 50 basis points to curb inflation.' |
| Operator | `synonym`: `Classify` → `Categorize` |
| Input change | **8 character edit(s)**, normalised distance **0.0468**, semantic input distance 0.0315 |
| Model and comparison | fixed panel of 5 models, equal weights; 5 matched model–prompt pair(s) from `main_v1` |
| Output change | Semantic distance **0.1406**, mean unchanged control distance **0.0000**, excess distance **+0.1406** |
| Functional result | Qwen 3.8 27B: incorrect → incorrect; same final answer; response length 480 → 441 characters; GPT-OSS-120B: correct → correct; same final answer; response length 32 → 32 characters; GPT-OSS-20B: correct → incorrect; final answer text changed; response length 32 → 32 characters; ALLaM-2-7B: correct → correct; same final answer; response length 23 → 43 characters; Gemini 3.1 Flash-Lite: correct → correct; same final answer; response length 137 → 137 characters |
| Tie status | unique |
| Evidence status | Measured retrospectively from stored main_v1 outputs; this prompt belongs to the discovery set that produced the category ranking, so the result is exploratory. |

### Responses of GPT-OSS-20B (largest effect in the panel)

**Original prompt response**

```text
Business

Final answer: Business
```

**Perturbed prompt response**

```text
Politics

Final answer: Politics
```

## 3. All operators

| Operator | Status | Char edits | d_in_char | Raw | Control | Excess | Correctness (before → after) |
|---|---|---:|---:|---:|---:|---:|---|
| `synonym` **(selected)** | measured | 8 | 0.0468 | 0.1406 | 0.0000 | +0.1406 | Qwen 3.8 27B incorrect→incorrect; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→incorrect; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `word_insertion` | measured | 10 | 0.0559 | 0.0556 | 0.0000 | +0.0556 | Qwen 3.8 27B incorrect→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `capitalization` | measured | 1 | 0.0059 | 0.0378 | 0.0000 | +0.0378 | Qwen 3.8 27B incorrect→incorrect; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `word_deletion` | measured | 4 | 0.0237 | 0.0165 | 0.0000 | +0.0165 | Qwen 3.8 27B incorrect→incorrect; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `char_substitution` | measured | 1 | 0.0059 | 0.0039 | 0.0000 | +0.0039 | Qwen 3.8 27B incorrect→incorrect; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `punctuation` | measured | 1 | 0.0059 | 0.0000 | 0.0000 | +0.0000 | Qwen 3.8 27B incorrect→incorrect; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `instruction_reordering` | inapplicable: inapplicable_or_no_op |  |  |  |  |  |  |
| `whitespace` | over_budget: d_in_char 0.1289 exceeds budget 0.10 | 25 | 0.1289 |  |  |  |  |
| `word_substitution` | inapplicable: inapplicable_or_no_op |  |  |  |  |  |  |

## 4. Input–output trade-off

Eligible edits not dominated by another edit with no more character edits and at least as much excess change:

- `capitalization`: 1 character edit(s) → excess +0.0378
- `synonym`: 8 character edit(s) → excess +0.1406

## 5. Source records

Full responses, per-model scores and record IDs are in the JSON file next to this report.

- `qwen/qwen3.8-27b|CLASS-002|treatment|synonym|1`: anchor record `203db736-baed-4581-8236-0915f5e9dfe5`, comparison record `86d5b883-65d4-498f-813b-b64e46d63dcc`
- `openai/gpt-oss-120b|CLASS-002|treatment|synonym|1`: anchor record `79ed0e85-a1f3-4785-9a21-2fe0f7b9f171`, comparison record `c39f6446-f45d-4ded-8c60-019b8412a5f9`
- `openai/gpt-oss-20b|CLASS-002|treatment|synonym|1`: anchor record `f86338b2-9d5b-4eb1-9722-c80fdc94ea8d`, comparison record `5852d77e-d39b-4d43-b6e2-44da97d402b3`
- `allam-2-7b|CLASS-002|treatment|synonym|1`: anchor record `788c6cdd-69d2-4653-9c9b-a57d51c1456e`, comparison record `c397d005-2b4c-4bf9-98d6-de884bb0e3c4`
- `gemini-3.1-flash-lite|CLASS-002|treatment|synonym|1`: anchor record `eaa60927-44e5-4496-97b4-dee70f1a1db1`, comparison record `e83bb75f-26b2-4c3a-9a7e-86346d9c949b`
