# Perturbation operator result: LOGIC-001 · Logical reasoning

**Status:** `selected` · **Rule:** budget mode, d_in_char ≤ 0.10 · **Model scope:** fixed panel of 5 models, equal weights · **Evidence:** retrospective

## 1. Category recommendation

- Recommended: **punctuation** (exploratory (main_v1 discovery ranking); source: category_operator_rankings.csv (logical_reasoning, budget 0.10))
- Category score 0.0744, coverage 9/9 complete prompts
- Why: A terminal punctuation edit changes the cue at the end of the prompt while leaving premises and the requested conclusion intact.
- A category recommendation is not a measurement of this prompt; the measured result follows.

## 2. Measured result for this prompt

capitalization produced the largest control-adjusted change (+0.0304) among 7 eligible, measured edits within budget 0.10. The next best eligible edit was word_substitution (+0.0295). Preservation evidence: not flagged by the retrospective audit (operator audited by a sample of 5 candidates).

| Field | Result |
|---|---|
| Prompt and category | `LOGIC-001` · Logical reasoning |
| Original prompt | Evaluate the validity of this argument: Premise 1: All birds have feathers. Premise 2: All penguins are birds. Conclusion: All penguins have feathers. Is the conclusion logically valid? Answer Valid or Invalid and state the conclusion. |
| Perturbed prompt | evaluate the validity of this argument: Premise 1: All birds have feathers. Premise 2: All penguins are birds. Conclusion: All penguins have feathers. Is the conclusion logically valid? Answer Valid or Invalid and state the conclusion. |
| Operator | `capitalization`: `Evaluate` → `evaluate` |
| Input change | **1 character edit(s)**, normalised distance **0.0043**, semantic input distance 0.0000 |
| Model and comparison | fixed panel of 5 models, equal weights; 5 matched model–prompt pair(s) from `main_v1` |
| Output change | Semantic distance **0.0304**, mean unchanged control distance **0.0000**, excess distance **+0.0304** |
| Functional result | Qwen 3.8 27B: correct → correct; final answer text changed; response length 555 → 602 characters; GPT-OSS-120B: correct → correct; same final answer; response length 69 → 69 characters; GPT-OSS-20B: correct → correct; response length 46 → 48 characters; ALLaM-2-7B: incorrect → incorrect; same final answer; response length 49 → 49 characters; Gemini 3.1 Flash-Lite: correct → correct; final answer text changed; response length 285 → 285 characters |
| Tie status | unique |
| Evidence status | Measured retrospectively from stored main_v1 outputs; this prompt belongs to the discovery set that produced the category ranking, so the result is exploratory. |

### Responses of Qwen 3.8 27B (largest effect in the panel)

**Original prompt response**

```text
The argument is a classic example of a valid syllogism (specifically, Barbara form: All M are P, All S are M, therefore All S are P).

1.  **Premise 1**: All birds have feathers. (If something is a bird, it has feathers.)
2.  **Premise 2**: All penguins are birds. (If something is a penguin, it is a bird.)
3.  **Logical Deduction**: Since penguins are birds, and all birds have feathers, it necessarily follows that penguins have feathers.

Therefore, the conclusion follows logically from the premises.

Final answer: Valid; All penguins have feathers.
```

**Perturbed prompt response**

```text
The argument is a classic example of a valid syllogism (specifically, a Barbara syllogism).

1.  **Premise 1**: All $A$ are $B$ (All birds have feathers).
2.  **Premise 2**: All $C$ are $A$ (All penguins are birds).
3.  **Conclusion**: Therefore, all $C$ are $B$ (All penguins have feathers).

Since the set of penguins is a subset of the set of birds, and the set of birds is a subset of the set of things with feathers, it logically follows that the set of penguins is a subset of the set of things with feathers. The truth of the premises guarantees the truth of the conclusion.

Final answer: Valid
```

## 3. All operators

| Operator | Status | Char edits | d_in_char | Raw | Control | Excess | Correctness (before → after) |
|---|---|---:|---:|---:|---:|---:|---|
| `capitalization` **(selected)** | measured | 1 | 0.0043 | 0.0304 | 0.0000 | +0.0304 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→incorrect; Gemini 3.1 Flash-Lite correct→correct |
| `word_substitution` | measured | 8 | 0.0340 | 0.0295 | 0.0000 | +0.0295 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→incorrect; Gemini 3.1 Flash-Lite correct→correct |
| `word_insertion` | measured | 10 | 0.0408 | 0.0274 | 0.0000 | +0.0274 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→incorrect; Gemini 3.1 Flash-Lite correct→correct |
| `char_substitution` | measured | 1 | 0.0043 | 0.0273 | 0.0000 | +0.0273 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→incorrect; Gemini 3.1 Flash-Lite correct→correct |
| `punctuation` | measured | 1 | 0.0043 | 0.0256 | 0.0000 | +0.0256 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→incorrect; Gemini 3.1 Flash-Lite correct→correct |
| `synonym` | measured | 7 | 0.0295 | 0.0065 | 0.0000 | +0.0065 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→incorrect; Gemini 3.1 Flash-Lite correct→correct |
| `word_deletion` | measured | 4 | 0.0170 | 0.0041 | 0.0000 | +0.0041 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→incorrect; Gemini 3.1 Flash-Lite correct→correct |
| `instruction_reordering` | over_budget: d_in_char 0.4255 exceeds budget 0.10 | 100 | 0.4255 |  |  |  |  |
| `whitespace` | over_budget: d_in_char 0.1296 exceeds budget 0.10 | 35 | 0.1296 |  |  |  |  |

## 4. Input–output trade-off

Eligible edits not dominated by another edit with no more character edits and at least as much excess change:

- `capitalization`: 1 character edit(s) → excess +0.0304

## 5. Source records

Full responses, per-model scores and record IDs are in the JSON file next to this report.

- `qwen/qwen3.8-27b|LOGIC-001|treatment|capitalization|1`: anchor record `caf55c29-72c0-4d67-a13e-ed86a9e30786`, comparison record `fc9a5187-f5dd-47cb-bbd2-ac0b2f8084f6`
- `openai/gpt-oss-120b|LOGIC-001|treatment|capitalization|1`: anchor record `02b836d8-78a0-4698-8666-4937234738b6`, comparison record `80192e06-604a-4515-a00b-7011f282ed24`
- `openai/gpt-oss-20b|LOGIC-001|treatment|capitalization|1`: anchor record `79a01186-55cf-434d-b9d3-3da7360a2554`, comparison record `6270d449-fb0b-4d5a-b20b-bc357ad6b70e`
- `allam-2-7b|LOGIC-001|treatment|capitalization|1`: anchor record `d6d35a41-7025-4683-947f-d1c421947c0e`, comparison record `db626fce-4b4e-420f-a96f-6818e5e128c1`
- `gemini-3.1-flash-lite|LOGIC-001|treatment|capitalization|1`: anchor record `5acab190-b6a1-4abe-83ec-c4a6292725ea`, comparison record `165ba3e0-d81e-48c0-b40c-a2ba50f55468`
