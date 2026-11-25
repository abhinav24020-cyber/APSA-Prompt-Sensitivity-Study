# Perturbation operator result: CODE-003 · Code generation

**Status:** `selected` · **Rule:** budget mode, d_in_char ≤ 0.10 · **Model scope:** fixed panel of 5 models, equal weights · **Evidence:** retrospective

## 1. Category recommendation

- Recommended: **word_insertion** (exploratory (main_v1 discovery ranking); source: category_operator_rankings.csv (code_generation, budget 0.10))
- Category score 0.0386, coverage 10/10 complete prompts
- Why: A leading tone cue ('Carefully') can change which implementation the model writes while preserving the signature and input/output contract.
- A category recommendation is not a measurement of this prompt; the measured result follows.

## 2. Measured result for this prompt

char_substitution produced the largest control-adjusted change (+0.0986) among 7 eligible, measured edits within budget 0.10. The next best eligible edit was word_insertion (+0.0376). Preservation evidence: not flagged by the retrospective audit (every candidate of this operator was audited).

| Field | Result |
|---|---|
| Prompt and category | `CODE-003` · Code generation |
| Original prompt | Write a Python function flatten_list(nested: list) -> list that recursively flattens an arbitrarily nested list of integers into a single flat list. |
| Perturbed prompt | Write a Python function flatten_list(n3sted: list) -> list that recursively flattens an arbitrarily nested list of integers into a single flat list. |
| Operator | `char_substitution`: `flatten_list(nested:` → `flatten_list(n3sted:` |
| Input change | **1 character edit(s)**, normalised distance **0.0068**, semantic input distance 0.0583 |
| Model and comparison | fixed panel of 5 models, equal weights; 5 matched model–prompt pair(s) from `main_v1` |
| Output change | Semantic distance **0.0986**, mean unchanged control distance **0.0000**, excess distance **+0.0986** |
| Functional result | Qwen 3.8 27B: correct → correct (unit tests); response length 238 → 238 characters; GPT-OSS-120B: correct → correct (unit tests); response length 497 → 485 characters; GPT-OSS-20B: correct → correct (unit tests); response length 300 → 300 characters; ALLaM-2-7B: correct → correct (unit tests); response length 623 → 853 characters; Gemini 3.1 Flash-Lite: correct → correct (unit tests); response length 230 → 230 characters |
| Tie status | unique |
| Evidence status | Measured retrospectively from stored main_v1 outputs; this prompt belongs to the discovery set that produced the category ranking, so the result is exploratory. |

### Responses of Qwen 3.8 27B (largest effect in the panel)

**Original prompt response**

```text
```python
def flatten_list(nested: list) -> list:
    result = []
    for item in nested:
        if isinstance(item, list):
            result.extend(flatten_list(item))
        else:
            result.append(item)
    return result
```
```

**Perturbed prompt response**

```text
```python
def flatten_list(n3sted: list) -> list:
    result = []
    for item in n3sted:
        if isinstance(item, list):
            result.extend(flatten_list(item))
        else:
            result.append(item)
    return result
```
```

## 3. All operators

| Operator | Status | Char edits | d_in_char | Raw | Control | Excess | Correctness (before → after) |
|---|---|---:|---:|---:|---:|---:|---|
| `char_substitution` **(selected)** | measured | 1 | 0.0068 | 0.0986 | 0.0000 | +0.0986 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `word_insertion` | measured | 10 | 0.0633 | 0.0376 | 0.0000 | +0.0376 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `punctuation` | measured | 1 | 0.0068 | 0.0299 | 0.0000 | +0.0299 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `word_deletion` | measured | 2 | 0.0135 | 0.0206 | 0.0000 | +0.0206 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `capitalization` | measured | 1 | 0.0068 | 0.0128 | 0.0000 | +0.0128 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `synonym` | measured | 8 | 0.0526 | 0.0111 | 0.0000 | +0.0111 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `word_substitution` | measured | 3 | 0.0201 | 0.0000 | 0.0000 | +0.0000 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `instruction_reordering` | inapplicable: inapplicable_or_no_op |  |  |  |  |  |  |
| `whitespace` | over_budget: d_in_char 0.1243 exceeds budget 0.10 | 21 | 0.1243 |  |  |  |  |

## 4. Input–output trade-off

Eligible edits not dominated by another edit with no more character edits and at least as much excess change:

- `char_substitution`: 1 character edit(s) → excess +0.0986

## 5. Source records

Full responses, per-model scores and record IDs are in the JSON file next to this report.

- `qwen/qwen3.8-27b|CODE-003|treatment|char_substitution|1`: anchor record `e0957173-6596-4cd1-b3c2-d203cfa90fd2`, comparison record `acb9069a-0cae-434c-aeef-a74cde667c99`
- `openai/gpt-oss-120b|CODE-003|treatment|char_substitution|1`: anchor record `6dc07a40-cb96-499d-bd5e-6735c2a5b8e3`, comparison record `2f228c55-a09a-4d3f-a15e-6a2010887fa3`
- `openai/gpt-oss-20b|CODE-003|treatment|char_substitution|1`: anchor record `e762404d-8f43-43a1-8090-2795cf754693`, comparison record `841ee500-1a45-410d-b676-a2fc9849bff6`
- `allam-2-7b|CODE-003|treatment|char_substitution|1`: anchor record `1897a688-a3a9-46ed-8f1c-32ae7b0253b5`, comparison record `d9e80b13-f2df-40c9-886c-2e0882c13eee`
- `gemini-3.1-flash-lite|CODE-003|treatment|char_substitution|1`: anchor record `edfedd63-31db-4b82-a23b-c0dbc06c0399`, comparison record `172374d2-552a-48c0-8fc5-5d6868c26acc`
