# Perturbation operator result: LOGIC-009 · Logical reasoning

**Status:** `selected` · **Rule:** budget mode, d_in_char ≤ 0.10 · **Model scope:** fixed panel of 5 models, equal weights · **Evidence:** retrospective

## 1. Category recommendation

- Recommended: **punctuation** (exploratory (main_v1 discovery ranking); source: category_operator_rankings.csv (logical_reasoning, budget 0.10))
- Category score 0.0744, coverage 9/9 complete prompts
- Why: A terminal punctuation edit changes the cue at the end of the prompt while leaving premises and the requested conclusion intact.
- A category recommendation is not a measurement of this prompt; the measured result follows.

## 2. Measured result for this prompt

word_insertion produced the largest control-adjusted change (+0.0928) among 7 eligible, measured edits within budget 0.10. The next best eligible edit was synonym (+0.0724). Preservation evidence: not flagged by the retrospective audit (operator audited by a sample of 5 candidates).

| Field | Result |
|---|---|
| Prompt and category | `LOGIC-009` · Logical reasoning |
| Original prompt | Identify the logical fallacy in the following statement: 'We must not lower taxes because if we do, nobody will work, society will collapse, and we will end up in complete anarchy.' |
| Perturbed prompt | Carefully Identify the logical fallacy in the following statement: 'We must not lower taxes because if we do, nobody will work, society will collapse, and we will end up in complete anarchy.' |
| Operator | `word_insertion`: `∅` → `Carefully` |
| Input change | **10 character edit(s)**, normalised distance **0.0524**, semantic input distance 0.0085 |
| Model and comparison | fixed panel of 5 models, equal weights; 5 matched model–prompt pair(s) from `main_v1` |
| Output change | Semantic distance **0.0952**, mean unchanged control distance **0.0024**, excess distance **+0.0928** |
| Functional result | Qwen 3.8 27B: correct → correct; same final answer; response length 443 → 453 characters; GPT-OSS-120B: incorrect → incorrect; same final answer; response length 332 → 313 characters; GPT-OSS-20B: incorrect → incorrect; same final answer; response length 270 → 269 characters; ALLaM-2-7B: correct → correct; same final answer; response length 308 → 290 characters; Gemini 3.1 Flash-Lite: correct → correct; same final answer; response length 335 → 380 characters |
| Tie status | unique |
| Evidence status | Measured retrospectively from stored main_v1 outputs; this prompt belongs to the discovery set that produced the category ranking, so the result is exploratory. |

### Responses of ALLaM-2-7B (largest effect in the panel)

**Original prompt response**

```text
The logical fallacy in this statement is known as the 'Slippery Slope' fallacy or 'Strawman' fallacy. It falsely assumes that lowering taxes will directly lead to extreme negative outcomes without providing proper evidence or a gradual explanation of the consequences. 

Final answer: Slippery Slope fallacy
```

**Perturbed prompt response**

```text
The logical fallacy in the statement is 'Slippery slope' fallacy. This fallacy occurs when the argument suggests that a specific event will lead to a chain of extreme and unlikely consequences without providing proper evidence for those consequences. 

Final answer: Slippery slope fallacy
```

## 3. All operators

| Operator | Status | Char edits | d_in_char | Raw | Control | Excess | Correctness (before → after) |
|---|---|---:|---:|---:|---:|---:|---|
| `word_insertion` **(selected)** | measured | 10 | 0.0524 | 0.0952 | 0.0024 | +0.0928 | Qwen 3.8 27B correct→correct; GPT-OSS-120B incorrect→incorrect; GPT-OSS-20B incorrect→incorrect; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `synonym` | measured | 8 | 0.0440 | 0.0748 | 0.0024 | +0.0724 | Qwen 3.8 27B correct→correct; GPT-OSS-120B incorrect→incorrect; GPT-OSS-20B incorrect→incorrect; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `word_deletion` | measured | 4 | 0.0221 | 0.0624 | 0.0024 | +0.0600 | Qwen 3.8 27B correct→correct; GPT-OSS-120B incorrect→incorrect; GPT-OSS-20B incorrect→incorrect; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `char_substitution` | measured | 1 | 0.0055 | 0.0583 | 0.0024 | +0.0559 | Qwen 3.8 27B correct→correct; GPT-OSS-120B incorrect→incorrect; GPT-OSS-20B incorrect→incorrect; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `word_substitution` | measured | 6 | 0.0331 | 0.0364 | 0.0024 | +0.0340 | Qwen 3.8 27B correct→correct; GPT-OSS-120B incorrect→incorrect; GPT-OSS-20B incorrect→incorrect; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `capitalization` | measured | 1 | 0.0055 | 0.0305 | 0.0024 | +0.0281 | Qwen 3.8 27B correct→correct; GPT-OSS-120B incorrect→incorrect; GPT-OSS-20B incorrect→incorrect; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `punctuation` | measured | 1 | 0.0055 | 0.0134 | 0.0024 | +0.0110 | Qwen 3.8 27B correct→correct; GPT-OSS-120B incorrect→incorrect; GPT-OSS-20B incorrect→incorrect; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `instruction_reordering` | inapplicable: inapplicable_or_no_op |  |  |  |  |  |  |
| `whitespace` | over_budget: d_in_char 0.1422 exceeds budget 0.10 | 30 | 0.1422 |  |  |  |  |

## 4. Input–output trade-off

Eligible edits not dominated by another edit with no more character edits and at least as much excess change:

- `char_substitution`: 1 character edit(s) → excess +0.0559
- `word_deletion`: 4 character edit(s) → excess +0.0600
- `synonym`: 8 character edit(s) → excess +0.0724
- `word_insertion`: 10 character edit(s) → excess +0.0928

## 5. Source records

Full responses, per-model scores and record IDs are in the JSON file next to this report.

- `qwen/qwen3.8-27b|LOGIC-009|treatment|word_insertion|1`: anchor record `ff6ac4b5-465b-4065-8eb1-01fbc42143e2`, comparison record `b77576c8-fdcc-411b-a873-63511c6705dc`
- `openai/gpt-oss-120b|LOGIC-009|treatment|word_insertion|1`: anchor record `a8d50229-55c6-4491-a53e-901832363885`, comparison record `17a7dca3-108e-4ce2-9c85-c9de14b158ce`
- `openai/gpt-oss-20b|LOGIC-009|treatment|word_insertion|1`: anchor record `5724d941-34d9-4ce8-88a3-57756e3cb23c`, comparison record `85582540-35f8-493f-8fc9-f683260c250a`
- `allam-2-7b|LOGIC-009|treatment|word_insertion|1`: anchor record `be57347e-53a9-4c91-939d-80935124fdf5`, comparison record `574a0dff-5a4d-4f23-8542-584dba6d98db`
- `gemini-3.1-flash-lite|LOGIC-009|treatment|word_insertion|1`: anchor record `732fe421-00dd-445f-b78a-d475378e20c0`, comparison record `4b11a503-89a0-4c6e-b8d1-0023370fcd78`
