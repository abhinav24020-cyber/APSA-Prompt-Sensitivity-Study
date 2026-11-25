# Perturbation operator result: CODE-010 · Code generation

**Status:** `selected` · **Rule:** budget mode, d_in_char ≤ 0.10 · **Model scope:** fixed panel of 5 models, equal weights · **Evidence:** retrospective

## 1. Category recommendation

- Recommended: **word_insertion** (exploratory (main_v1 discovery ranking); source: category_operator_rankings.csv (code_generation, budget 0.10))
- Category score 0.0386, coverage 10/10 complete prompts
- Why: A leading tone cue ('Carefully') can change which implementation the model writes while preserving the signature and input/output contract.
- A category recommendation is not a measurement of this prompt; the measured result follows.

## 2. Measured result for this prompt

capitalization produced the largest control-adjusted change (+0.0720) among 7 eligible, measured edits within budget 0.10. The next best eligible edit was char_substitution (+0.0597). Preservation evidence: not flagged by the retrospective audit (operator audited by a sample of 5 candidates).

| Field | Result |
|---|---|
| Prompt and category | `CODE-010` · Code generation |
| Original prompt | Write a Python function max_subarray_sum(nums: list[int]) -> int that finds the maximum sum of a contiguous subarray using Kadane's algorithm. |
| Perturbed prompt | write a Python function max_subarray_sum(nums: list[int]) -> int that finds the maximum sum of a contiguous subarray using Kadane's algorithm. |
| Operator | `capitalization`: `Write` → `write` |
| Input change | **1 character edit(s)**, normalised distance **0.0070**, semantic input distance 0.0000 |
| Model and comparison | fixed panel of 5 models, equal weights; 5 matched model–prompt pair(s) from `main_v1` |
| Output change | Semantic distance **0.0720**, mean unchanged control distance **0.0000**, excess distance **+0.0720** |
| Functional result | Qwen 3.8 27B: correct → correct (unit tests); response length 267 → 267 characters; GPT-OSS-120B: correct → correct (unit tests); response length 548 → 475 characters; GPT-OSS-20B: correct → correct (unit tests); response length 447 → 436 characters; ALLaM-2-7B: incorrect → correct (unit tests); final answer text changed; response length 442 → 1251 characters; Gemini 3.1 Flash-Lite: correct → correct (unit tests); response length 411 → 320 characters |
| Tie status | unique |
| Evidence status | Measured retrospectively from stored main_v1 outputs; this prompt belongs to the discovery set that produced the category ranking, so the result is exploratory. |

### Responses of ALLaM-2-7B (largest effect in the panel)

**Original prompt response**

```text
```python
def max_subarray_sum(nums):
    max_so_far = nums[0]
    max_ending_here = nums[0]

    for num in nums[1:]:
        max_ending_here = max(num, max_ending_here + num)
        if max_ending_here < 0:
            max_ending_here = 0
        else:
            max_so_far = max(max_so_far, max_ending_here)

    return max_so_far
```
Final answer: The function returns the maximum sum of a contiguous subarray using Kadane's algorithm.
```

**Perturbed prompt response**

```text
Sure, here's the Python function implementing Kadane's algorithm:

```python
def max_subarray_sum(nums):
    max_so_far = nums[0]  # Initialize max_so_far with the first element of the list
    max_ending_here = nums[0]  # Initialize max_ending_here with the first element of the list

    for num in nums[1:]:  # Iterate over the remaining elements of the list
        max_ending_here = max(num + max_ending_here, num)  # Update max_ending_here with the maximum of the current element and the sum of max_ending_here and the current element
        if max_ending_here < 0:  # If max_ending_here becomes negative, reset it to the current element
            max_ending_here = num
        max_so_far = max(max_so_far, max_ending_here)  # Update max_so_far with the maximum of the current max_so_far and max_ending_here

    return max_so_far
```

You can use this function by passing a list of integers to it:

```python
numbers = [1, -2, 3, -5, 6, -7, 8, -9, 10]
result = max_subarray_sum(numbers)
print("The maximum sum of a contiguous subarray is:", result)
```

This will output:

```
The maximum sum of a contiguous subarray is: 14
```

In this example, the maximum sum of a contiguous subarray is 14, which is achieved by the subarray [6, 8, 10].
```

## 3. All operators

| Operator | Status | Char edits | d_in_char | Raw | Control | Excess | Correctness (before → after) |
|---|---|---:|---:|---:|---:|---:|---|
| `capitalization` **(selected)** | measured | 1 | 0.0070 | 0.0720 | 0.0000 | +0.0720 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→correct; Gemini 3.1 Flash-Lite correct→correct |
| `char_substitution` | measured | 1 | 0.0070 | 0.0597 | 0.0000 | +0.0597 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→incorrect; Gemini 3.1 Flash-Lite correct→correct |
| `word_deletion` | measured | 4 | 0.0282 | 0.0436 | 0.0000 | +0.0436 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→incorrect; Gemini 3.1 Flash-Lite correct→correct |
| `word_insertion` | measured | 10 | 0.0658 | 0.0395 | 0.0000 | +0.0395 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→incorrect; Gemini 3.1 Flash-Lite correct→correct |
| `word_substitution` | measured | 3 | 0.0210 | 0.0305 | 0.0000 | +0.0305 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→incorrect; Gemini 3.1 Flash-Lite correct→correct |
| `punctuation` | measured | 1 | 0.0070 | 0.0248 | 0.0000 | +0.0248 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→incorrect; Gemini 3.1 Flash-Lite correct→correct |
| `synonym` | measured | 8 | 0.0559 | 0.0190 | 0.0000 | +0.0190 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→incorrect; Gemini 3.1 Flash-Lite correct→correct |
| `instruction_reordering` | inapplicable: inapplicable_or_no_op |  |  |  |  |  |  |
| `whitespace` | over_budget: d_in_char 0.1180 exceeds budget 0.10 | 19 | 0.1180 |  |  |  |  |

## 4. Input–output trade-off

Eligible edits not dominated by another edit with no more character edits and at least as much excess change:

- `capitalization`: 1 character edit(s) → excess +0.0720

## 5. Source records

Full responses, per-model scores and record IDs are in the JSON file next to this report.

- `qwen/qwen3.8-27b|CODE-010|treatment|capitalization|1`: anchor record `d3c4ebd7-7b7f-4a03-be27-ad4834a833b8`, comparison record `ec2e1356-5e54-4942-b8a0-2e39f19e76c9`
- `openai/gpt-oss-120b|CODE-010|treatment|capitalization|1`: anchor record `1738581d-68c1-46a5-902d-c9257c7adf8f`, comparison record `6acb8917-8a16-4992-aef5-86e37bf3b946`
- `openai/gpt-oss-20b|CODE-010|treatment|capitalization|1`: anchor record `d1fcaf74-7da9-4434-bc96-ab91a13d230e`, comparison record `62f782aa-6a3d-4aea-b4a6-5d2e4e32e41e`
- `allam-2-7b|CODE-010|treatment|capitalization|1`: anchor record `86f68e56-0c80-4cf2-9445-a6cd8659f553`, comparison record `1e575752-729f-48da-b196-93dee0f9146a`
- `gemini-3.1-flash-lite|CODE-010|treatment|capitalization|1`: anchor record `37b0c4d0-82cd-4886-8725-c0fdba0de273`, comparison record `bd042a91-d2ff-42f9-8a49-4f65975d49a5`
