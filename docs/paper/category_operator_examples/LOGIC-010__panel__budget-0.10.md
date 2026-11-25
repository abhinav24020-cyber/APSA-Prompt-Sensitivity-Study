# Perturbation operator result — LOGIC-010 · Logical reasoning

**Status** selected · **Rule** budget mode, maximum input distance 0.10 · **Model scope** fixed panel of 5 models, equal weights · **Evidence** retrospective

**Category source** dataset. Material implication truth value evaluation

**Original prompt** Determine the truth value of (P implies Q) when P is False and Q is False.

## Category recommendation

**punctuation** (exploratory (main_v1 discovery ranking)). Source: category_operator_rankings.csv (logical_reasoning, budget 0.10).

Category score 0.0744, coverage 9/9 complete prompts.

A terminal punctuation edit changes the cue at the end of the prompt while leaving premises and the requested conclusion intact.

## Measured result for this prompt

punctuation produced the largest control-adjusted change (+0.2891) among 5 eligible, measured edits within budget 0.10. The gap to char_substitution (+0.1798) was +0.1093. Preservation evidence: not flagged by the retrospective audit (operator audited by a sample of 5 candidates).

**Exact edit** <del><code>&#x27;.&#x27;</code></del> → <ins><code>&#x27;&#x27;</code></ins>

**Edited prompt** Determine the truth value of (P implies Q) when P is False and Q is False

**Input distance** 1 Levenshtein character edits / 74 characters in the longer prompt = **0.0135**.

**Comparison with char_substitution** +0.2891 − (+0.1798) = +0.1093 in excess distance. The selected edit uses 1 character edit(s) and the rival uses 1.

### Raw output distance and unchanged controls

The raw output distance is the study’s clipped 1 − cosine between response embeddings. Excess is raw distance minus the mean of the unchanged repeats. Calculations use full-precision values.

| Model | Raw distance | Mean of unchanged repeats | Excess |
|---|---:|---:|---:|
| Qwen 3.8 27B | 0.1967 | (0.0000 + 0.0000) / 2 = 0.0000 | 0.1967 − 0.0000 = **+0.1967** |
| GPT-OSS-120B | 0.7999 | (0.0000 + 0.0000) / 2 = 0.0000 | 0.7999 − 0.0000 = **+0.7999** |
| GPT-OSS-20B | 0.0000 | (0.0000 + 0.0000) / 2 = 0.0000 | 0.0000 − 0.0000 = **+0.0000** |
| ALLaM-2-7B | 0.1769 | (0.0000 + 0.0000) / 2 = 0.0000 | 0.1769 − 0.0000 = **+0.1769** |
| Gemini 3.1 Flash-Lite | 0.2719 | (0.0000 + 0.0000) / 2 = 0.0000 | 0.2719 − 0.0000 = **+0.2719** |

**Equal-weight panel excess** [(+0.1967) + (+0.7999) + (+0.0000) + (+0.1769) + (+0.2719)] / 5 = **+0.2891**.

### Responses for GPT-OSS-120B

correct → correct; same final answer; response length 209 → 18 characters.
Normalized final answers (original → perturbed) true → true.

<table><thead><tr><th>Original response</th><th>Perturbed response</th></tr></thead><tbody>
<tr><td><pre>The implication \(P \rightarrow Q\) is true whenever the antecedent \(P\) is false, regardless of the truth value of \(Q\). Since \(P\) is false and \(Q\) is false, the statement is true.

Final answer: True</pre></td><td><pre>Final answer: True</pre></td></tr>
</tbody></table>

Exploratory measurement from stored main_v1 outputs.

## All operators

| Operator | Eligibility and reason | Measurement | Exact edit | Edits | Input distance | Raw | Control | Excess | Correctness (before → after) |
|---|---|---|---|---:|---:|---:|---:|---:|---|
| `char_substitution` | eligible. not flagged by the retrospective audit (every candidate of this operator was audited) | measured | <del><code>&#x27;e&#x27;</code></del> → <ins><code>&#x27;3&#x27;</code></ins> | 1 | 0.0135 | 0.1798 | 0.0000 | +0.1798 | Qwen 3.8 27B correct → correct, GPT-OSS-120B correct → correct, GPT-OSS-20B correct → correct, ALLaM-2-7B incorrect → incorrect, Gemini 3.1 Flash-Lite correct → correct |
| `capitalization` | eligible. not flagged by the retrospective audit (operator audited by a sample of 5 candidates) | measured | <del><code>&#x27;D&#x27;</code></del> → <ins><code>&#x27;d&#x27;</code></ins> | 1 | 0.0135 | 0.1484 | 0.0000 | +0.1484 | Qwen 3.8 27B correct → correct, GPT-OSS-120B correct → correct, GPT-OSS-20B correct → correct, ALLaM-2-7B incorrect → incorrect, Gemini 3.1 Flash-Lite correct → correct |
| `punctuation` **(selected)** | eligible. not flagged by the retrospective audit (operator audited by a sample of 5 candidates) | measured | <del><code>&#x27;.&#x27;</code></del> → <ins><code>&#x27;&#x27;</code></ins> | 1 | 0.0135 | 0.2891 | 0.0000 | +0.2891 | Qwen 3.8 27B correct → correct, GPT-OSS-120B correct → correct, GPT-OSS-20B correct → correct, ALLaM-2-7B incorrect → correct, Gemini 3.1 Flash-Lite correct → correct |
| `whitespace` | over_budget. d_in_char 0.1685 exceeds budget 0.10 | excluded | <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins> | 15 | 0.1685 |  |  |  |  |
| `word_insertion` | over_budget. d_in_char 0.1190 exceeds budget 0.10 | excluded | <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27;Carefully &#x27;</code></ins> | 10 | 0.1190 |  |  |  |  |
| `word_deletion` | eligible. not flagged by the retrospective audit (every candidate of this operator was audited) | measured | <del><code>&#x27;e th&#x27;</code></del> → <ins><code>&#x27;&#x27;</code></ins> | 4 | 0.0541 | 0.0359 | 0.0000 | +0.0359 | Qwen 3.8 27B correct → correct, GPT-OSS-120B correct → correct, GPT-OSS-20B correct → correct, ALLaM-2-7B incorrect → incorrect, Gemini 3.1 Flash-Lite correct → correct |
| `synonym` | eligible. not flagged by the retrospective audit (every candidate of this operator was audited) | measured | <del><code>&#x27;De&#x27;</code></del> → <ins><code>&#x27;Es&#x27;</code></ins>, <del><code>&#x27;erm&#x27;</code></del> → <ins><code>&#x27;abl&#x27;</code></ins>, <del><code>&#x27;ne&#x27;</code></del> → <ins><code>&#x27;sh&#x27;</code></ins> | 7 | 0.0946 | 0.1693 | 0.0000 | +0.1693 | Qwen 3.8 27B correct → correct, GPT-OSS-120B correct → correct, GPT-OSS-20B correct → correct, ALLaM-2-7B incorrect → incorrect, Gemini 3.1 Flash-Lite correct → correct |
| `word_substitution` | meaning_changing. retrospective audit flag: question_changed | excluded | <del><code>&#x27;Fals&#x27;</code></del> → <ins><code>&#x27;Tru&#x27;</code></ins> | 4 | 0.0541 |  |  |  |  |
| `instruction_reordering` | inapplicable. inapplicable_or_no_op | excluded |  |  |  |  |  |  |  |
| `random_edit` | noise_benchmark. Noise benchmark only. Preservation: unaudited. | measured | <del><code>&#x27;t&#x27;</code></del> → <ins><code>&#x27;&#x27;</code></ins>, <del><code>&#x27;i&#x27;</code></del> → <ins><code>&#x27;h&#x27;</code></ins> | 2 | 0.0270 | 0.2866 | 0.0000 | +0.2866 | Qwen 3.8 27B correct → correct, GPT-OSS-120B correct → correct, GPT-OSS-20B correct → correct, ALLaM-2-7B incorrect → incorrect, Gemini 3.1 Flash-Lite correct → correct |

## Input–output trade-off

Each edit below is on the frontier of character edit count and excess distance.

- `punctuation` · 1 character edit(s) · excess +0.2891

## Source records

The JSON record next to this report contains full responses, per-model scores, candidate IDs, and the treatment and control pair IDs with their generation IDs.
