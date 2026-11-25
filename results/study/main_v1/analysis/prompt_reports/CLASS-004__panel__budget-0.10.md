# Perturbation operator result: CLASS-004 · Classification

**Status:** `selected` · **Rule:** budget mode, d_in_char ≤ 0.10 · **Model scope:** fixed panel of 5 models, equal weights · **Evidence:** retrospective

## 1. Category recommendation

- Recommended: **synonym** (exploratory (main_v1 discovery ranking); source: category_operator_rankings.csv (classification, budget 0.10))
- Category score 0.0761, coverage 10/10 complete prompts
- Why: Replacing an instruction verb (e.g. Classify -> Categorize) changes the cue used to request a label while preserving the label set and evidence.
- A category recommendation is not a measurement of this prompt; the measured result follows.

## 2. Measured result for this prompt

char_substitution produced the largest control-adjusted change (+0.0628) among 6 eligible, measured edits within budget 0.10. The next best eligible edit was capitalization (+0.0551). Preservation evidence: not flagged by the retrospective audit (every candidate of this operator was audited).

| Field | Result |
|---|---|
| Prompt and category | `CLASS-004` · Classification |
| Original prompt | Classify the following email snippet as Spam or Ham (Not Spam): 'CONGRATULATIONS! You have won a $1000 gift card. Click this link immediately to claim your prize before it expires.' |
| Perturbed prompt | Classify the following email snippet as Spam or Ham (Not Spam): 'CONGRATULATIONS! You have won a $1000 gift card. Click this link immediately to claim your pr1ze before it expires.' |
| Operator | `char_substitution`: `prize` → `pr1ze` |
| Input change | **1 character edit(s)**, normalised distance **0.0055**, semantic input distance 0.0431 |
| Model and comparison | fixed panel of 5 models, equal weights; 5 matched model–prompt pair(s) from `main_v1` |
| Output change | Semantic distance **0.0628**, mean unchanged control distance **0.0000**, excess distance **+0.0628** |
| Functional result | Qwen 3.8 27B: correct → correct; same final answer; response length 423 → 491 characters; GPT-OSS-120B: correct → correct; same final answer; response length 23 → 24 characters; GPT-OSS-20B: correct → correct; same final answer; response length 25 → 24 characters; ALLaM-2-7B: incorrect → incorrect; response length 238 → 265 characters; Gemini 3.1 Flash-Lite: correct → correct; same final answer; response length 194 → 238 characters |
| Tie status | unique |
| Evidence status | Measured retrospectively from stored main_v1 outputs; this prompt belongs to the discovery set that produced the category ranking, so the result is exploratory. |

### Responses of Gemini 3.1 Flash-Lite (largest effect in the panel)

**Original prompt response**

```text
The email snippet is classified as Spam because it uses common phishing tactics such as urgent language, promises of a high-value prize, and a call to click an external link.

Final answer: Spam
```

**Perturbed prompt response**

```text
The email snippet uses classic phishing tactics, including urgent language ("immediately"), promises of high-value rewards ("$1000 gift card"), and suspicious character substitution ("pr1ze"). It is classified as Spam.

Final answer: Spam
```

## 3. All operators

| Operator | Status | Char edits | d_in_char | Raw | Control | Excess | Correctness (before → after) |
|---|---|---:|---:|---:|---:|---:|---|
| `char_substitution` **(selected)** | measured | 1 | 0.0055 | 0.0628 | 0.0000 | +0.0628 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→incorrect; Gemini 3.1 Flash-Lite correct→correct |
| `capitalization` | measured | 1 | 0.0055 | 0.0551 | 0.0000 | +0.0551 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→incorrect; Gemini 3.1 Flash-Lite correct→correct |
| `word_deletion` | measured | 4 | 0.0221 | 0.0544 | 0.0000 | +0.0544 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→incorrect; Gemini 3.1 Flash-Lite correct→correct |
| `word_insertion` | measured | 10 | 0.0524 | 0.0481 | 0.0000 | +0.0481 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→incorrect; Gemini 3.1 Flash-Lite correct→correct |
| `synonym` | measured | 8 | 0.0437 | 0.0431 | 0.0000 | +0.0430 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→incorrect; Gemini 3.1 Flash-Lite correct→correct |
| `punctuation` | measured | 1 | 0.0055 | 0.0182 | 0.0000 | +0.0182 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→incorrect; Gemini 3.1 Flash-Lite correct→correct |
| `instruction_reordering` | over_budget: d_in_char 0.7514 exceeds budget 0.10 | 136 | 0.7514 |  |  |  |  |
| `whitespace` | over_budget: d_in_char 0.1381 exceeds budget 0.10 | 29 | 0.1381 |  |  |  |  |
| `word_substitution` | inapplicable: inapplicable_or_no_op |  |  |  |  |  |  |

## 4. Input–output trade-off

Eligible edits not dominated by another edit with no more character edits and at least as much excess change:

- `char_substitution`: 1 character edit(s) → excess +0.0628

## 5. Source records

Full responses, per-model scores and record IDs are in the JSON file next to this report.

- `qwen/qwen3.8-27b|CLASS-004|treatment|char_substitution|1`: anchor record `8c48f25f-c825-444e-9650-50442957f52a`, comparison record `e7448c5f-6fa2-4d33-b5e3-7dd3273ab2d9`
- `openai/gpt-oss-120b|CLASS-004|treatment|char_substitution|1`: anchor record `c34eb730-19af-4229-a40a-6826a44dd6eb`, comparison record `1215f800-970e-4941-aa32-f021883df2d0`
- `openai/gpt-oss-20b|CLASS-004|treatment|char_substitution|1`: anchor record `198214ac-351d-4e17-8066-31a32bf6426a`, comparison record `a1ed41aa-9256-4707-b92c-78b8a5806790`
- `allam-2-7b|CLASS-004|treatment|char_substitution|1`: anchor record `29d15c7b-75aa-4e5a-a25e-2e1b19426cd6`, comparison record `c7426776-6f95-4ca4-a90f-ab18919ec591`
- `gemini-3.1-flash-lite|CLASS-004|treatment|char_substitution|1`: anchor record `4aacb8ab-08e6-4d47-a5f2-00a2536200e0`, comparison record `514fee57-ce9e-482a-b186-82142bb89c90`
