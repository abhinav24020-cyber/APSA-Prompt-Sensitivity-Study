# Perturbation operator result: CODE-004 · Code generation

**Status:** `selected` · **Rule:** budget mode, d_in_char ≤ 0.10 · **Model scope:** fixed panel of 5 models, equal weights · **Evidence:** retrospective

## 1. Category recommendation

- Recommended: **word_insertion** (exploratory (main_v1 discovery ranking); source: category_operator_rankings.csv (code_generation, budget 0.10))
- Category score 0.0386, coverage 10/10 complete prompts
- Why: A leading tone cue ('Carefully') can change which implementation the model writes while preserving the signature and input/output contract.
- A category recommendation is not a measurement of this prompt; the measured result follows.

## 2. Measured result for this prompt

punctuation produced the largest control-adjusted change (+0.0361) among 6 eligible, measured edits within budget 0.10. The next best eligible edit was word_insertion (+0.0348). Preservation evidence: not flagged by the retrospective audit (operator audited by a sample of 5 candidates).

| Field | Result |
|---|---|
| Prompt and category | `CODE-004` · Code generation |
| Original prompt | Write a Python function fibonacci(n: int) -> list[int] that returns a list of the first n Fibonacci numbers starting with 0, 1. |
| Perturbed prompt | Write a Python function fibonacci(n: int) -> list[int] that returns a list of the first n Fibonacci numbers starting with 0, 1 |
| Operator | `punctuation`: `1.` → `1` |
| Input change | **1 character edit(s)**, normalised distance **0.0079**, semantic input distance 0.0061 |
| Model and comparison | fixed panel of 5 models, equal weights; 5 matched model–prompt pair(s) from `main_v1` |
| Output change | Semantic distance **0.0361**, mean unchanged control distance **0.0000**, excess distance **+0.0361** |
| Functional result | Qwen 3.8 27B: correct → correct (unit tests); response length 212 → 212 characters; GPT-OSS-120B: correct → correct (unit tests); response length 293 → 293 characters; GPT-OSS-20B: correct → correct (unit tests); response length 293 → 293 characters; ALLaM-2-7B: correct → correct (unit tests); response length 452 → 316 characters; Gemini 3.1 Flash-Lite: correct → correct (unit tests); response length 269 → 245 characters |
| Tie status | unique |
| Evidence status | Measured retrospectively from stored main_v1 outputs; this prompt belongs to the discovery set that produced the category ranking, so the result is exploratory. |

### Responses of ALLaM-2-7B (largest effect in the panel)

**Original prompt response**

```text
Sure, here's a Python function that returns a list of the first n Fibonacci numbers starting with 0, 1:

```python
def fibonacci(n: int) -> list[int]:
    fib_list = [0, 1]
    for i in range(2, n):
        fib_list.append(fib_list[-1] + fib_list[-2])
    return fib_list[:n]
```

This function uses a list to store the Fibonacci numbers and a loop to generate the remaining numbers up to n. It returns a list containing the first n Fibonacci numbers.
```

**Perturbed prompt response**

```text
Here's the Python function for calculating the first n Fibonacci numbers starting with 0, 1:

```python
def fibonacci(n: int) -> list[int]:
    fib_list = [0, 1]
    for i in range(2, n):
        fib_list.append(fib_list[-1] + fib_list[-2])
    return fib_list[:n]
```

Final answer: fibonacci(5) -> [0, 1, 1, 2, 3]
```

## 3. All operators

| Operator | Status | Char edits | d_in_char | Raw | Control | Excess | Correctness (before → after) |
|---|---|---:|---:|---:|---:|---:|---|
| `punctuation` **(selected)** | measured | 1 | 0.0079 | 0.0361 | 0.0000 | +0.0361 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `word_insertion` | measured | 10 | 0.0730 | 0.0348 | 0.0000 | +0.0348 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `synonym` | measured | 8 | 0.0625 | 0.0285 | 0.0000 | +0.0285 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `word_substitution` | measured | 3 | 0.0234 | 0.0244 | 0.0000 | +0.0244 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `word_deletion` | measured | 4 | 0.0315 | 0.0023 | 0.0000 | +0.0023 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `capitalization` | measured | 1 | 0.0079 | 0.0009 | 0.0000 | +0.0009 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `char_substitution` | meaning_changing: retrospective audit flag: specification_changed | 1 | 0.0079 |  |  |  |  |
| `instruction_reordering` | inapplicable: inapplicable_or_no_op |  |  |  |  |  |  |
| `whitespace` | over_budget: d_in_char 0.1419 exceeds budget 0.10 | 21 | 0.1419 |  |  |  |  |

## 4. Input–output trade-off

Eligible edits not dominated by another edit with no more character edits and at least as much excess change:

- `punctuation`: 1 character edit(s) → excess +0.0361

## 5. Source records

Full responses, per-model scores and record IDs are in the JSON file next to this report.

- `qwen/qwen3.8-27b|CODE-004|treatment|punctuation|1`: anchor record `18806db7-19a8-4368-8dc4-742015d438f2`, comparison record `87bac9c8-ad5b-49e7-a2e9-73241860a036`
- `openai/gpt-oss-120b|CODE-004|treatment|punctuation|1`: anchor record `07ec6d01-4e0d-4e1d-a442-8e737cc60d51`, comparison record `530362d7-e3b9-4f25-a82a-1f2e7b8c899f`
- `openai/gpt-oss-20b|CODE-004|treatment|punctuation|1`: anchor record `f2ed135e-6492-40cb-b8e7-7f817bb5c100`, comparison record `c1e67a43-770a-4714-b8d9-c1770af15b8a`
- `allam-2-7b|CODE-004|treatment|punctuation|1`: anchor record `9df980fa-cb33-449b-aa7d-2c497f34bd89`, comparison record `d2c198ca-3af9-4ab3-879c-740043e6960d`
- `gemini-3.1-flash-lite|CODE-004|treatment|punctuation|1`: anchor record `5034270f-a99e-4f65-be03-fc3274636c98`, comparison record `1ccf53d0-2859-4ac2-9eac-a479f5e0bebc`
