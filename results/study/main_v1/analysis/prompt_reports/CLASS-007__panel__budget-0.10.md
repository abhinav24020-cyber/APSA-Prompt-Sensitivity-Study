# Perturbation operator result: CLASS-007 · Classification

**Status:** `selected` · **Rule:** budget mode, d_in_char ≤ 0.10 · **Model scope:** fixed panel of 5 models, equal weights · **Evidence:** retrospective

## 1. Category recommendation

- Recommended: **synonym** (exploratory (main_v1 discovery ranking); source: category_operator_rankings.csv (classification, budget 0.10))
- Category score 0.0761, coverage 10/10 complete prompts
- Why: Replacing an instruction verb (e.g. Classify -> Categorize) changes the cue used to request a label while preserving the label set and evidence.
- A category recommendation is not a measurement of this prompt; the measured result follows.

## 2. Measured result for this prompt

capitalization produced the largest control-adjusted change (+0.1307) among 6 eligible, measured edits within budget 0.10. The next best eligible edit was punctuation (+0.1068). Preservation evidence: not flagged by the retrospective audit (operator audited by a sample of 5 candidates).

| Field | Result |
|---|---|
| Prompt and category | `CLASS-007` · Classification |
| Original prompt | Given Premise: 'A dog is running in the park chasing a red ball.' and Hypothesis: 'An animal is outside.' Classify the relation as Entailment, Contradiction, or Neutral. |
| Perturbed prompt | given Premise: 'A dog is running in the park chasing a red ball.' and Hypothesis: 'An animal is outside.' Classify the relation as Entailment, Contradiction, or Neutral. |
| Operator | `capitalization`: `Given` → `given` |
| Input change | **1 character edit(s)**, normalised distance **0.0059**, semantic input distance 0.0000 |
| Model and comparison | fixed panel of 5 models, equal weights; 5 matched model–prompt pair(s) from `main_v1` |
| Output change | Semantic distance **0.1363**, mean unchanged control distance **0.0056**, excess distance **+0.1307** |
| Functional result | Qwen 3.8 27B: correct → correct; same final answer; response length 622 → 741 characters; GPT-OSS-120B: correct → correct; same final answer; response length 35 → 35 characters; GPT-OSS-20B: correct → correct; final answer text changed; response length 36 → 10 characters; ALLaM-2-7B: correct → incorrect; final answer text changed; response length 37 → 217 characters; Gemini 3.1 Flash-Lite: correct → correct; same final answer; response length 220 → 220 characters |
| Tie status | unique |
| Evidence status | Measured retrospectively from stored main_v1 outputs; this prompt belongs to the discovery set that produced the category ranking, so the result is exploratory. |

### Responses of ALLaM-2-7B (largest effect in the panel)

**Original prompt response**

```text
Entailment

Final answer: Entailment
```

**Perturbed prompt response**

```text
Premise: 'A dog is running in the park chasing a red ball.'
Hypothesis: 'An animal is outside.'

Classification: Entailment

Final answer: An animal is outside because the premise describes a dog running in the park.
```

## 3. All operators

| Operator | Status | Char edits | d_in_char | Raw | Control | Excess | Correctness (before → after) |
|---|---|---:|---:|---:|---:|---:|---|
| `capitalization` **(selected)** | measured | 1 | 0.0059 | 0.1363 | 0.0056 | +0.1307 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→incorrect; Gemini 3.1 Flash-Lite correct→correct |
| `punctuation` | measured | 1 | 0.0059 | 0.1124 | 0.0056 | +0.1068 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→incorrect; Gemini 3.1 Flash-Lite correct→correct |
| `synonym` | measured | 8 | 0.0468 | 0.0309 | 0.0056 | +0.0253 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `char_substitution` | measured | 1 | 0.0059 | 0.0148 | 0.0056 | +0.0091 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `word_insertion` | measured | 10 | 0.0559 | 0.0141 | 0.0056 | +0.0085 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `word_deletion` | measured | 4 | 0.0237 | 0.0033 | 0.0056 | -0.0024 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `instruction_reordering` | inapplicable: inapplicable_or_no_op |  |  |  |  |  |  |
| `whitespace` | over_budget: d_in_char 0.1333 exceeds budget 0.10 | 26 | 0.1333 |  |  |  |  |
| `word_substitution` | inapplicable: inapplicable_or_no_op |  |  |  |  |  |  |

## 4. Input–output trade-off

Eligible edits not dominated by another edit with no more character edits and at least as much excess change:

- `capitalization`: 1 character edit(s) → excess +0.1307

## 5. Source records

Full responses, per-model scores and record IDs are in the JSON file next to this report.

- `qwen/qwen3.8-27b|CLASS-007|treatment|capitalization|1`: anchor record `50ff82a5-8ede-473c-9344-9a9f3c1073c7`, comparison record `5a2b154b-5155-425a-884b-3b439e5b5ccf`
- `openai/gpt-oss-120b|CLASS-007|treatment|capitalization|1`: anchor record `48d4fee0-33a1-4f71-8c8c-992552fdfeda`, comparison record `fcedbeb9-cc58-4586-a48c-578e3afba055`
- `openai/gpt-oss-20b|CLASS-007|treatment|capitalization|1`: anchor record `3a316b7e-0c8f-48cd-ad6e-5c2b36ef1e52`, comparison record `000c9356-c2fc-40cb-a024-52bc0299fb06`
- `allam-2-7b|CLASS-007|treatment|capitalization|1`: anchor record `c53e6a34-706c-4857-b1cc-25391de4e97c`, comparison record `14b10907-cdcf-410c-8a1b-f4e2ffce0e65`
- `gemini-3.1-flash-lite|CLASS-007|treatment|capitalization|1`: anchor record `22bd8e8e-3d75-45b0-8b4f-64a5c60e047e`, comparison record `ed36751b-eaec-4477-a0f0-e5b75aac0200`
