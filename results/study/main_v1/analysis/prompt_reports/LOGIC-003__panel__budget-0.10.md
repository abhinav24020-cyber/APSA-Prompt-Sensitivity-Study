# Perturbation operator result: LOGIC-003 · Logical reasoning

**Status:** `selected` · **Rule:** budget mode, d_in_char ≤ 0.10 · **Model scope:** fixed panel of 5 models, equal weights · **Evidence:** retrospective

## 1. Category recommendation

- Recommended: **punctuation** (exploratory (main_v1 discovery ranking); source: category_operator_rankings.csv (logical_reasoning, budget 0.10))
- Category score 0.0744, coverage 9/9 complete prompts
- Why: A terminal punctuation edit changes the cue at the end of the prompt while leaving premises and the requested conclusion intact.
- A category recommendation is not a measurement of this prompt; the measured result follows.

## 2. Measured result for this prompt

word_deletion produced the largest control-adjusted change (+0.1538) among 4 eligible, measured edits within budget 0.10. The next best eligible edit was capitalization (+0.0876). Preservation evidence: not flagged by the retrospective audit (every candidate of this operator was audited).

| Field | Result |
|---|---|
| Prompt and category | `LOGIC-003` · Logical reasoning |
| Original prompt | Four friends (Alice, Bob, Carol, Dave) sit in a row of 4 chairs numbered 1 to 4 from left to right. Alice sits in seat 1. Bob sits next to Carol. Dave does not sit next to Alice. Who sits in seat 4? |
| Perturbed prompt | Four friends (Alice, Bob, Carol, Dave) sit in row of 4 chairs numbered 1 to 4 from left to right. Alice sits in seat 1. Bob sits next to Carol. Dave does not sit next to Alice. Who sits in seat 4? |
| Operator | `word_deletion`: `a` → `∅` |
| Input change | **2 character edit(s)**, normalised distance **0.0101**, semantic input distance 0.0007 |
| Model and comparison | fixed panel of 5 models, equal weights; 5 matched model–prompt pair(s) from `main_v1` |
| Output change | Semantic distance **0.1538**, mean unchanged control distance **0.0000**, excess distance **+0.1538** |
| Functional result | Qwen 3.8 27B: correct → correct; same final answer; response length 1790 → 1476 characters; GPT-OSS-120B: correct → correct; same final answer; response length 40 → 18 characters; GPT-OSS-20B: correct → correct; same final answer; response length 41 → 24 characters; ALLaM-2-7B: incorrect → incorrect; final answer text changed; response length 285 → 375 characters; Gemini 3.1 Flash-Lite: correct → correct; same final answer; response length 926 → 816 characters |
| Tie status | unique |
| Evidence status | Measured retrospectively from stored main_v1 outputs; this prompt belongs to the discovery set that produced the category ranking, so the result is exploratory. |

### Responses of GPT-OSS-120B (largest effect in the panel)

**Original prompt response**

```text
Dave sits in seat 4.

Final answer: Dave
```

**Perturbed prompt response**

```text
Final answer: Dave
```

## 3. All operators

| Operator | Status | Char edits | d_in_char | Raw | Control | Excess | Correctness (before → after) |
|---|---|---:|---:|---:|---:|---:|---|
| `word_deletion` **(selected)** | measured | 2 | 0.0101 | 0.1538 | 0.0000 | +0.1538 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→incorrect; Gemini 3.1 Flash-Lite correct→correct |
| `capitalization` | measured | 1 | 0.0051 | 0.0876 | 0.0000 | +0.0876 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→incorrect; Gemini 3.1 Flash-Lite correct→correct |
| `word_insertion` | measured | 10 | 0.0481 | 0.0731 | 0.0000 | +0.0731 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→incorrect; Gemini 3.1 Flash-Lite correct→correct |
| `punctuation` | measured | 1 | 0.0051 | 0.0263 | 0.0000 | +0.0263 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→incorrect; ALLaM-2-7B incorrect→incorrect; Gemini 3.1 Flash-Lite correct→correct |
| `char_substitution` | meaning_changing: retrospective audit flag: answer_entity_changed | 1 | 0.0051 |  |  |  |  |
| `instruction_reordering` | over_budget: d_in_char 0.2020 exceeds budget 0.10 | 40 | 0.2020 |  |  |  |  |
| `synonym` | inapplicable: inapplicable_or_no_op |  |  |  |  |  |  |
| `whitespace` | over_budget: d_in_char 0.1750 exceeds budget 0.10 | 42 | 0.1750 |  |  |  |  |
| `word_substitution` | inapplicable: inapplicable_or_no_op |  |  |  |  |  |  |

## 4. Input–output trade-off

Eligible edits not dominated by another edit with no more character edits and at least as much excess change:

- `capitalization`: 1 character edit(s) → excess +0.0876
- `word_deletion`: 2 character edit(s) → excess +0.1538

## 5. Source records

Full responses, per-model scores and record IDs are in the JSON file next to this report.

- `qwen/qwen3.8-27b|LOGIC-003|treatment|word_deletion|1`: anchor record `5abd1999-e8e4-4ad6-90ce-0e267cf7f4d8`, comparison record `a17aaa5b-848c-42bb-99ac-5f55c01e1947`
- `openai/gpt-oss-120b|LOGIC-003|treatment|word_deletion|1`: anchor record `d8116b1c-821b-4346-876a-aa720cea394f`, comparison record `3116ec0a-de32-47d7-ad75-5475be858821`
- `openai/gpt-oss-20b|LOGIC-003|treatment|word_deletion|1`: anchor record `e27d9fce-d9c4-47bc-968f-ec47e29dfd98`, comparison record `13011fd0-78fe-4505-b3f7-e778f1e01e39`
- `allam-2-7b|LOGIC-003|treatment|word_deletion|1`: anchor record `0ba027b8-1522-4826-8544-f66541ef8d57`, comparison record `8fb62896-dcda-4bbc-8542-d1d1dc47e254`
- `gemini-3.1-flash-lite|LOGIC-003|treatment|word_deletion|1`: anchor record `7b344ead-a492-4c18-940a-07c0e71a1947`, comparison record `e0e19df8-b2af-49fa-9a34-2849a6cf3447`
