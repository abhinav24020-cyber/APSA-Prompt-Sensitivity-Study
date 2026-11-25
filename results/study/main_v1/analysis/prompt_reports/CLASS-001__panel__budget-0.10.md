# Perturbation operator result: CLASS-001 · Classification

**Status:** `selected` · **Rule:** budget mode, d_in_char ≤ 0.10 · **Model scope:** fixed panel of 5 models, equal weights · **Evidence:** retrospective

## 1. Category recommendation

- Recommended: **synonym** (exploratory (main_v1 discovery ranking); source: category_operator_rankings.csv (classification, budget 0.10))
- Category score 0.0761, coverage 10/10 complete prompts
- Why: Replacing an instruction verb (e.g. Classify -> Categorize) changes the cue used to request a label while preserving the label set and evidence.
- A category recommendation is not a measurement of this prompt; the measured result follows.

## 2. Measured result for this prompt

capitalization produced the largest control-adjusted change (+0.0950) among 6 eligible, measured edits within budget 0.10. The next best eligible edit was synonym (+0.0846). Preservation evidence: not flagged by the retrospective audit (operator audited by a sample of 5 candidates).

| Field | Result |
|---|---|
| Prompt and category | `CLASS-001` · Classification |
| Original prompt | Classify the sentiment of the following product review as Positive, Negative, or Neutral: 'The battery life is acceptable, but the screen scratches easily and customer support was unhelpful.' |
| Perturbed prompt | classify the sentiment of the following product review as Positive, Negative, or Neutral: 'The battery life is acceptable, but the screen scratches easily and customer support was unhelpful.' |
| Operator | `capitalization`: `Classify` → `classify` |
| Input change | **1 character edit(s)**, normalised distance **0.0052**, semantic input distance 0.0000 |
| Model and comparison | fixed panel of 5 models, equal weights; 5 matched model–prompt pair(s) from `main_v1` |
| Output change | Semantic distance **0.0950**, mean unchanged control distance **0.0000**, excess distance **+0.0950** |
| Functional result | Qwen 3.8 27B: correct → correct; same final answer; response length 391 → 404 characters; GPT-OSS-120B: correct → correct; same final answer; response length 32 → 32 characters; GPT-OSS-20B: correct → correct; same final answer; response length 32 → 32 characters; ALLaM-2-7B: incorrect → correct; final answer text changed; response length 412 → 160 characters; Gemini 3.1 Flash-Lite: correct → correct; same final answer; response length 225 → 225 characters |
| Tie status | unique |
| Evidence status | Measured retrospectively from stored main_v1 outputs; this prompt belongs to the discovery set that produced the category ranking, so the result is exploratory. |

### Responses of ALLaM-2-7B (largest effect in the panel)

**Original prompt response**

```text
Final answer: Negative

Code:
import textblob

review = "The battery life is acceptable, but the screen scratches easily and customer support was unhelpful."
sentiment = textblob.TextBlob(review).sentiment

if sentiment.polarity < 0:
    sentiment_label = "Negative"
elif sentiment.polarity == 0:
    sentiment_label = "Neutral"
else:
    sentiment_label = "Positive"

print("Sentiment label:", sentiment_label)
```

**Perturbed prompt response**

```text
Final answer: Negative

The sentiment of the review can be classified as negative due to the mention of issues with battery life, screen, and customer support.
```

## 3. All operators

| Operator | Status | Char edits | d_in_char | Raw | Control | Excess | Correctness (before → after) |
|---|---|---:|---:|---:|---:|---:|---|
| `capitalization` **(selected)** | measured | 1 | 0.0052 | 0.0950 | 0.0000 | +0.0950 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→correct; Gemini 3.1 Flash-Lite correct→correct |
| `synonym` | measured | 8 | 0.0415 | 0.0846 | 0.0000 | +0.0846 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→correct; Gemini 3.1 Flash-Lite correct→correct |
| `word_insertion` | measured | 10 | 0.0498 | 0.0474 | 0.0000 | +0.0474 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→incorrect; Gemini 3.1 Flash-Lite correct→correct |
| `word_deletion` | measured | 4 | 0.0209 | 0.0473 | 0.0000 | +0.0473 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→incorrect; Gemini 3.1 Flash-Lite correct→correct |
| `char_substitution` | measured | 1 | 0.0052 | 0.0446 | 0.0000 | +0.0446 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→incorrect; Gemini 3.1 Flash-Lite correct→correct |
| `punctuation` | measured | 1 | 0.0052 | 0.0154 | 0.0000 | +0.0154 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→incorrect; Gemini 3.1 Flash-Lite correct→correct |
| `instruction_reordering` | inapplicable: inapplicable_or_no_op |  |  |  |  |  |  |
| `whitespace` | over_budget: d_in_char 0.1239 exceeds budget 0.10 | 27 | 0.1239 |  |  |  |  |
| `word_substitution` | inapplicable: inapplicable_or_no_op |  |  |  |  |  |  |

## 4. Input–output trade-off

Eligible edits not dominated by another edit with no more character edits and at least as much excess change:

- `capitalization`: 1 character edit(s) → excess +0.0950

## 5. Source records

Full responses, per-model scores and record IDs are in the JSON file next to this report.

- `qwen/qwen3.8-27b|CLASS-001|treatment|capitalization|1`: anchor record `3b6f0116-f19e-4391-8a83-353c34d3b319`, comparison record `8df3cb7b-a089-49c6-ad25-83cbe420d1e7`
- `openai/gpt-oss-120b|CLASS-001|treatment|capitalization|1`: anchor record `72b7e5b8-e040-4986-8039-6a09da2e5900`, comparison record `61be0f1b-483b-4f6e-b4db-373bb0b4268d`
- `openai/gpt-oss-20b|CLASS-001|treatment|capitalization|1`: anchor record `184aa270-11aa-4962-84ac-dc21416de39c`, comparison record `fb75a536-1ca8-4822-b35b-bf4fff24efcd`
- `allam-2-7b|CLASS-001|treatment|capitalization|1`: anchor record `850cd311-d07c-449f-ab21-10857ba70ecf`, comparison record `8d6f409f-8813-42a2-880e-23ea1c24b233`
- `gemini-3.1-flash-lite|CLASS-001|treatment|capitalization|1`: anchor record `56545dba-7280-4a47-9938-28a77a979264`, comparison record `08990916-8c54-4548-a17e-e0328aa7ddf0`
