# Perturbation operator result: CODE-006 · Code generation

**Status:** `selected` · **Rule:** budget mode, d_in_char ≤ 0.10 · **Model scope:** fixed panel of 5 models, equal weights · **Evidence:** retrospective

## 1. Category recommendation

- Recommended: **word_insertion** (exploratory (main_v1 discovery ranking); source: category_operator_rankings.csv (code_generation, budget 0.10))
- Category score 0.0386, coverage 10/10 complete prompts
- Why: A leading tone cue ('Carefully') can change which implementation the model writes while preserving the signature and input/output contract.
- A category recommendation is not a measurement of this prompt; the measured result follows.

## 2. Measured result for this prompt

char_substitution produced the largest control-adjusted change (+0.0202) among 7 eligible, measured edits within budget 0.10. The next best eligible edit was word_deletion (+0.0140). Preservation evidence: not flagged by the retrospective audit (every candidate of this operator was audited).

| Field | Result |
|---|---|
| Prompt and category | `CODE-006` · Code generation |
| Original prompt | Write a Python function merge_sorted(arr1: list[int], arr2: list[int]) -> list[int] that merges two sorted lists into one sorted list in O(n + m) time. |
| Perturbed prompt | Write a Python function merge_sorted(arr1: 1ist[int], arr2: list[int]) -> list[int] that merges two sorted lists into one sorted list in O(n + m) time. |
| Operator | `char_substitution`: `list[int],` → `1ist[int],` |
| Input change | **1 character edit(s)**, normalised distance **0.0066**, semantic input distance 0.0173 |
| Model and comparison | fixed panel of 5 models, equal weights; 5 matched model–prompt pair(s) from `main_v1` |
| Output change | Semantic distance **0.0202**, mean unchanged control distance **0.0000**, excess distance **+0.0202** |
| Functional result | Qwen 3.8 27B: correct → correct (unit tests); response length 412 → 412 characters; GPT-OSS-120B: correct → correct (unit tests); response length 566 → 566 characters; GPT-OSS-20B: correct → correct (unit tests); response length 540 → 540 characters; ALLaM-2-7B: incorrect → incorrect (unit tests); response length 418 → 416 characters; Gemini 3.1 Flash-Lite: correct → correct (unit tests); response length 403 → 497 characters |
| Tie status | unique |
| Evidence status | Measured retrospectively from stored main_v1 outputs; this prompt belongs to the discovery set that produced the category ranking, so the result is exploratory. |

### Responses of Gemini 3.1 Flash-Lite (largest effect in the panel)

**Original prompt response**

```text
```python
def merge_sorted(arr1: list[int], arr2: list[int]) -> list[int]:
    merged = []
    i, j = 0, 0
    
    while i < len(arr1) and j < len(arr2):
        if arr1[i] <= arr2[j]:
            merged.append(arr1[i])
            i += 1
        else:
            merged.append(arr2[j])
            j += 1
            
    merged.extend(arr1[i:])
    merged.extend(arr2[j:])
    
    return merged
```
```

**Perturbed prompt response**

```text
```python
def merge_sorted(arr1: list[int], arr2: list[int]) -> list[int]:
    merged = []
    i, j = 0, 0
    while i < len(arr1) and j < len(arr2):
        if arr1[i] < arr2[j]:
            merged.append(arr1[i])
            i += 1
        else:
            merged.append(arr2[j])
            j += 1
    merged.extend(arr1[i:])
    merged.extend(arr2[j:])
    return merged
```

Final answer: The provided Python function merges two sorted lists in O(n + m) time using the two-pointer technique.
```

## 3. All operators

| Operator | Status | Char edits | d_in_char | Raw | Control | Excess | Correctness (before → after) |
|---|---|---:|---:|---:|---:|---:|---|
| `char_substitution` **(selected)** | measured | 1 | 0.0066 | 0.0202 | 0.0000 | +0.0202 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→incorrect; Gemini 3.1 Flash-Lite correct→correct |
| `word_deletion` | measured | 2 | 0.0132 | 0.0140 | 0.0000 | +0.0140 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→incorrect; Gemini 3.1 Flash-Lite correct→correct |
| `word_substitution` | measured | 3 | 0.0197 | 0.0124 | 0.0000 | +0.0124 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→incorrect; Gemini 3.1 Flash-Lite correct→correct |
| `word_insertion` | measured | 10 | 0.0621 | 0.0064 | 0.0000 | +0.0064 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→incorrect; Gemini 3.1 Flash-Lite correct→correct |
| `synonym` | measured | 8 | 0.0516 | 0.0006 | 0.0000 | +0.0006 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→incorrect; Gemini 3.1 Flash-Lite correct→correct |
| `capitalization` | measured | 1 | 0.0066 | 0.0001 | 0.0000 | +0.0001 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→incorrect; Gemini 3.1 Flash-Lite correct→correct |
| `punctuation` | measured | 1 | 0.0066 | 0.0001 | 0.0000 | +0.0001 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→incorrect; Gemini 3.1 Flash-Lite correct→correct |
| `instruction_reordering` | inapplicable: inapplicable_or_no_op |  |  |  |  |  |  |
| `whitespace` | over_budget: d_in_char 0.1322 exceeds budget 0.10 | 23 | 0.1322 |  |  |  |  |

## 4. Input–output trade-off

Eligible edits not dominated by another edit with no more character edits and at least as much excess change:

- `char_substitution`: 1 character edit(s) → excess +0.0202

## 5. Source records

Full responses, per-model scores and record IDs are in the JSON file next to this report.

- `qwen/qwen3.8-27b|CODE-006|treatment|char_substitution|1`: anchor record `e227be65-2ceb-4f61-8b59-63d4f1d0cb68`, comparison record `6b549a03-fbad-48ba-89d7-90565be2291d`
- `openai/gpt-oss-120b|CODE-006|treatment|char_substitution|1`: anchor record `245e5bd2-18fb-4dd8-a615-7cb93a9e3201`, comparison record `753da23e-e1d6-4af2-9330-47e9befa3259`
- `openai/gpt-oss-20b|CODE-006|treatment|char_substitution|1`: anchor record `f5a80942-11d1-423b-aae1-a3f6c286ab83`, comparison record `148f9e46-ea4f-4633-a274-22c7c5bd1bf7`
- `allam-2-7b|CODE-006|treatment|char_substitution|1`: anchor record `bb468a49-e109-49e8-aec4-64cc7fc75270`, comparison record `574346ab-bd8b-4075-9ede-5931fb3ff11e`
- `gemini-3.1-flash-lite|CODE-006|treatment|char_substitution|1`: anchor record `8317f146-deb1-4187-8521-362b7dce8d3b`, comparison record `ef773fa1-5d61-4187-8b0a-e4882a6df2c4`
