# Perturbation operator result: CLASS-006 · Classification

**Status:** `selected` · **Rule:** budget mode, d_in_char ≤ 0.10 · **Model scope:** fixed panel of 5 models, equal weights · **Evidence:** retrospective

## 1. Category recommendation

- Recommended: **synonym** (exploratory (main_v1 discovery ranking); source: category_operator_rankings.csv (classification, budget 0.10))
- Category score 0.0761, coverage 10/10 complete prompts
- Why: Replacing an instruction verb (e.g. Classify -> Categorize) changes the cue used to request a label while preserving the label set and evidence.
- A category recommendation is not a measurement of this prompt; the measured result follows.

## 2. Measured result for this prompt

word_substitution produced the largest control-adjusted change (+0.0965) among 7 eligible, measured edits within budget 0.10. The next best eligible edit was punctuation (+0.0422). Preservation evidence: not flagged by the retrospective audit (every candidate of this operator was audited).

| Field | Result |
|---|---|
| Prompt and category | `CLASS-006` · Classification |
| Original prompt | Identify the language of the text: 'El desarrollo de la inteligencia artificial avanza a un ritmo acelerado en todo el mundo.' |
| Perturbed prompt | Detect the language of the text: 'El desarrollo de la inteligencia artificial avanza a un ritmo acelerado en todo el mundo.' |
| Operator | `word_substitution`: `Identify` → `Detect` |
| Input change | **6 character edit(s)**, normalised distance **0.0476**, semantic input distance 0.1201 |
| Model and comparison | fixed panel of 5 models, equal weights; 5 matched model–prompt pair(s) from `main_v1` |
| Output change | Semantic distance **0.0965**, mean unchanged control distance **0.0000**, excess distance **+0.0965** |
| Functional result | Qwen 3.8 27B: correct → correct; same final answer; response length 334 → 376 characters; GPT-OSS-120B: correct → correct; same final answer; response length 21 → 21 characters; GPT-OSS-20B: correct → correct; same final answer; response length 21 → 30 characters; ALLaM-2-7B: correct → correct; same final answer; response length 60 → 454 characters; Gemini 3.1 Flash-Lite: correct → correct; same final answer; response length 59 → 59 characters |
| Tie status | unique |
| Evidence status | Measured retrospectively from stored main_v1 outputs; this prompt belongs to the discovery set that produced the category ranking, so the result is exploratory. |

### Responses of ALLaM-2-7B (largest effect in the panel)

**Original prompt response**

```text
The language of the text is Spanish.

Final answer: Spanish
```

**Perturbed prompt response**

```text
To detect the language of the given text, I will use the langdetect library in Python. Please install the library if you haven't already:

```python
pip install langdetect
```

Now, let's identify the language:

```python
from langdetect import detect

text = 'El desarrollo de la inteligencia artificial avanza a un ritmo acelerado en todo el mundo.'
language = detect(text)

print(f'The language of the text is: {language}')
```

Final answer: Spanish
```

## 3. All operators

| Operator | Status | Char edits | d_in_char | Raw | Control | Excess | Correctness (before → after) |
|---|---|---:|---:|---:|---:|---:|---|
| `word_substitution` **(selected)** | measured | 6 | 0.0476 | 0.0965 | 0.0000 | +0.0965 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `punctuation` | measured | 1 | 0.0079 | 0.0422 | 0.0000 | +0.0422 | Qwen 3.8 27B correct→incorrect; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `capitalization` | measured | 1 | 0.0079 | 0.0336 | 0.0000 | +0.0336 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `word_insertion` | measured | 10 | 0.0735 | 0.0336 | 0.0000 | +0.0336 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `char_substitution` | measured | 1 | 0.0079 | 0.0199 | 0.0000 | +0.0199 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `word_deletion` | measured | 4 | 0.0317 | 0.0079 | 0.0000 | +0.0079 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `synonym` | measured | 8 | 0.0630 | 0.0018 | 0.0000 | +0.0018 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `instruction_reordering` | inapplicable: inapplicable_or_no_op |  |  |  |  |  |  |
| `whitespace` | over_budget: d_in_char 0.1370 exceeds budget 0.10 | 20 | 0.1370 |  |  |  |  |

## 4. Input–output trade-off

Eligible edits not dominated by another edit with no more character edits and at least as much excess change:

- `punctuation`: 1 character edit(s) → excess +0.0422
- `word_substitution`: 6 character edit(s) → excess +0.0965

## 5. Source records

Full responses, per-model scores and record IDs are in the JSON file next to this report.

- `qwen/qwen3.8-27b|CLASS-006|treatment|word_substitution|1`: anchor record `4f420fe4-c589-4cc1-90fa-45a24ec3b300`, comparison record `4c4da49a-3710-42ba-96aa-d0332c262156`
- `openai/gpt-oss-120b|CLASS-006|treatment|word_substitution|1`: anchor record `195668be-c8cc-4f86-9221-25a1cf9d86d8`, comparison record `79c49031-b9a4-4f07-9d69-8878eb46c82f`
- `openai/gpt-oss-20b|CLASS-006|treatment|word_substitution|1`: anchor record `7e874bd1-2858-4fbe-b90f-efe32a9838f4`, comparison record `911b7147-070d-491d-b119-3e06beb7f187`
- `allam-2-7b|CLASS-006|treatment|word_substitution|1`: anchor record `b8b59554-7b10-4314-8fc8-ac8f6c119d9d`, comparison record `19728ae3-fb0d-4547-be0d-154941fd516d`
- `gemini-3.1-flash-lite|CLASS-006|treatment|word_substitution|1`: anchor record `f2b41e95-acd0-4da0-8d0a-d0d0ad0b4bfa`, comparison record `4f1023a6-d0f5-4f39-873b-a4abe59ccb3a`
