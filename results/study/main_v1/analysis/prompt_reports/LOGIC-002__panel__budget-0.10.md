# Perturbation operator result: LOGIC-002 · Logical reasoning

**Status:** `selected` · **Rule:** budget mode, d_in_char ≤ 0.10 · **Model scope:** fixed panel of 5 models, equal weights · **Evidence:** retrospective

## 1. Category recommendation

- Recommended: **punctuation** (exploratory (main_v1 discovery ranking); source: category_operator_rankings.csv (logical_reasoning, budget 0.10))
- Category score 0.0744, coverage 9/9 complete prompts
- Why: A terminal punctuation edit changes the cue at the end of the prompt while leaving premises and the requested conclusion intact.
- A category recommendation is not a measurement of this prompt; the measured result follows.

## 2. Measured result for this prompt

word_insertion produced the largest control-adjusted change (+0.0343) among 5 eligible, measured edits within budget 0.10. The next best eligible edit was capitalization (+0.0279). Preservation evidence: not flagged by the retrospective audit (operator audited by a sample of 5 candidates).

| Field | Result |
|---|---|
| Prompt and category | `LOGIC-002` · Logical reasoning |
| Original prompt | On an island, Knights always tell the truth and Knaves always lie. You meet Person A and Person B. Person A says: 'At least one of us is a Knave.' What are Person A and Person B? |
| Perturbed prompt | Carefully On an island, Knights always tell the truth and Knaves always lie. You meet Person A and Person B. Person A says: 'At least one of us is a Knave.' What are Person A and Person B? |
| Operator | `word_insertion`: `∅` → `Carefully` |
| Input change | **10 character edit(s)**, normalised distance **0.0532**, semantic input distance 0.0048 |
| Model and comparison | fixed panel of 5 models, equal weights; 5 matched model–prompt pair(s) from `main_v1` |
| Output change | Semantic distance **0.0387**, mean unchanged control distance **0.0044**, excess distance **+0.0343** |
| Functional result | Qwen 3.8 27B: correct → correct; same final answer; response length 1447 → 1364 characters; GPT-OSS-120B: correct → correct; same final answer; response length 84 → 84 characters; GPT-OSS-20B: correct → correct; same final answer; response length 90 → 90 characters; ALLaM-2-7B: incorrect → incorrect; final answer text changed; response length 1113 → 533 characters; Gemini 3.1 Flash-Lite: correct → correct; same final answer; response length 497 → 497 characters |
| Tie status | unique |
| Evidence status | Measured retrospectively from stored main_v1 outputs; this prompt belongs to the discovery set that produced the category ranking, so the result is exploratory. |

### Responses of ALLaM-2-7B (largest effect in the panel)

**Original prompt response**

```text
Let's analyze the statement from Person A:

1. If Person A is a knight (always tells the truth), then their statement "At least one of us is a Knave" would be true because there is at least one person who is a knave (Person B).
2. If Person A is a knave (always lies), then their statement would also be true because they want to believe that at least one of them is a knave (which means they are the only knave).

In both cases, the statement from Person A is true. Now, let's consider Person B's statement:

1. If Person B is a knight, their statement "I am not a knave" would be true because they are not a knave (knights tell the truth).
2. If Person B is a knave, their statement would be false because they are a knave, making them a knave in the statement.

In conclusion, Person A could be a knight or a knave, and Person B could be a knight or a knave as well. There are two possible combinations:

1. Person A is a knight, and Person B is a knave.
2. Person A is a knave, and Person B is a knight.

Final answer: Person A could be a knight or a knave, and Person B could be a knight or a knave as well.
```

**Perturbed prompt response**

```text
Let's analyze the statement from Person A:

1. If Person A is a knight, their statement would be true because at least one of them (Person A) is a knight and knights always tell the truth.
2. If Person A is a knave, their statement would also be true because at least one of them (Person A) is a knave, and knaves always lie about being a knave.

Both cases satisfy the statement, so we cannot determine Person A's and Person B's roles based on this information alone. We need more information to identify them as knights or knaves.
```

## 3. All operators

| Operator | Status | Char edits | d_in_char | Raw | Control | Excess | Correctness (before → after) |
|---|---|---:|---:|---:|---:|---:|---|
| `word_insertion` **(selected)** | measured | 10 | 0.0532 | 0.0387 | 0.0044 | +0.0343 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→incorrect; Gemini 3.1 Flash-Lite correct→correct |
| `capitalization` | measured | 1 | 0.0056 | 0.0323 | 0.0044 | +0.0279 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→incorrect; Gemini 3.1 Flash-Lite correct→correct |
| `char_substitution` | measured | 1 | 0.0056 | 0.0296 | 0.0044 | +0.0252 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→incorrect; Gemini 3.1 Flash-Lite correct→correct |
| `punctuation` | measured | 1 | 0.0056 | 0.0191 | 0.0044 | +0.0148 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→correct; Gemini 3.1 Flash-Lite correct→correct |
| `word_deletion` | measured | 4 | 0.0225 | 0.0173 | 0.0044 | +0.0129 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→correct; Gemini 3.1 Flash-Lite correct→correct |
| `instruction_reordering` | over_budget: d_in_char 0.6180 exceeds budget 0.10 | 110 | 0.6180 |  |  |  |  |
| `synonym` | inapplicable: inapplicable_or_no_op |  |  |  |  |  |  |
| `whitespace` | over_budget: d_in_char 0.1682 exceeds budget 0.10 | 36 | 0.1682 |  |  |  |  |
| `word_substitution` | inapplicable: inapplicable_or_no_op |  |  |  |  |  |  |

## 4. Input–output trade-off

Eligible edits not dominated by another edit with no more character edits and at least as much excess change:

- `capitalization`: 1 character edit(s) → excess +0.0279
- `word_insertion`: 10 character edit(s) → excess +0.0343

## 5. Source records

Full responses, per-model scores and record IDs are in the JSON file next to this report.

- `qwen/qwen3.8-27b|LOGIC-002|treatment|word_insertion|1`: anchor record `4b9f2c02-5fb6-433e-b292-56a32107a237`, comparison record `70dd1c0c-1881-4c10-a0e5-797e04dd1376`
- `openai/gpt-oss-120b|LOGIC-002|treatment|word_insertion|1`: anchor record `e398d658-f9ec-4e5b-9aae-0817c87aa569`, comparison record `1c0e77e5-43e8-4472-ac71-92781e80eba8`
- `openai/gpt-oss-20b|LOGIC-002|treatment|word_insertion|1`: anchor record `9b652077-a44d-4eda-a2c9-2e3d207bc504`, comparison record `7d58f01f-3f6a-4d21-ba25-decb3e683788`
- `allam-2-7b|LOGIC-002|treatment|word_insertion|1`: anchor record `6f8c94d2-2d3f-460b-9883-000db034e47b`, comparison record `57c6612e-b27d-4bf1-a80b-c7d5585fd718`
- `gemini-3.1-flash-lite|LOGIC-002|treatment|word_insertion|1`: anchor record `2e2ff70d-b779-4ded-b33d-f949eee44935`, comparison record `cc4901c3-6b6b-4749-bb46-551989cd41c3`
