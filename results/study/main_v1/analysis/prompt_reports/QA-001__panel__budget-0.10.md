# Perturbation operator result: QA-001 · Question answering

**Status:** `selected` · **Rule:** budget mode, d_in_char ≤ 0.10 · **Model scope:** fixed panel of 5 models, equal weights · **Evidence:** retrospective

## 1. Category recommendation

- Recommended: **punctuation** (exploratory (main_v1 discovery ranking); source: category_operator_rankings.csv (question_answering, budget 0.10))
- Category score 0.0426, coverage 10/10 complete prompts
- Why: Editing the question's final delimiter can change the form or length of the answer while keeping the requested fact fixed.
- A category recommendation is not a measurement of this prompt; the measured result follows.

## 2. Measured result for this prompt

punctuation produced the largest control-adjusted change (+0.0225) among 5 eligible, measured edits within budget 0.10. The next best eligible edit was word_deletion (+0.0105). Preservation evidence: not flagged by the retrospective audit (operator audited by a sample of 5 candidates).

| Field | Result |
|---|---|
| Prompt and category | `QA-001` · Question answering |
| Original prompt | Which physicist received the Nobel Prize in Physics in 1921 for his discovery of the law of the photoelectric effect? |
| Perturbed prompt | Which physicist received the Nobel Prize in Physics in 1921 for his discovery of the law of the photoelectric effect |
| Operator | `punctuation`: `effect?` → `effect` |
| Input change | **1 character edit(s)**, normalised distance **0.0085**, semantic input distance 0.0195 |
| Model and comparison | fixed panel of 5 models, equal weights; 5 matched model–prompt pair(s) from `main_v1` |
| Output change | Semantic distance **0.0225**, mean unchanged control distance **0.0000**, excess distance **+0.0225** |
| Functional result | Qwen 3.8 27B: correct → correct; same final answer; response length 170 → 170 characters; GPT-OSS-120B: correct → correct; same final answer; response length 149 → 149 characters; GPT-OSS-20B: correct → correct; same final answer; response length 48 → 48 characters; ALLaM-2-7B: correct → incorrect; final answer text changed; response length 170 → 170 characters; Gemini 3.1 Flash-Lite: correct → correct; same final answer; response length 204 → 204 characters |
| Tie status | unique |
| Evidence status | Measured retrospectively from stored main_v1 outputs; this prompt belongs to the discovery set that produced the category ranking, so the result is exploratory. |

### Responses of ALLaM-2-7B (largest effect in the panel)

**Original prompt response**

```text
Final answer: Albert Einstein

Albert Einstein is the physicist who received the Nobel Prize in Physics in 1921 for his discovery of the law of the photoelectric effect.
```

**Perturbed prompt response**

```text
The physicist who received the Nobel Prize in Physics in 1921 for discovering the law of the photoelectric effect is Werner Heisenberg. 

Final answer: Werner Heisenberg
```

## 3. All operators

| Operator | Status | Char edits | d_in_char | Raw | Control | Excess | Correctness (before → after) |
|---|---|---:|---:|---:|---:|---:|---|
| `punctuation` **(selected)** | measured | 1 | 0.0085 | 0.0225 | 0.0000 | +0.0225 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→incorrect; Gemini 3.1 Flash-Lite correct→correct |
| `word_deletion` | measured | 4 | 0.0342 | 0.0105 | 0.0000 | +0.0105 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `word_insertion` | measured | 10 | 0.0787 | 0.0055 | 0.0000 | +0.0055 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `capitalization` | measured | 1 | 0.0085 | 0.0006 | 0.0000 | +0.0006 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `char_substitution` | measured | 1 | 0.0085 | 0.0006 | 0.0000 | +0.0006 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `instruction_reordering` | inapplicable: inapplicable_or_no_op |  |  |  |  |  |  |
| `synonym` | inapplicable: inapplicable_or_no_op |  |  |  |  |  |  |
| `whitespace` | over_budget: d_in_char 0.1397 exceeds budget 0.10 | 19 | 0.1397 |  |  |  |  |
| `word_substitution` | inapplicable: inapplicable_or_no_op |  |  |  |  |  |  |

## 4. Input–output trade-off

Eligible edits not dominated by another edit with no more character edits and at least as much excess change:

- `punctuation`: 1 character edit(s) → excess +0.0225

## 5. Source records

Full responses, per-model scores and record IDs are in the JSON file next to this report.

- `qwen/qwen3.8-27b|QA-001|treatment|punctuation|1`: anchor record `fbcff992-b47f-4bea-965a-18c8bac1b645`, comparison record `38b1b013-6de0-4ad7-b805-a748fd9b283f`
- `openai/gpt-oss-120b|QA-001|treatment|punctuation|1`: anchor record `d00f7a81-1bfe-40b1-b33a-dc238e976ded`, comparison record `591e08fc-0327-4a53-b56e-e59be374ad20`
- `openai/gpt-oss-20b|QA-001|treatment|punctuation|1`: anchor record `8fca7e49-f17c-44b2-bdb7-8c7964456505`, comparison record `1c44a109-a16a-4167-8c8a-61363b88a81d`
- `allam-2-7b|QA-001|treatment|punctuation|1`: anchor record `90f727c6-5843-4796-aecf-2aa16de01c72`, comparison record `17d493d6-9fd0-43f8-a56b-59c54086f6bc`
- `gemini-3.1-flash-lite|QA-001|treatment|punctuation|1`: anchor record `fffe0450-0fcd-490a-bd0d-c3adaa563028`, comparison record `58e3537c-1a4d-4e5e-ab50-c6d259448f1f`
