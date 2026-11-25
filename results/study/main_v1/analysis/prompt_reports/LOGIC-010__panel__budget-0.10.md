# Perturbation operator result: LOGIC-010 · Logical reasoning

**Status:** `selected` · **Rule:** budget mode, d_in_char ≤ 0.10 · **Model scope:** fixed panel of 5 models, equal weights · **Evidence:** retrospective

## 1. Category recommendation

- Recommended: **punctuation** (exploratory (main_v1 discovery ranking); source: category_operator_rankings.csv (logical_reasoning, budget 0.10))
- Category score 0.0744, coverage 9/9 complete prompts
- Why: A terminal punctuation edit changes the cue at the end of the prompt while leaving premises and the requested conclusion intact.
- A category recommendation is not a measurement of this prompt; the measured result follows.

## 2. Measured result for this prompt

punctuation produced the largest control-adjusted change (+0.2891) among 5 eligible, measured edits within budget 0.10. The next best eligible edit was char_substitution (+0.1798). Preservation evidence: not flagged by the retrospective audit (operator audited by a sample of 5 candidates).

| Field | Result |
|---|---|
| Prompt and category | `LOGIC-010` · Logical reasoning |
| Original prompt | Determine the truth value of (P implies Q) when P is False and Q is False. |
| Perturbed prompt | Determine the truth value of (P implies Q) when P is False and Q is False |
| Operator | `punctuation`: `False.` → `False` |
| Input change | **1 character edit(s)**, normalised distance **0.0135**, semantic input distance 0.0100 |
| Model and comparison | fixed panel of 5 models, equal weights; 5 matched model–prompt pair(s) from `main_v1` |
| Output change | Semantic distance **0.2891**, mean unchanged control distance **0.0000**, excess distance **+0.2891** |
| Functional result | Qwen 3.8 27B: correct → correct; same final answer; response length 742 → 711 characters; GPT-OSS-120B: correct → correct; same final answer; response length 207 → 18 characters; GPT-OSS-20B: correct → correct; same final answer; response length 24 → 24 characters; ALLaM-2-7B: incorrect → correct; final answer text changed; response length 423 → 135 characters; Gemini 3.1 Flash-Lite: correct → correct; same final answer; response length 285 → 396 characters |
| Tie status | unique |
| Evidence status | Measured retrospectively from stored main_v1 outputs; this prompt belongs to the discovery set that produced the category ranking, so the result is exploratory. |

### Responses of GPT-OSS-120B (largest effect in the panel)

**Original prompt response**

```text
The implication \(P \rightarrow Q\) is true whenever the antecedent \(P\) is false, regardless of the truth value of \(Q\). Since \(P\) is false and \(Q\) is false, the statement is true.

Final answer: True
```

**Perturbed prompt response**

```text
Final answer: True
```

## 3. All operators

| Operator | Status | Char edits | d_in_char | Raw | Control | Excess | Correctness (before → after) |
|---|---|---:|---:|---:|---:|---:|---|
| `punctuation` **(selected)** | measured | 1 | 0.0135 | 0.2891 | 0.0000 | +0.2891 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→correct; Gemini 3.1 Flash-Lite correct→correct |
| `char_substitution` | measured | 1 | 0.0135 | 0.1798 | 0.0000 | +0.1798 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→incorrect; Gemini 3.1 Flash-Lite correct→correct |
| `synonym` | measured | 7 | 0.0946 | 0.1693 | 0.0000 | +0.1693 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→incorrect; Gemini 3.1 Flash-Lite correct→correct |
| `capitalization` | measured | 1 | 0.0135 | 0.1484 | 0.0000 | +0.1484 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→incorrect; Gemini 3.1 Flash-Lite correct→correct |
| `word_deletion` | measured | 4 | 0.0541 | 0.0359 | 0.0000 | +0.0359 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→incorrect; Gemini 3.1 Flash-Lite correct→correct |
| `instruction_reordering` | inapplicable: inapplicable_or_no_op |  |  |  |  |  |  |
| `whitespace` | over_budget: d_in_char 0.1685 exceeds budget 0.10 | 15 | 0.1685 |  |  |  |  |
| `word_insertion` | over_budget: d_in_char 0.1190 exceeds budget 0.10 | 10 | 0.1190 |  |  |  |  |
| `word_substitution` | meaning_changing: retrospective audit flag: question_changed | 4 | 0.0541 |  |  |  |  |

## 4. Input–output trade-off

Eligible edits not dominated by another edit with no more character edits and at least as much excess change:

- `punctuation`: 1 character edit(s) → excess +0.2891

## 5. Source records

Full responses, per-model scores and record IDs are in the JSON file next to this report.

- `qwen/qwen3.8-27b|LOGIC-010|treatment|punctuation|1`: anchor record `36e9d000-f120-411d-a317-fe31caf54a80`, comparison record `e9615f3d-e3b6-4ebc-9e04-e4ee3b002955`
- `openai/gpt-oss-120b|LOGIC-010|treatment|punctuation|1`: anchor record `15a755a1-5066-4ab0-97ea-7b1f0f7cb659`, comparison record `066df468-8b4d-4a9c-a018-7b8cc741a97a`
- `openai/gpt-oss-20b|LOGIC-010|treatment|punctuation|1`: anchor record `ef4df79c-e3f1-431b-b4cb-16c4f989a861`, comparison record `e57df891-f9cc-4763-80d7-78638784360e`
- `allam-2-7b|LOGIC-010|treatment|punctuation|1`: anchor record `a145cf49-c279-4608-ab16-cd6d0e295a0d`, comparison record `0b427b36-7b1a-4ea0-8b1e-ded078489d51`
- `gemini-3.1-flash-lite|LOGIC-010|treatment|punctuation|1`: anchor record `a81a0a97-678c-496e-9ce8-be34fb85611c`, comparison record `15123a56-b380-487d-9185-8205f0b31fe5`
