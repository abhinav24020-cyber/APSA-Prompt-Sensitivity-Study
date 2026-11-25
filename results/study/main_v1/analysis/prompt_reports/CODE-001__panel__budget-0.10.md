# Perturbation operator result: CODE-001 · Code generation

**Status:** `selected` · **Rule:** budget mode, d_in_char ≤ 0.10 · **Model scope:** fixed panel of 5 models, equal weights · **Evidence:** retrospective

## 1. Category recommendation

- Recommended: **word_insertion** (exploratory (main_v1 discovery ranking); source: category_operator_rankings.csv (code_generation, budget 0.10))
- Category score 0.0386, coverage 10/10 complete prompts
- Why: A leading tone cue ('Carefully') can change which implementation the model writes while preserving the signature and input/output contract.
- A category recommendation is not a measurement of this prompt; the measured result follows.

## 2. Measured result for this prompt

word_insertion produced the largest control-adjusted change (+0.0303) among 6 eligible, measured edits within budget 0.10. The next best eligible edit was word_deletion (+0.0221). Preservation evidence: not flagged by the retrospective audit (operator audited by a sample of 5 candidates).

| Field | Result |
|---|---|
| Prompt and category | `CODE-001` · Code generation |
| Original prompt | Write a Python function reverse_string(s: str) -> str that returns the reversed string without using Python's built-in slice step [::-1] or reversed(). |
| Perturbed prompt | Carefully Write a Python function reverse_string(s: str) -> str that returns the reversed string without using Python's built-in slice step [::-1] or reversed(). |
| Operator | `word_insertion`: `∅` → `Carefully` |
| Input change | **10 character edit(s)**, normalised distance **0.0621**, semantic input distance 0.0058 |
| Model and comparison | fixed panel of 5 models, equal weights; 5 matched model–prompt pair(s) from `main_v1` |
| Output change | Semantic distance **0.0303**, mean unchanged control distance **0.0000**, excess distance **+0.0303** |
| Functional result | Qwen 3.8 27B: correct → correct (unit tests); response length 159 → 159 characters; GPT-OSS-120B: correct → correct (unit tests); response length 508 → 591 characters; GPT-OSS-20B: correct → correct (unit tests); response length 236 → 259 characters; ALLaM-2-7B: incorrect → correct (unit tests); final answer text changed; response length 445 → 464 characters; Gemini 3.1 Flash-Lite: correct → correct (unit tests); response length 324 → 322 characters |
| Tie status | unique |
| Evidence status | Measured retrospectively from stored main_v1 outputs; this prompt belongs to the discovery set that produced the category ranking, so the result is exploratory. |

### Responses of GPT-OSS-20B (largest effect in the panel)

**Original prompt response**

```text
```python
def reverse_string(s: str) -> str:
    """Return the reversed string without using slice step or reversed()."""
    result = []
    for i in range(len(s) - 1, -1, -1):
        result.append(s[i])
    return ''.join(result)
```
```

**Perturbed prompt response**

```text
```python
def reverse_string(s: str) -> str:
    """
    Return the reversed string of `s` without using slicing or reversed().
    """
    result = []
    for char in s:
        result.insert(0, char)   # prepend each character
    return ''.join(result)
```
```

## 3. All operators

| Operator | Status | Char edits | d_in_char | Raw | Control | Excess | Correctness (before → after) |
|---|---|---:|---:|---:|---:|---:|---|
| `word_insertion` **(selected)** | measured | 10 | 0.0621 | 0.0303 | 0.0000 | +0.0303 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→correct; Gemini 3.1 Flash-Lite correct→correct |
| `word_deletion` | measured | 4 | 0.0265 | 0.0221 | 0.0000 | +0.0221 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→incorrect; Gemini 3.1 Flash-Lite correct→correct |
| `word_substitution` | measured | 3 | 0.0197 | 0.0177 | 0.0000 | +0.0177 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→correct; Gemini 3.1 Flash-Lite correct→correct |
| `capitalization` | measured | 1 | 0.0066 | 0.0148 | 0.0000 | +0.0148 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→incorrect; Gemini 3.1 Flash-Lite correct→correct |
| `synonym` | measured | 8 | 0.0526 | 0.0134 | 0.0000 | +0.0134 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→incorrect; Gemini 3.1 Flash-Lite correct→correct |
| `punctuation` | measured | 1 | 0.0066 | 0.0128 | 0.0000 | +0.0128 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→correct; Gemini 3.1 Flash-Lite correct→correct |
| `char_substitution` | meaning_changing: retrospective audit flag: specification_changed | 1 | 0.0066 |  |  |  |  |
| `instruction_reordering` | inapplicable: inapplicable_or_no_op |  |  |  |  |  |  |
| `whitespace` | over_budget: d_in_char 0.1221 exceeds budget 0.10 | 21 | 0.1221 |  |  |  |  |

## 4. Input–output trade-off

Eligible edits not dominated by another edit with no more character edits and at least as much excess change:

- `capitalization`: 1 character edit(s) → excess +0.0148
- `word_substitution`: 3 character edit(s) → excess +0.0177
- `word_deletion`: 4 character edit(s) → excess +0.0221
- `word_insertion`: 10 character edit(s) → excess +0.0303

## 5. Source records

Full responses, per-model scores and record IDs are in the JSON file next to this report.

- `qwen/qwen3.8-27b|CODE-001|treatment|word_insertion|1`: anchor record `648567a3-f571-475c-b934-2514a38e4b06`, comparison record `30b4dc48-5559-4078-ba48-0ed965558786`
- `openai/gpt-oss-120b|CODE-001|treatment|word_insertion|1`: anchor record `8dbece3c-325a-4d7a-adc0-732f31e3d967`, comparison record `2856c44b-5f84-401e-b5dd-91633bb002ef`
- `openai/gpt-oss-20b|CODE-001|treatment|word_insertion|1`: anchor record `c4650085-bde3-4c81-9829-f5a904a83849`, comparison record `33623588-63cb-430d-a889-1b7af616a6b8`
- `allam-2-7b|CODE-001|treatment|word_insertion|1`: anchor record `fd208254-bc03-4861-87b4-c372ac461843`, comparison record `a0d3ffb9-0778-4cd9-8ef7-00324005b48c`
- `gemini-3.1-flash-lite|CODE-001|treatment|word_insertion|1`: anchor record `497d5459-2c55-46d8-9b75-fb92cce9babe`, comparison record `87a5b4db-2f75-45dc-baab-2acbdf04a7e2`
