# Perturbation operator result: LOGIC-010 · Logical reasoning

**Status:** `selected` · **Rule:** budget mode, d_in_char ≤ 0.10 · **Model scope:** GPT-OSS-120B (single model) · **Evidence:** retrospective

## 1. Category recommendation

- Recommended: **punctuation** (exploratory (main_v1 discovery ranking); source: category_operator_rankings.csv (logical_reasoning, budget 0.10))
- Category score 0.0744, coverage 9/9 complete prompts
- Why: A terminal punctuation edit changes the cue at the end of the prompt while leaving premises and the requested conclusion intact.
- A category recommendation is not a measurement of this prompt; the measured result follows.

## 2. Measured result for this prompt

punctuation produced the largest control-adjusted change (+0.7999) among 5 eligible, measured edits within budget 0.10. The next best eligible edit was char_substitution (+0.7611). Preservation evidence: not flagged by the retrospective audit (operator audited by a sample of 5 candidates).

| Field | Result |
|---|---|
| Prompt and category | `LOGIC-010` · Logical reasoning |
| Original prompt | Determine the truth value of (P implies Q) when P is False and Q is False. |
| Perturbed prompt | Determine the truth value of (P implies Q) when P is False and Q is False |
| Operator | `punctuation`: `False.` → `False` |
| Input change | **1 character edit(s)**, normalised distance **0.0135**, semantic input distance 0.0100 |
| Model and comparison | GPT-OSS-120B (single model); 1 matched model–prompt pair(s) from `main_v1` |
| Output change | Semantic distance **0.7999**, mean unchanged control distance **0.0000**, excess distance **+0.7999** |
| Functional result | GPT-OSS-120B: correct → correct; same final answer; response length 207 → 18 characters |
| Tie status | unique |
| Evidence status | Measured retrospectively from stored main_v1 outputs; this prompt belongs to the discovery set that produced the category ranking, so the result is exploratory. Largest observed raw distance among the 245 eligible logical reasoning results searched at budget 0.10. It is also the largest observed excess distance in the category at this budget. Separate 5-model panel result for LOGIC-010: punctuation led with mean excess +0.2891. The single-model case and the panel average are different quantities. |

### Response

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
| `punctuation` **(selected)** | measured | 1 | 0.0135 | 0.7999 | 0.0000 | +0.7999 | GPT-OSS-120B correct→correct |
| `char_substitution` | measured | 1 | 0.0135 | 0.7611 | 0.0000 | +0.7611 | GPT-OSS-120B correct→correct |
| `capitalization` | measured | 1 | 0.0135 | 0.0000 | 0.0000 | +0.0000 | GPT-OSS-120B correct→correct |
| `synonym` | measured | 7 | 0.0946 | 0.0000 | 0.0000 | +0.0000 | GPT-OSS-120B correct→correct |
| `word_deletion` | measured | 4 | 0.0541 | 0.0000 | 0.0000 | +0.0000 | GPT-OSS-120B correct→correct |
| `instruction_reordering` | inapplicable: inapplicable_or_no_op |  |  |  |  |  |  |
| `whitespace` | over_budget: d_in_char 0.1685 exceeds budget 0.10 | 15 | 0.1685 |  |  |  |  |
| `word_insertion` | over_budget: d_in_char 0.1190 exceeds budget 0.10 | 10 | 0.1190 |  |  |  |  |
| `word_substitution` | meaning_changing: retrospective audit flag: question_changed | 4 | 0.0541 |  |  |  |  |

## 4. Input–output trade-off

Eligible edits not dominated by another edit with no more character edits and at least as much excess change:

- `punctuation`: 1 character edit(s) → excess +0.7999

## 5. Source records

Full responses, per-model scores and record IDs are in the JSON file next to this report.

- `openai/gpt-oss-120b|LOGIC-010|treatment|punctuation|1`: anchor record `15a755a1-5066-4ab0-97ea-7b1f0f7cb659`, comparison record `066df468-8b4d-4a9c-a018-7b8cc741a97a`
