# Perturbation operator result: CODE-007 · Code generation

**Status:** `selected` · **Rule:** budget mode, d_in_char ≤ 0.10 · **Model scope:** fixed panel of 5 models, equal weights · **Evidence:** retrospective

## 1. Category recommendation

- Recommended: **word_insertion** (exploratory (main_v1 discovery ranking); source: category_operator_rankings.csv (code_generation, budget 0.10))
- Category score 0.0386, coverage 10/10 complete prompts
- Why: A leading tone cue ('Carefully') can change which implementation the model writes while preserving the signature and input/output contract.
- A category recommendation is not a measurement of this prompt; the measured result follows.

## 2. Measured result for this prompt

word_insertion produced the largest control-adjusted change (+0.0878) among 7 eligible, measured edits within budget 0.10. The next best eligible edit was word_substitution (+0.0450). Preservation evidence: not flagged by the retrospective audit (operator audited by a sample of 5 candidates).

| Field | Result |
|---|---|
| Prompt and category | `CODE-007` · Code generation |
| Original prompt | Write a Python function is_anagram(str1: str, str2: str) -> bool that checks if two strings are anagrams of each other (ignoring case and spaces). |
| Perturbed prompt | Carefully Write a Python function is_anagram(str1: str, str2: str) -> bool that checks if two strings are anagrams of each other (ignoring case and spaces). |
| Operator | `word_insertion`: `∅` → `Carefully` |
| Input change | **10 character edit(s)**, normalised distance **0.0641**, semantic input distance 0.0024 |
| Model and comparison | fixed panel of 5 models, equal weights; 5 matched model–prompt pair(s) from `main_v1` |
| Output change | Semantic distance **0.0878**, mean unchanged control distance **0.0000**, excess distance **+0.0878** |
| Functional result | Qwen 3.8 27B: correct → correct (unit tests); response length 173 → 381 characters; GPT-OSS-120B: correct → correct (unit tests); response length 498 → 757 characters; GPT-OSS-20B: correct → correct (unit tests); response length 323 → 352 characters; ALLaM-2-7B: correct → correct (unit tests); response length 718 → 811 characters; Gemini 3.1 Flash-Lite: correct → correct (unit tests); response length 173 → 355 characters |
| Tie status | unique |
| Evidence status | Measured retrospectively from stored main_v1 outputs; this prompt belongs to the discovery set that produced the category ranking, so the result is exploratory. |

### Responses of Qwen 3.8 27B (largest effect in the panel)

**Original prompt response**

```text
```python
def is_anagram(str1: str, str2: str) -> bool:
    s1 = ''.join(str1.lower().split())
    s2 = ''.join(str2.lower().split())
    return sorted(s1) == sorted(s2)
```
```

**Perturbed prompt response**

```text
```python
def is_anagram(str1: str, str2: str) -> bool:
    # Remove spaces and convert to lowercase
    s1 = str1.replace(" ", "").lower()
    s2 = str2.replace(" ", "").lower()
    
    # Check if lengths are equal
    if len(s1) != len(s2):
        return False
    
    # Count character frequencies
    from collections import Counter
    return Counter(s1) == Counter(s2)
```
```

## 3. All operators

| Operator | Status | Char edits | d_in_char | Raw | Control | Excess | Correctness (before → after) |
|---|---|---:|---:|---:|---:|---:|---|
| `word_insertion` **(selected)** | measured | 10 | 0.0641 | 0.0878 | 0.0000 | +0.0878 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `word_substitution` | measured | 3 | 0.0204 | 0.0450 | 0.0000 | +0.0450 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `synonym` | measured | 8 | 0.0544 | 0.0437 | 0.0000 | +0.0437 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `word_deletion` | measured | 2 | 0.0137 | 0.0342 | 0.0000 | +0.0342 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `capitalization` | measured | 1 | 0.0068 | 0.0323 | 0.0000 | +0.0323 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `char_substitution` | measured | 1 | 0.0068 | 0.0233 | 0.0000 | +0.0233 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `punctuation` | measured | 1 | 0.0068 | 0.0049 | 0.0000 | +0.0049 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `instruction_reordering` | inapplicable: inapplicable_or_no_op |  |  |  |  |  |  |
| `whitespace` | over_budget: d_in_char 0.1361 exceeds budget 0.10 | 23 | 0.1361 |  |  |  |  |

## 4. Input–output trade-off

Eligible edits not dominated by another edit with no more character edits and at least as much excess change:

- `capitalization`: 1 character edit(s) → excess +0.0323
- `word_deletion`: 2 character edit(s) → excess +0.0342
- `word_substitution`: 3 character edit(s) → excess +0.0450
- `word_insertion`: 10 character edit(s) → excess +0.0878

## 5. Source records

Full responses, per-model scores and record IDs are in the JSON file next to this report.

- `qwen/qwen3.8-27b|CODE-007|treatment|word_insertion|1`: anchor record `3f88280a-7fcc-4b8d-b006-db7ee0f8d34d`, comparison record `659b1044-5501-408b-9330-6673423ffa61`
- `openai/gpt-oss-120b|CODE-007|treatment|word_insertion|1`: anchor record `28712c54-7149-4217-9293-366708033bdf`, comparison record `b85f136c-a401-4333-a272-da8d254a37a3`
- `openai/gpt-oss-20b|CODE-007|treatment|word_insertion|1`: anchor record `c1bbb698-452c-4f27-96a2-fb85936cbe15`, comparison record `5d8d04f2-f564-4dd9-b64b-bbb04b82d0f7`
- `allam-2-7b|CODE-007|treatment|word_insertion|1`: anchor record `7515a7b9-bc6c-43ce-91b7-745f13f6af59`, comparison record `bd6a45d7-76a7-4a76-a17a-c917a314552e`
- `gemini-3.1-flash-lite|CODE-007|treatment|word_insertion|1`: anchor record `9724d82a-8000-4190-ac55-49f3bc0f1afb`, comparison record `47f01d75-d2e5-4dd0-a9ee-5cf6059a5378`
