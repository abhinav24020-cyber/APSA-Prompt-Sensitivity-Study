# Perturbation operator result: CLASS-005 · Classification

**Status:** `selected` · **Rule:** budget mode, d_in_char ≤ 0.10 · **Model scope:** fixed panel of 5 models, equal weights · **Evidence:** retrospective

## 1. Category recommendation

- Recommended: **synonym** (exploratory (main_v1 discovery ranking); source: category_operator_rankings.csv (classification, budget 0.10))
- Category score 0.0761, coverage 10/10 complete prompts
- Why: Replacing an instruction verb (e.g. Classify -> Categorize) changes the cue used to request a label while preserving the label set and evidence.
- A category recommendation is not a measurement of this prompt; the measured result follows.

## 2. Measured result for this prompt

word_insertion produced the largest control-adjusted change (+0.2016) among 6 eligible, measured edits within budget 0.10. The next best eligible edit was punctuation (+0.1577). Preservation evidence: not flagged by the retrospective audit (operator audited by a sample of 5 candidates).

| Field | Result |
|---|---|
| Prompt and category | `CLASS-005` · Classification |
| Original prompt | Identify the primary emotion expressed in the statement: 'I cannot believe they cancelled the concert after I waited six hours in the rain!' Options: [Joy, Anger, Fear, Sadness, Surprise]. |
| Perturbed prompt | Carefully Identify the primary emotion expressed in the statement: 'I cannot believe they cancelled the concert after I waited six hours in the rain!' Options: [Joy, Anger, Fear, Sadness, Surprise]. |
| Operator | `word_insertion`: `∅` → `Carefully` |
| Input change | **10 character edit(s)**, normalised distance **0.0505**, semantic input distance 0.0133 |
| Model and comparison | fixed panel of 5 models, equal weights; 5 matched model–prompt pair(s) from `main_v1` |
| Output change | Semantic distance **0.2016**, mean unchanged control distance **0.0000**, excess distance **+0.2016** |
| Functional result | Qwen 3.8 27B: correct → correct; same final answer; response length 381 → 1588 characters; GPT-OSS-120B: correct → correct; same final answer; response length 27 → 27 characters; GPT-OSS-20B: correct → correct; response length 5 → 5 characters; ALLaM-2-7B: correct → correct; final answer text changed; response length 195 → 20 characters; Gemini 3.1 Flash-Lite: correct → correct; same final answer; response length 217 → 144 characters |
| Tie status | unique |
| Evidence status | Measured retrospectively from stored main_v1 outputs; this prompt belongs to the discovery set that produced the category ranking, so the result is exploratory. |

### Responses of ALLaM-2-7B (largest effect in the panel)

**Original prompt response**

```text
Final answer: Anger

The primary emotion expressed in the statement is anger because the person is upset about the concert cancellation and the associated negative experience of waiting in rain.
```

**Perturbed prompt response**

```text
Final answer: Anger
```

## 3. All operators

| Operator | Status | Char edits | d_in_char | Raw | Control | Excess | Correctness (before → after) |
|---|---|---:|---:|---:|---:|---:|---|
| `word_insertion` **(selected)** | measured | 10 | 0.0505 | 0.2016 | 0.0000 | +0.2016 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `punctuation` | measured | 1 | 0.0053 | 0.1577 | 0.0000 | +0.1577 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `synonym` | measured | 8 | 0.0423 | 0.1521 | 0.0000 | +0.1521 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `word_deletion` | measured | 4 | 0.0213 | 0.1148 | 0.0000 | +0.1148 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `word_substitution` | measured | 6 | 0.0319 | 0.1020 | 0.0000 | +0.1020 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `capitalization` | measured | 1 | 0.0053 | 0.0906 | 0.0000 | +0.0906 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `char_substitution` | meaning_changing: retrospective audit flag: answer_option_changed | 1 | 0.0053 |  |  |  |  |
| `instruction_reordering` | inapplicable: inapplicable_or_no_op |  |  |  |  |  |  |
| `whitespace` | over_budget: d_in_char 0.1296 exceeds budget 0.10 | 28 | 0.1296 |  |  |  |  |

## 4. Input–output trade-off

Eligible edits not dominated by another edit with no more character edits and at least as much excess change:

- `punctuation`: 1 character edit(s) → excess +0.1577
- `word_insertion`: 10 character edit(s) → excess +0.2016

## 5. Source records

Full responses, per-model scores and record IDs are in the JSON file next to this report.

- `qwen/qwen3.8-27b|CLASS-005|treatment|word_insertion|1`: anchor record `316fe6e5-88b9-46eb-b2a1-caaca8276856`, comparison record `e66fd026-19ef-46ad-92b0-0d92e948dcce`
- `openai/gpt-oss-120b|CLASS-005|treatment|word_insertion|1`: anchor record `7012b644-371e-4782-918e-96507b1e1376`, comparison record `f08ae5a4-ef95-480a-8c0f-da91aab7bff6`
- `openai/gpt-oss-20b|CLASS-005|treatment|word_insertion|1`: anchor record `5b37144b-3776-4afb-8fde-6ba09b21a4aa`, comparison record `b4955e79-81d3-4693-9929-50d37e72611d`
- `allam-2-7b|CLASS-005|treatment|word_insertion|1`: anchor record `0d6f5dee-ebb0-4df9-986f-6847703483ae`, comparison record `e00600d7-3e81-42b5-9f86-465fef5a30e6`
- `gemini-3.1-flash-lite|CLASS-005|treatment|word_insertion|1`: anchor record `02b6d77f-2d25-4e03-8f81-7909d83b785a`, comparison record `0a2179aa-1a20-4a1b-8eb1-5a723c560508`
