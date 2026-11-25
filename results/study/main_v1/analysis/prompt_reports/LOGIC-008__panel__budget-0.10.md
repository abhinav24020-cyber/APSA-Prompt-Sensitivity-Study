# Perturbation operator result: LOGIC-008 · Logical reasoning

**Status:** `selected` · **Rule:** budget mode, d_in_char ≤ 0.10 · **Model scope:** fixed panel of 5 models, equal weights · **Evidence:** retrospective

## 1. Category recommendation

- Recommended: **punctuation** (exploratory (main_v1 discovery ranking); source: category_operator_rankings.csv (logical_reasoning, budget 0.10))
- Category score 0.0744, coverage 9/9 complete prompts
- Why: A terminal punctuation edit changes the cue at the end of the prompt while leaving premises and the requested conclusion intact.
- A category recommendation is not a measurement of this prompt; the measured result follows.

## 2. Measured result for this prompt

word_insertion produced the largest control-adjusted change (+0.0262) among 5 eligible, measured edits within budget 0.10. The next best eligible edit was capitalization (+0.0221). Preservation evidence: not flagged by the retrospective audit (operator audited by a sample of 5 candidates).

| Field | Result |
|---|---|
| Prompt and category | `LOGIC-008` · Logical reasoning |
| Original prompt | Three people (Anna, Brian, Clara) own three different pets (Dog, Cat, Fish). Anna is allergic to fur. Brian does not own a fish. Clara does not own the dog. Who owns which pet? |
| Perturbed prompt | Carefully Three people (Anna, Brian, Clara) own three different pets (Dog, Cat, Fish). Anna is allergic to fur. Brian does not own a fish. Clara does not own the dog. Who owns which pet? |
| Operator | `word_insertion`: `∅` → `Carefully` |
| Input change | **10 character edit(s)**, normalised distance **0.0538**, semantic input distance 0.0050 |
| Model and comparison | fixed panel of 5 models, equal weights; 5 matched model–prompt pair(s) from `main_v1` |
| Output change | Semantic distance **0.0262**, mean unchanged control distance **0.0000**, excess distance **+0.0262** |
| Functional result | Qwen 3.8 27B: correct → correct; same final answer; response length 1400 → 1409 characters; GPT-OSS-120B: correct → correct; same final answer; response length 95 → 95 characters; GPT-OSS-20B: correct → correct; final answer text changed; response length 111 → 117 characters; ALLaM-2-7B: incorrect → incorrect; final answer text changed; response length 525 → 644 characters; Gemini 3.1 Flash-Lite: correct → correct; same final answer; response length 433 → 342 characters |
| Tie status | unique |
| Evidence status | Measured retrospectively from stored main_v1 outputs; this prompt belongs to the discovery set that produced the category ranking, so the result is exploratory. |

### Responses of ALLaM-2-7B (largest effect in the panel)

**Original prompt response**

```text
To determine who owns which pet, let's use logical deduction based on the information provided:

1. Anna is allergic to fur.
2. Brian does not own a fish.
3. Clara does not own the dog.

Let's assign pets to each person:
A = Anna, B = Brian, C = Clara

Since Anna is allergic to fur, she can't own a dog. Therefore, she must own a cat (C).
Since Brian does not own a fish, he must own a dog (B).
Since Clara does not own the dog, she must own a fish (C).

Final answer: Anna has a cat, Brian has a dog, and Clara has a fish.
```

**Perturbed prompt response**

```text
To determine who owns which pet, let's use the given information:

1. Anna has a pet that is not a fish.
2. Brian does not own a fish.
3. Clara does not own the dog.

Now let's analyze the pets:

Anna has a pet that is not a fish, so she has either a cat or a fish. Since she is allergic to fur, she must have a fish.

Brian does not own a fish, so he must have a cat or a fish. Since we know Anna has a fish, Brian must have the cat.

Clara does not own the dog, so she must have a fish or a cat. Since we know Anna has a fish and Brian has a cat, Clara must have the dog.

Final answer: Anna has a fish, Brian has a cat, and Clara has a dog.
```

## 3. All operators

| Operator | Status | Char edits | d_in_char | Raw | Control | Excess | Correctness (before → after) |
|---|---|---:|---:|---:|---:|---:|---|
| `word_insertion` **(selected)** | measured | 10 | 0.0538 | 0.0262 | 0.0000 | +0.0262 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→incorrect; Gemini 3.1 Flash-Lite correct→correct |
| `capitalization` | measured | 1 | 0.0057 | 0.0221 | 0.0000 | +0.0221 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→incorrect; Gemini 3.1 Flash-Lite correct→correct |
| `char_substitution` | measured | 1 | 0.0057 | 0.0128 | 0.0000 | +0.0128 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→correct; Gemini 3.1 Flash-Lite correct→correct |
| `word_deletion` | measured | 4 | 0.0227 | 0.0099 | 0.0000 | +0.0099 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→incorrect; Gemini 3.1 Flash-Lite correct→correct |
| `punctuation` | measured | 1 | 0.0057 | 0.0069 | 0.0000 | +0.0069 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→incorrect; Gemini 3.1 Flash-Lite correct→correct |
| `instruction_reordering` | over_budget: d_in_char 0.2273 exceeds budget 0.10 | 40 | 0.2273 |  |  |  |  |
| `synonym` | inapplicable: inapplicable_or_no_op |  |  |  |  |  |  |
| `whitespace` | over_budget: d_in_char 0.1538 exceeds budget 0.10 | 32 | 0.1538 |  |  |  |  |
| `word_substitution` | inapplicable: inapplicable_or_no_op |  |  |  |  |  |  |

## 4. Input–output trade-off

Eligible edits not dominated by another edit with no more character edits and at least as much excess change:

- `capitalization`: 1 character edit(s) → excess +0.0221
- `word_insertion`: 10 character edit(s) → excess +0.0262

## 5. Source records

Full responses, per-model scores and record IDs are in the JSON file next to this report.

- `qwen/qwen3.8-27b|LOGIC-008|treatment|word_insertion|1`: anchor record `175c0fe3-7bd9-4b37-960a-cd5a1db4c6aa`, comparison record `525788f4-66b7-471c-9a0c-977d4d299cee`
- `openai/gpt-oss-120b|LOGIC-008|treatment|word_insertion|1`: anchor record `d15e392e-4a79-4be9-8de0-261a5f01a019`, comparison record `3f906ef2-9bf4-46e6-a142-de1e526a992a`
- `openai/gpt-oss-20b|LOGIC-008|treatment|word_insertion|1`: anchor record `be43cc2b-2e21-4e03-a549-d311f3cf4ced`, comparison record `2194529b-65a5-481a-bee1-3f4bb58e6f73`
- `allam-2-7b|LOGIC-008|treatment|word_insertion|1`: anchor record `082c65c6-cfd0-41de-a6ce-b72934443806`, comparison record `310db93d-b7eb-47c4-9600-8af8633f5898`
- `gemini-3.1-flash-lite|LOGIC-008|treatment|word_insertion|1`: anchor record `5b700713-9cea-45a4-8f3f-7c47d27a515a`, comparison record `95ef9adb-ea11-4b92-9c3a-40ddb3e1e45d`
