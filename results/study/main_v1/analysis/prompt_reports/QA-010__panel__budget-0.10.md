# Perturbation operator result: QA-010 · Question answering

**Status:** `selected` · **Rule:** budget mode, d_in_char ≤ 0.10 · **Model scope:** fixed panel of 5 models, equal weights · **Evidence:** retrospective

## 1. Category recommendation

- Recommended: **punctuation** (exploratory (main_v1 discovery ranking); source: category_operator_rankings.csv (question_answering, budget 0.10))
- Category score 0.0426, coverage 10/10 complete prompts
- Why: Editing the question's final delimiter can change the form or length of the answer while keeping the requested fact fixed.
- A category recommendation is not a measurement of this prompt; the measured result follows.

## 2. Measured result for this prompt

word_deletion produced the largest control-adjusted change (+0.0227) among 4 eligible, measured edits within budget 0.10. The next best eligible edit was char_substitution (+0.0196). Preservation evidence: not flagged by the retrospective audit (every candidate of this operator was audited).

| Field | Result |
|---|---|
| Prompt and category | `QA-010` · Question answering |
| Original prompt | What is the chemical symbol for Gold, and what is its atomic number? |
| Perturbed prompt | What is chemical symbol for Gold, and what is its atomic number? |
| Operator | `word_deletion`: `the` → `∅` |
| Input change | **4 character edit(s)**, normalised distance **0.0588**, semantic input distance 0.0035 |
| Model and comparison | fixed panel of 5 models, equal weights; 5 matched model–prompt pair(s) from `main_v1` |
| Output change | Semantic distance **0.0227**, mean unchanged control distance **0.0000**, excess distance **+0.0227** |
| Functional result | Qwen 3.8 27B: correct → correct; same final answer; response length 94 → 94 characters; GPT-OSS-120B: correct → correct; same final answer; response length 88 → 94 characters; GPT-OSS-20B: correct → correct; same final answer; response length 90 → 50 characters; ALLaM-2-7B: correct → correct; final answer text changed; response length 123 → 108 characters; Gemini 3.1 Flash-Lite: correct → correct; same final answer; response length 86 → 86 characters |
| Tie status | unique |
| Evidence status | Measured retrospectively from stored main_v1 outputs; this prompt belongs to the discovery set that produced the category ranking, so the result is exploratory. |

### Responses of GPT-OSS-20B (largest effect in the panel)

**Original prompt response**

```text
Gold has the chemical symbol **Au** and an atomic number of **79**.  
Final answer: Au, 79
```

**Perturbed prompt response**

```text
Gold: Au, atomic number 79.  
Final answer: Au, 79
```

## 3. All operators

| Operator | Status | Char edits | d_in_char | Raw | Control | Excess | Correctness (before → after) |
|---|---|---:|---:|---:|---:|---:|---|
| `word_deletion` **(selected)** | measured | 4 | 0.0588 | 0.0227 | 0.0000 | +0.0227 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `char_substitution` | measured | 1 | 0.0147 | 0.0196 | 0.0000 | +0.0196 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `punctuation` | measured | 1 | 0.0147 | 0.0085 | 0.0000 | +0.0085 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `capitalization` | measured | 1 | 0.0147 | 0.0023 | 0.0000 | +0.0023 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `instruction_reordering` | inapplicable: inapplicable_or_no_op |  |  |  |  |  |  |
| `synonym` | meaning_changing: retrospective audit flag: question_changed | 5 | 0.0735 |  |  |  |  |
| `whitespace` | over_budget: d_in_char 0.1500 exceeds budget 0.10 | 12 | 0.1500 |  |  |  |  |
| `word_insertion` | over_budget: d_in_char 0.1282 exceeds budget 0.10 | 10 | 0.1282 |  |  |  |  |
| `word_substitution` | inapplicable: inapplicable_or_no_op |  |  |  |  |  |  |

## 4. Input–output trade-off

Eligible edits not dominated by another edit with no more character edits and at least as much excess change:

- `char_substitution`: 1 character edit(s) → excess +0.0196
- `word_deletion`: 4 character edit(s) → excess +0.0227

## 5. Source records

Full responses, per-model scores and record IDs are in the JSON file next to this report.

- `qwen/qwen3.8-27b|QA-010|treatment|word_deletion|1`: anchor record `74b1969b-7d6a-4368-8339-faa248cc3c39`, comparison record `7a0c0136-bb16-4fcc-a367-93633b643b77`
- `openai/gpt-oss-120b|QA-010|treatment|word_deletion|1`: anchor record `46771da9-80c2-42a2-9c56-fb2b4f343b45`, comparison record `1677408a-ab5e-4b25-8d7e-237f6942e30b`
- `openai/gpt-oss-20b|QA-010|treatment|word_deletion|1`: anchor record `b3618323-9aba-4018-a562-b8e7b7078e3d`, comparison record `655a38e9-d3a7-443a-a1e3-18cacfc057a0`
- `allam-2-7b|QA-010|treatment|word_deletion|1`: anchor record `b06fede1-26df-4d0b-98e4-c9d72c3415f6`, comparison record `b423bcf7-ebc8-4c8c-bb2d-0d2f17ca5a0a`
- `gemini-3.1-flash-lite|QA-010|treatment|word_deletion|1`: anchor record `1681a8cf-20aa-423a-9fcd-1c4ede35fb8f`, comparison record `ed3cb12a-755a-4b44-bddf-c8f5f7dea6a3`
