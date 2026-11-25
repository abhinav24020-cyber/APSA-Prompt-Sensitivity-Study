# Perturbation operator result — QA-001 · Question answering

**Status** selected · **Rule** budget mode, maximum input distance 0.10 · **Model scope** fixed panel of 5 models, equal weights · **Evidence** retrospective

**Category source** dataset. Physics Nobel prize discovery query

**Original prompt** Which physicist received the Nobel Prize in Physics in 1921 for his discovery of the law of the photoelectric effect?

## Category recommendation

**punctuation** (exploratory (main_v1 discovery ranking)). Source: category_operator_rankings.csv (question_answering, budget 0.10).

Category score 0.0426, coverage 10/10 complete prompts.

Editing the question's final delimiter can change the form or length of the answer while keeping the requested fact fixed.

## Measured result for this prompt

punctuation produced the largest control-adjusted change (+0.0225) among 5 eligible, measured edits within budget 0.10. The gap to word_deletion (+0.0105) was +0.0120. Preservation evidence: not flagged by the retrospective audit (operator audited by a sample of 5 candidates).

**Exact edit** <del><code>&#x27;?&#x27;</code></del> → <ins><code>&#x27;&#x27;</code></ins>

**Edited prompt** Which physicist received the Nobel Prize in Physics in 1921 for his discovery of the law of the photoelectric effect

**Input distance** 1 Levenshtein character edits / 117 characters in the longer prompt = **0.0085**.

**Comparison with word_deletion** +0.0225 − (+0.0105) = +0.0120 in excess distance. The selected edit uses 1 character edit(s) and the rival uses 4.

### Raw output distance and unchanged controls

The raw output distance is the study’s clipped 1 − cosine between response embeddings. Excess is raw distance minus the mean of the unchanged repeats. Calculations use full-precision values.

| Model | Raw distance | Mean of unchanged repeats | Excess |
|---|---:|---:|---:|
| Qwen 3.8 27B | 0.0000 | (0.0000 + 0.0000) / 2 = 0.0000 | 0.0000 − 0.0000 = **+0.0000** |
| GPT-OSS-120B | 0.0000 | (0.0000 + 0.0000) / 2 = 0.0000 | 0.0000 − 0.0000 = **+0.0000** |
| GPT-OSS-20B | 0.0000 | (0.0000 + 0.0000) / 2 = 0.0000 | 0.0000 − 0.0000 = **+0.0000** |
| ALLaM-2-7B | 0.1125 | (0.0000 + 0.0000) / 2 = 0.0000 | 0.1125 − 0.0000 = **+0.1125** |
| Gemini 3.1 Flash-Lite | 0.0000 | (0.0000 + 0.0000) / 2 = 0.0000 | 0.0000 − 0.0000 = **+0.0000** |

**Equal-weight panel excess** [(+0.0000) + (+0.0000) + (+0.0000) + (+0.1125) + (+0.0000)] / 5 = **+0.0225**.

### Responses for ALLaM-2-7B

correct → incorrect; final answer text changed; response length 172 → 172 characters.
Normalized final answers (original → perturbed) alberteinsteinalberteinsteinisthephysicistwhoreceivedthenobelprizeinphysicsin1921forhisdiscoveryofthelawofthephotoelectriceffect → wernerheisenberg.

<table><thead><tr><th>Original response</th><th>Perturbed response</th></tr></thead><tbody>
<tr><td><pre>Final answer: Albert Einstein

Albert Einstein is the physicist who received the Nobel Prize in Physics in 1921 for his discovery of the law of the photoelectric effect. </pre></td><td><pre>The physicist who received the Nobel Prize in Physics in 1921 for discovering the law of the photoelectric effect is Werner Heisenberg. 

Final answer: Werner Heisenberg </pre></td></tr>
</tbody></table>

Exploratory measurement from stored main_v1 outputs.

## All operators

| Operator | Eligibility and reason | Measurement | Exact edit | Edits | Input distance | Raw | Control | Excess | Correctness (before → after) |
|---|---|---|---|---:|---:|---:|---:|---:|---|
| `char_substitution` | eligible. not flagged by the retrospective audit (every candidate of this operator was audited) | measured | <del><code>&#x27;t&#x27;</code></del> → <ins><code>&#x27;+&#x27;</code></ins> | 1 | 0.0085 | 0.0006 | 0.0000 | +0.0006 | Qwen 3.8 27B correct → correct, GPT-OSS-120B correct → correct, GPT-OSS-20B correct → correct, ALLaM-2-7B correct → correct, Gemini 3.1 Flash-Lite correct → correct |
| `capitalization` | eligible. not flagged by the retrospective audit (operator audited by a sample of 5 candidates) | measured | <del><code>&#x27;W&#x27;</code></del> → <ins><code>&#x27;w&#x27;</code></ins> | 1 | 0.0085 | 0.0006 | 0.0000 | +0.0006 | Qwen 3.8 27B correct → correct, GPT-OSS-120B correct → correct, GPT-OSS-20B correct → correct, ALLaM-2-7B correct → correct, Gemini 3.1 Flash-Lite correct → correct |
| `punctuation` **(selected)** | eligible. not flagged by the retrospective audit (operator audited by a sample of 5 candidates) | measured | <del><code>&#x27;?&#x27;</code></del> → <ins><code>&#x27;&#x27;</code></ins> | 1 | 0.0085 | 0.0225 | 0.0000 | +0.0225 | Qwen 3.8 27B correct → correct, GPT-OSS-120B correct → correct, GPT-OSS-20B correct → correct, ALLaM-2-7B correct → incorrect, Gemini 3.1 Flash-Lite correct → correct |
| `whitespace` | over_budget. d_in_char 0.1397 exceeds budget 0.10 | excluded | <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins> | 19 | 0.1397 |  |  |  |  |
| `word_insertion` | eligible. not flagged by the retrospective audit (operator audited by a sample of 5 candidates) | measured | <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27;Carefully &#x27;</code></ins> | 10 | 0.0787 | 0.0055 | 0.0000 | +0.0055 | Qwen 3.8 27B correct → correct, GPT-OSS-120B correct → correct, GPT-OSS-20B correct → correct, ALLaM-2-7B correct → correct, Gemini 3.1 Flash-Lite correct → correct |
| `word_deletion` | eligible. not flagged by the retrospective audit (every candidate of this operator was audited) | measured | <del><code>&#x27; the&#x27;</code></del> → <ins><code>&#x27;&#x27;</code></ins> | 4 | 0.0342 | 0.0105 | 0.0000 | +0.0105 | Qwen 3.8 27B correct → correct, GPT-OSS-120B correct → correct, GPT-OSS-20B correct → correct, ALLaM-2-7B correct → correct, Gemini 3.1 Flash-Lite correct → correct |
| `synonym` | inapplicable. inapplicable_or_no_op | excluded |  |  |  |  |  |  |  |
| `word_substitution` | inapplicable. inapplicable_or_no_op | excluded |  |  |  |  |  |  |  |
| `instruction_reordering` | inapplicable. inapplicable_or_no_op | excluded |  |  |  |  |  |  |  |
| `random_edit` | noise_benchmark. Noise benchmark only. Preservation: unaudited. | measured | <del><code>&#x27;t&#x27;</code></del> → <ins><code>&#x27;&#x27;</code></ins>, <del><code>&#x27; &#x27;</code></del> → <ins><code>&#x27;i&#x27;</code></ins> | 2 | 0.0171 | 0.0142 | 0.0000 | +0.0142 | Qwen 3.8 27B correct → correct, GPT-OSS-120B correct → correct, GPT-OSS-20B correct → correct, ALLaM-2-7B correct → correct, Gemini 3.1 Flash-Lite correct → correct |

## Input–output trade-off

Each edit below is on the frontier of character edit count and excess distance.

- `punctuation` · 1 character edit(s) · excess +0.0225

## Source records

The JSON record next to this report contains full responses, per-model scores, candidate IDs, and the treatment and control pair IDs with their generation IDs.
