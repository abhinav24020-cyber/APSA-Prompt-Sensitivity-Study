# Perturbation operator result: CLASS-010 · Classification

**Status:** `selected` · **Rule:** budget mode, d_in_char ≤ 0.10 · **Model scope:** fixed panel of 5 models, equal weights · **Evidence:** retrospective

## 1. Category recommendation

- Recommended: **synonym** (exploratory (main_v1 discovery ranking); source: category_operator_rankings.csv (classification, budget 0.10))
- Category score 0.0761, coverage 10/10 complete prompts
- Why: Replacing an instruction verb (e.g. Classify -> Categorize) changes the cue used to request a label while preserving the label set and evidence.
- A category recommendation is not a measurement of this prompt; the measured result follows.

## 2. Measured result for this prompt

word_deletion produced the largest control-adjusted change (+0.0493) among 6 eligible, measured edits within budget 0.10. The next best eligible edit was capitalization (+0.0481). Preservation evidence: not flagged by the retrospective audit (every candidate of this operator was audited).

| Field | Result |
|---|---|
| Prompt and category | `CLASS-010` · Classification |
| Original prompt | Classify the market stance of the comment as Bullish, Bearish, or Neutral: 'Strong quarterly earnings and expanding margins signal robust growth potential for the semiconductor sector.' |
| Perturbed prompt | Classify market stance of the comment as Bullish, Bearish, or Neutral: 'Strong quarterly earnings and expanding margins signal robust growth potential for the semiconductor sector.' |
| Operator | `word_deletion`: `the` → `∅` |
| Input change | **4 character edit(s)**, normalised distance **0.0216**, semantic input distance 0.0031 |
| Model and comparison | fixed panel of 5 models, equal weights; 5 matched model–prompt pair(s) from `main_v1` |
| Output change | Semantic distance **0.0493**, mean unchanged control distance **0.0000**, excess distance **+0.0493** |
| Functional result | Qwen 3.8 27B: correct → correct; same final answer; response length 280 → 354 characters; GPT-OSS-120B: correct → correct; same final answer; response length 31 → 31 characters; GPT-OSS-20B: correct → correct; same final answer; response length 30 → 30 characters; ALLaM-2-7B: correct → correct; same final answer; response length 31 → 31 characters; Gemini 3.1 Flash-Lite: correct → correct; same final answer; response length 206 → 129 characters |
| Tie status | unique |
| Evidence status | Measured retrospectively from stored main_v1 outputs; this prompt belongs to the discovery set that produced the category ranking, so the result is exploratory. |

### Responses of Qwen 3.8 27B (largest effect in the panel)

**Original prompt response**

```text
The comment highlights "strong quarterly earnings," "expanding margins," and "robust growth potential." These are all positive indicators that suggest the market or sector is expected to perform well and increase in value. Therefore, the stance is positive.

Final answer: Bullish
```

**Perturbed prompt response**

```text
The comment highlights "strong quarterly earnings" and "expanding margins," which are positive fundamental indicators. Furthermore, it explicitly mentions "robust growth potential," indicating an optimistic outlook on the future performance of the semiconductor sector. These factors collectively point to a positive market stance.

Final answer: Bullish
```

## 3. All operators

| Operator | Status | Char edits | d_in_char | Raw | Control | Excess | Correctness (before → after) |
|---|---|---:|---:|---:|---:|---:|---|
| `word_deletion` **(selected)** | measured | 4 | 0.0216 | 0.0493 | 0.0000 | +0.0493 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `capitalization` | measured | 1 | 0.0054 | 0.0481 | 0.0000 | +0.0481 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `synonym` | measured | 8 | 0.0428 | 0.0468 | 0.0000 | +0.0468 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `word_insertion` | measured | 10 | 0.0513 | 0.0458 | 0.0000 | +0.0458 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `punctuation` | measured | 1 | 0.0054 | 0.0406 | 0.0000 | +0.0406 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `char_substitution` | measured | 1 | 0.0054 | 0.0187 | 0.0000 | +0.0187 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `instruction_reordering` | inapplicable: inapplicable_or_no_op |  |  |  |  |  |  |
| `whitespace` | over_budget: d_in_char 0.1190 exceeds budget 0.10 | 25 | 0.1190 |  |  |  |  |
| `word_substitution` | inapplicable: inapplicable_or_no_op |  |  |  |  |  |  |

## 4. Input–output trade-off

Eligible edits not dominated by another edit with no more character edits and at least as much excess change:

- `capitalization`: 1 character edit(s) → excess +0.0481
- `word_deletion`: 4 character edit(s) → excess +0.0493

## 5. Source records

Full responses, per-model scores and record IDs are in the JSON file next to this report.

- `qwen/qwen3.8-27b|CLASS-010|treatment|word_deletion|1`: anchor record `b7159248-9fb2-434f-8335-247e376c9828`, comparison record `6002e2b0-30b6-4f30-92b2-a2ad4cf78cb4`
- `openai/gpt-oss-120b|CLASS-010|treatment|word_deletion|1`: anchor record `d9562f6a-6e45-4270-8ee8-92221dc546ff`, comparison record `9827c06f-5bf7-46fd-a5ec-55f2577c6d6c`
- `openai/gpt-oss-20b|CLASS-010|treatment|word_deletion|1`: anchor record `5aca7f0d-4963-40ed-b4ca-b0efee5d608d`, comparison record `8a09b115-25e9-4eb8-8501-82b8cd0c54a8`
- `allam-2-7b|CLASS-010|treatment|word_deletion|1`: anchor record `f970215c-d30b-4232-9d32-c622590e685e`, comparison record `7a48d04c-2d98-4ad1-9d02-66c799430ced`
- `gemini-3.1-flash-lite|CLASS-010|treatment|word_deletion|1`: anchor record `60ad0921-de8c-442a-ad79-ff957b6f3332`, comparison record `9b87d86f-91af-465d-b99c-9f5cd8bed91b`
