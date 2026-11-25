# Perturbation operator result: CODE-009 · Code generation

**Status:** `selected` · **Rule:** budget mode, d_in_char ≤ 0.10 · **Model scope:** fixed panel of 5 models, equal weights · **Evidence:** retrospective

## 1. Category recommendation

- Recommended: **word_insertion** (exploratory (main_v1 discovery ranking); source: category_operator_rankings.csv (code_generation, budget 0.10))
- Category score 0.0386, coverage 10/10 complete prompts
- Why: A leading tone cue ('Carefully') can change which implementation the model writes while preserving the signature and input/output contract.
- A category recommendation is not a measurement of this prompt; the measured result follows.

## 2. Measured result for this prompt

synonym produced the largest control-adjusted change (+0.0358) among 7 eligible, measured edits within budget 0.10. The next best eligible edit was capitalization (+0.0177). Preservation evidence: not flagged by the retrospective audit (every candidate of this operator was audited).

| Field | Result |
|---|---|
| Prompt and category | `CODE-009` · Code generation |
| Original prompt | Write a Python function binary_search(arr: list[int], target: int) -> int that returns the index of target in a sorted list arr, or -1 if target is not present. |
| Perturbed prompt | Write a Python procedure binary_search(arr: list[int], target: int) -> int that returns the index of target in a sorted list arr, or -1 if target is not present. |
| Operator | `synonym`: `function` → `procedure` |
| Input change | **8 character edit(s)**, normalised distance **0.0497**, semantic input distance 0.0202 |
| Model and comparison | fixed panel of 5 models, equal weights; 5 matched model–prompt pair(s) from `main_v1` |
| Output change | Semantic distance **0.0358**, mean unchanged control distance **0.0000**, excess distance **+0.0358** |
| Functional result | Qwen 3.8 27B: correct → correct (unit tests); response length 330 → 330 characters; GPT-OSS-120B: correct → correct (unit tests); response length 407 → 407 characters; GPT-OSS-20B: correct → correct (unit tests); response length 364 → 330 characters; ALLaM-2-7B: correct → correct (unit tests); response length 557 → 578 characters; Gemini 3.1 Flash-Lite: correct → correct (unit tests); response length 344 → 518 characters |
| Tie status | unique |
| Evidence status | Measured retrospectively from stored main_v1 outputs; this prompt belongs to the discovery set that produced the category ranking, so the result is exploratory. |

### Responses of Gemini 3.1 Flash-Lite (largest effect in the panel)

**Original prompt response**

```text
```python
def binary_search(arr: list[int], target: int) -> int:
    low = 0
    high = len(arr) - 1
    
    while low <= high:
        mid = (low + high) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
            
    return -1
```
```

**Perturbed prompt response**

```text
```python
def binary_search(arr: list[int], target: int) -> int:
    low = 0
    high = len(arr) - 1
    
    while low <= high:
        mid = (low + high) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
            
    return -1
```

Final answer: The provided Python code implements the binary search algorithm to find the index of a target value in a sorted list, returning -1 if the target is not found.
```

## 3. All operators

| Operator | Status | Char edits | d_in_char | Raw | Control | Excess | Correctness (before → after) |
|---|---|---:|---:|---:|---:|---:|---|
| `synonym` **(selected)** | measured | 8 | 0.0497 | 0.0358 | 0.0000 | +0.0358 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `capitalization` | measured | 1 | 0.0063 | 0.0177 | 0.0000 | +0.0177 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `word_substitution` | measured | 3 | 0.0186 | 0.0175 | 0.0000 | +0.0175 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `char_substitution` | measured | 1 | 0.0063 | 0.0162 | 0.0000 | +0.0162 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `word_deletion` | measured | 4 | 0.0250 | 0.0151 | 0.0000 | +0.0151 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `word_insertion` | measured | 10 | 0.0588 | 0.0146 | 0.0000 | +0.0146 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `punctuation` | measured | 1 | 0.0063 | 0.0116 | 0.0000 | +0.0116 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `instruction_reordering` | inapplicable: inapplicable_or_no_op |  |  |  |  |  |  |
| `whitespace` | over_budget: d_in_char 0.1444 exceeds budget 0.10 | 27 | 0.1444 |  |  |  |  |

## 4. Input–output trade-off

Eligible edits not dominated by another edit with no more character edits and at least as much excess change:

- `capitalization`: 1 character edit(s) → excess +0.0177
- `synonym`: 8 character edit(s) → excess +0.0358

## 5. Source records

Full responses, per-model scores and record IDs are in the JSON file next to this report.

- `qwen/qwen3.8-27b|CODE-009|treatment|synonym|1`: anchor record `b04d8c2c-e9cf-44fa-98ae-0c049a1d9f3c`, comparison record `b57b1de0-285b-48a8-b5bc-b4b16af22c09`
- `openai/gpt-oss-120b|CODE-009|treatment|synonym|1`: anchor record `c3ee6e3f-85f8-4c1f-bd9b-c5b362e21e0a`, comparison record `281de85b-d0d8-45e9-9e03-11d9da033ce7`
- `openai/gpt-oss-20b|CODE-009|treatment|synonym|1`: anchor record `82cc1cd3-3c53-46e9-9de9-e49064af850b`, comparison record `a20f8f08-9289-4233-ace0-a75c49770e5e`
- `allam-2-7b|CODE-009|treatment|synonym|1`: anchor record `6bfa157e-04ac-4bc5-b437-b2772e60e08d`, comparison record `669d1715-99a3-44c5-b0da-6204e2177ac6`
- `gemini-3.1-flash-lite|CODE-009|treatment|synonym|1`: anchor record `bb45c834-2b36-4da2-bf19-b8b5f06a1349`, comparison record `79fae363-04a4-4901-89cf-830498de5ef6`
