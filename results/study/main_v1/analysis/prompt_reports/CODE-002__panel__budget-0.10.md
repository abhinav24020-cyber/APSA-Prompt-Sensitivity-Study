# Perturbation operator result: CODE-002 · Code generation

**Status:** `selected` · **Rule:** budget mode, d_in_char ≤ 0.10 · **Model scope:** fixed panel of 5 models, equal weights · **Evidence:** retrospective

## 1. Category recommendation

- Recommended: **word_insertion** (exploratory (main_v1 discovery ranking); source: category_operator_rankings.csv (code_generation, budget 0.10))
- Category score 0.0386, coverage 10/10 complete prompts
- Why: A leading tone cue ('Carefully') can change which implementation the model writes while preserving the signature and input/output contract.
- A category recommendation is not a measurement of this prompt; the measured result follows.

## 2. Measured result for this prompt

char_substitution produced the largest control-adjusted change (+0.0432) among 6 eligible, measured edits within budget 0.10. The next best eligible edit was capitalization (+0.0395). Preservation evidence: not flagged by the retrospective audit (every candidate of this operator was audited).

| Field | Result |
|---|---|
| Prompt and category | `CODE-002` · Code generation |
| Original prompt | Write a Python function is_prime(n: int) -> bool that returns True if n is a prime number and False otherwise, operating in O(sqrt(n)) time. |
| Perturbed prompt | Write a Python function is_prime(n: int) -> bool that returns True if n is a prime number and False 0therwise, operating in O(sqrt(n)) time. |
| Operator | `char_substitution`: `otherwise,` → `0therwise,` |
| Input change | **1 character edit(s)**, normalised distance **0.0071**, semantic input distance 0.0184 |
| Model and comparison | fixed panel of 5 models, equal weights; 5 matched model–prompt pair(s) from `main_v1` |
| Output change | Semantic distance **0.0432**, mean unchanged control distance **0.0000**, excess distance **+0.0432** |
| Functional result | Qwen 3.8 27B: correct → correct (unit tests); response length 264 → 264 characters; GPT-OSS-120B: correct → correct (unit tests); response length 473 → 489 characters; GPT-OSS-20B: correct → correct (unit tests); response length 395 → 362 characters; ALLaM-2-7B: correct → correct (unit tests); response length 655 → 649 characters; Gemini 3.1 Flash-Lite: correct → correct (unit tests); response length 406 → 421 characters |
| Tie status | unique |
| Evidence status | Measured retrospectively from stored main_v1 outputs; this prompt belongs to the discovery set that produced the category ranking, so the result is exploratory. |

### Responses of ALLaM-2-7B (largest effect in the panel)

**Original prompt response**

```text
To create a Python function that checks if a number is prime within O(sqrt(n)) time, you can use the following code:

```python
def is_prime(n: int) -> bool:
    if n <= 1:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True
```

This function first checks if the number is less than or equal to 1, as prime numbers are greater than 1. Then, it iterates from 2 to the square root of n (inclusive) to check for divisors. If a divisor is found, the function returns False, indicating that n is not prime. If no divisor is found, the function returns True, indicating that n is prime.
```

**Perturbed prompt response**

```text
Here's a Python function that checks if a number is prime within O(sqrt(n)) time complexity:

```python
def is_prime(n: int) -> bool:
    if n <= 1:
        return False
    elif n <= 3:
        return True
    elif n % 2 == 0 or n % 3 == 0:
        return False

    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6

    return True
```

This function first handles the base cases (numbers less than or equal to 1 or 3) and then checks for divisibility by known prime factors (2 and 3). For larger numbers, it checks for divisibility by odd numbers up to the square root of the number.
```

## 3. All operators

| Operator | Status | Char edits | d_in_char | Raw | Control | Excess | Correctness (before → after) |
|---|---|---:|---:|---:|---:|---:|---|
| `char_substitution` **(selected)** | measured | 1 | 0.0071 | 0.0432 | 0.0000 | +0.0432 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `capitalization` | measured | 1 | 0.0071 | 0.0395 | 0.0000 | +0.0395 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `word_insertion` | measured | 10 | 0.0667 | 0.0388 | 0.0000 | +0.0388 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `synonym` | measured | 6 | 0.0423 | 0.0380 | 0.0000 | +0.0380 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `word_deletion` | measured | 2 | 0.0143 | 0.0251 | 0.0000 | +0.0251 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `punctuation` | measured | 1 | 0.0071 | 0.0110 | 0.0000 | +0.0110 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `instruction_reordering` | inapplicable: inapplicable_or_no_op |  |  |  |  |  |  |
| `whitespace` | over_budget: d_in_char 0.1411 exceeds budget 0.10 | 23 | 0.1411 |  |  |  |  |
| `word_substitution` | meaning_changing: retrospective audit flag: specification_changed | 4 | 0.0286 |  |  |  |  |

## 4. Input–output trade-off

Eligible edits not dominated by another edit with no more character edits and at least as much excess change:

- `char_substitution`: 1 character edit(s) → excess +0.0432

## 5. Source records

Full responses, per-model scores and record IDs are in the JSON file next to this report.

- `qwen/qwen3.8-27b|CODE-002|treatment|char_substitution|1`: anchor record `304e0aa8-09fb-4746-aa65-1b68362c4cf3`, comparison record `2ab095c6-50bc-4d71-84a1-d296bb0a80e5`
- `openai/gpt-oss-120b|CODE-002|treatment|char_substitution|1`: anchor record `8499613e-2f33-411f-a6c5-01e8af48a01a`, comparison record `baf3d3a9-d0d2-4635-b480-9d6d805f2196`
- `openai/gpt-oss-20b|CODE-002|treatment|char_substitution|1`: anchor record `c192f5ed-6f41-4e2d-ad42-0241f59104c9`, comparison record `7ce01d5d-b03a-4b49-af63-fb840b0fa203`
- `allam-2-7b|CODE-002|treatment|char_substitution|1`: anchor record `b7e04e65-b726-4a0b-8907-2ca64a71268a`, comparison record `a3b28731-21eb-4757-a208-df3a313b4b6f`
- `gemini-3.1-flash-lite|CODE-002|treatment|char_substitution|1`: anchor record `8ff9213f-d0ee-45a8-9a46-95bacf6e3ff5`, comparison record `abbd412d-0b56-4f94-bca5-ab9fbd58ddbf`
