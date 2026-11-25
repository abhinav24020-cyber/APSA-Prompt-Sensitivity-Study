# Perturbation operator result: LOGIC-004 · Logical reasoning

**Status:** `selected` · **Rule:** budget mode, d_in_char ≤ 0.10 · **Model scope:** fixed panel of 5 models, equal weights · **Evidence:** retrospective

## 1. Category recommendation

- Recommended: **punctuation** (exploratory (main_v1 discovery ranking); source: category_operator_rankings.csv (logical_reasoning, budget 0.10))
- Category score 0.0744, coverage 9/9 complete prompts
- Why: A terminal punctuation edit changes the cue at the end of the prompt while leaving premises and the requested conclusion intact.
- A category recommendation is not a measurement of this prompt; the measured result follows.

## 2. Measured result for this prompt

punctuation produced the largest control-adjusted change (+0.0700) among 5 eligible, measured edits within budget 0.10. The next best eligible edit was capitalization (+0.0648). Preservation evidence: not flagged by the retrospective audit (operator audited by a sample of 5 candidates).

| Field | Result |
|---|---|
| Prompt and category | `LOGIC-004` · Logical reasoning |
| Original prompt | State the logical negation of the proposition: 'It is raining AND it is cold.' Express the negated proposition in natural English using De Morgan's laws. |
| Perturbed prompt | State the logical negation of the proposition: 'It is raining AND it is cold.' Express the negated proposition in natural English using De Morgan's laws |
| Operator | `punctuation`: `laws.` → `laws` |
| Input change | **1 character edit(s)**, normalised distance **0.0065**, semantic input distance 0.0042 |
| Model and comparison | fixed panel of 5 models, equal weights; 5 matched model–prompt pair(s) from `main_v1` |
| Output change | Semantic distance **0.0700**, mean unchanged control distance **0.0000**, excess distance **+0.0700** |
| Functional result | Qwen 3.8 27B: correct → correct; same final answer; response length 837 → 861 characters; GPT-OSS-120B: correct → correct; same final answer; response length 119 → 119 characters; GPT-OSS-20B: correct → correct; same final answer; response length 112 → 112 characters; ALLaM-2-7B: incorrect → incorrect; final answer text changed; response length 144 → 681 characters; Gemini 3.1 Flash-Lite: correct → correct; same final answer; response length 259 → 280 characters |
| Tie status | unique |
| Evidence status | Measured retrospectively from stored main_v1 outputs; this prompt belongs to the discovery set that produced the category ranking, so the result is exploratory. |

### Responses of ALLaM-2-7B (largest effect in the panel)

**Original prompt response**

```text
The logical negation of the proposition 'It is raining AND it is cold' is: 'It is either dry or warm.'

Final answer: It is either dry or warm.
```

**Perturbed prompt response**

```text
First, let's represent the given proposition as a logical statement: P = 'It is raining AND it is cold.'

Now, we want to find the logical negation of P, which is denoted as not P or ¬P. According to De Morgan's laws, the negation of a conjunction (AND) can be expressed as the negation of each term in the conjunction. In this case, the negation of the conjunction 'It is raining AND it is cold' is:

¬P = 'Not it is raining OR Not it is cold.'

Now, let's express this in natural English: The negated proposition is that "It is neither raining nor cold." 

Final answer: The logical negation of the proposition 'It is raining AND it is cold' is "It is neither raining nor cold."
```

## 3. All operators

| Operator | Status | Char edits | d_in_char | Raw | Control | Excess | Correctness (before → after) |
|---|---|---:|---:|---:|---:|---:|---|
| `punctuation` **(selected)** | measured | 1 | 0.0065 | 0.0700 | 0.0000 | +0.0700 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→incorrect; Gemini 3.1 Flash-Lite correct→correct |
| `capitalization` | measured | 1 | 0.0065 | 0.0648 | 0.0000 | +0.0648 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→correct; Gemini 3.1 Flash-Lite correct→correct |
| `char_substitution` | measured | 1 | 0.0065 | 0.0596 | 0.0000 | +0.0596 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→incorrect; Gemini 3.1 Flash-Lite correct→correct |
| `word_deletion` | measured | 4 | 0.0261 | 0.0556 | 0.0000 | +0.0556 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→correct; Gemini 3.1 Flash-Lite correct→correct |
| `word_insertion` | measured | 10 | 0.0614 | 0.0331 | 0.0000 | +0.0331 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→incorrect; Gemini 3.1 Flash-Lite correct→correct |
| `instruction_reordering` | inapplicable: inapplicable_or_no_op |  |  |  |  |  |  |
| `synonym` | inapplicable: inapplicable_or_no_op |  |  |  |  |  |  |
| `whitespace` | over_budget: d_in_char 0.1356 exceeds budget 0.10 | 24 | 0.1356 |  |  |  |  |
| `word_substitution` | inapplicable: inapplicable_or_no_op |  |  |  |  |  |  |

## 4. Input–output trade-off

Eligible edits not dominated by another edit with no more character edits and at least as much excess change:

- `punctuation`: 1 character edit(s) → excess +0.0700

## 5. Source records

Full responses, per-model scores and record IDs are in the JSON file next to this report.

- `qwen/qwen3.8-27b|LOGIC-004|treatment|punctuation|1`: anchor record `452e2223-8ee4-484e-bd7c-5ba07cf32480`, comparison record `cfaa160a-0580-4ef1-a8e9-c13d43092ff8`
- `openai/gpt-oss-120b|LOGIC-004|treatment|punctuation|1`: anchor record `124aa25a-15ac-4bf8-a4ab-190203f2cb77`, comparison record `170ca03e-708a-47ba-8fa9-259f78d56e64`
- `openai/gpt-oss-20b|LOGIC-004|treatment|punctuation|1`: anchor record `a228edf8-6dcb-47f1-a03e-1325db6d0a90`, comparison record `de9d2010-2410-479e-a9e4-bf41b39442f3`
- `allam-2-7b|LOGIC-004|treatment|punctuation|1`: anchor record `71b6926a-dc22-4018-acf2-be837ff936a9`, comparison record `2c9f6ff1-b215-44a4-b653-15ebac0653fd`
- `gemini-3.1-flash-lite|LOGIC-004|treatment|punctuation|1`: anchor record `5d1c51a9-0c13-4f3c-be21-798ab7aad55c`, comparison record `cdca05bb-2002-4ecd-848d-f39701951574`
