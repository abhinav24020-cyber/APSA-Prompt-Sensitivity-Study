# Perturbation operator result — CODE-001 · Code generation

**Status** selected · **Rule** budget mode, maximum input distance 0.10 · **Model scope** fixed panel of 5 models, equal weights · **Evidence** retrospective

**Category source** dataset. Python string reversal without slice step

**Original prompt** Write a Python function reverse_string(s: str) -&gt; str that returns the reversed string without using Python&#x27;s built-in slice step [::-1] or reversed().

## Category recommendation

**word_insertion** (exploratory (main_v1 discovery ranking)). Source: category_operator_rankings.csv (code_generation, budget 0.10).

Category score 0.0386, coverage 10/10 complete prompts.

A leading tone cue ('Carefully') can change which implementation the model writes while preserving the signature and input/output contract.

## Measured result for this prompt

word_insertion produced the largest control-adjusted change (+0.0303) among 6 eligible, measured edits within budget 0.10. The gap to word_deletion (+0.0221) was +0.0083. Preservation evidence: not flagged by the retrospective audit (operator audited by a sample of 5 candidates).

**Exact edit** <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27;Carefully &#x27;</code></ins>

**Edited prompt** Carefully Write a Python function reverse_string(s: str) -&gt; str that returns the reversed string without using Python&#x27;s built-in slice step [::-1] or reversed().

**Input distance** 10 Levenshtein character edits / 161 characters in the longer prompt = **0.0621**.

**Comparison with word_deletion** +0.0303 − (+0.0221) = +0.0083 in excess distance. The selected edit uses 10 character edit(s) and the rival uses 4.

### Raw output distance and unchanged controls

The raw output distance is the study’s clipped 1 − cosine between response embeddings. Excess is raw distance minus the mean of the unchanged repeats. Calculations use full-precision values.

| Model | Raw distance | Mean of unchanged repeats | Excess |
|---|---:|---:|---:|
| Qwen 3.8 27B | 0.0000 | (0.0000 + 0.0000) / 2 = 0.0000 | 0.0000 − 0.0000 = **+0.0000** |
| GPT-OSS-120B | 0.0634 | (0.0000 + 0.0000) / 2 = 0.0000 | 0.0634 − 0.0000 = **+0.0634** |
| GPT-OSS-20B | 0.0759 | (0.0000 + 0.0000) / 2 = 0.0000 | 0.0759 − 0.0000 = **+0.0759** |
| ALLaM-2-7B | 0.0119 | (0.0000 + 0.0000) / 2 = 0.0000 | 0.0119 − 0.0000 = **+0.0119** |
| Gemini 3.1 Flash-Lite | 0.0004 | (0.0000 + 0.0000) / 2 = 0.0000 | 0.0004 − 0.0000 = **+0.0004** |

**Equal-weight panel excess** [(+0.0000) + (+0.0634) + (+0.0759) + (+0.0119) + (+0.0004)] / 5 = **+0.0303**.

### Responses for GPT-OSS-20B

correct → correct (unit tests); response length 243 → 268 characters.
Normalized final answers (original → perturbed) unavailable → unavailable.

<table><thead><tr><th>Original response</th><th>Perturbed response</th></tr></thead><tbody>
<tr><td><pre>```python
def reverse_string(s: str) -&gt; str:
    &quot;&quot;&quot;Return the reversed string without using slice step or reversed().&quot;&quot;&quot;
    result = []
    for i in range(len(s) - 1, -1, -1):
        result.append(s[i])
    return &#x27;&#x27;.join(result)
```</pre></td><td><pre>```python
def reverse_string(s: str) -&gt; str:
    &quot;&quot;&quot;
    Return the reversed string of `s` without using slicing or reversed().
    &quot;&quot;&quot;
    result = []
    for char in s:
        result.insert(0, char)   # prepend each character
    return &#x27;&#x27;.join(result)
```</pre></td></tr>
</tbody></table>

Exploratory measurement from stored main_v1 outputs.

## All operators

| Operator | Eligibility and reason | Measurement | Exact edit | Edits | Input distance | Raw | Control | Excess | Correctness (before → after) |
|---|---|---|---|---:|---:|---:|---:|---:|---|
| `char_substitution` | meaning_changing. retrospective audit flag: specification_changed | excluded | <del><code>&#x27;s&#x27;</code></del> → <ins><code>&#x27;5&#x27;</code></ins> | 1 | 0.0066 |  |  |  |  |
| `capitalization` | eligible. not flagged by the retrospective audit (operator audited by a sample of 5 candidates) | measured | <del><code>&#x27;W&#x27;</code></del> → <ins><code>&#x27;w&#x27;</code></ins> | 1 | 0.0066 | 0.0148 | 0.0000 | +0.0148 | Qwen 3.8 27B correct → correct, GPT-OSS-120B correct → correct, GPT-OSS-20B correct → correct, ALLaM-2-7B incorrect → incorrect, Gemini 3.1 Flash-Lite correct → correct |
| `punctuation` | eligible. not flagged by the retrospective audit (operator audited by a sample of 5 candidates) | measured | <del><code>&#x27;.&#x27;</code></del> → <ins><code>&#x27;&#x27;</code></ins> | 1 | 0.0066 | 0.0128 | 0.0000 | +0.0128 | Qwen 3.8 27B correct → correct, GPT-OSS-120B correct → correct, GPT-OSS-20B correct → correct, ALLaM-2-7B incorrect → correct, Gemini 3.1 Flash-Lite correct → correct |
| `whitespace` | over_budget. d_in_char 0.1221 exceeds budget 0.10 | excluded | <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins> | 21 | 0.1221 |  |  |  |  |
| `word_insertion` **(selected)** | eligible. not flagged by the retrospective audit (operator audited by a sample of 5 candidates) | measured | <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27;Carefully &#x27;</code></ins> | 10 | 0.0621 | 0.0303 | 0.0000 | +0.0303 | Qwen 3.8 27B correct → correct, GPT-OSS-120B correct → correct, GPT-OSS-20B correct → correct, ALLaM-2-7B incorrect → correct, Gemini 3.1 Flash-Lite correct → correct |
| `word_deletion` | eligible. not flagged by the retrospective audit (every candidate of this operator was audited) | measured | <del><code>&#x27; the&#x27;</code></del> → <ins><code>&#x27;&#x27;</code></ins> | 4 | 0.0265 | 0.0221 | 0.0000 | +0.0221 | Qwen 3.8 27B correct → correct, GPT-OSS-120B correct → correct, GPT-OSS-20B correct → correct, ALLaM-2-7B incorrect → incorrect, Gemini 3.1 Flash-Lite correct → correct |
| `synonym` | eligible. not flagged by the retrospective audit (every candidate of this operator was audited) | measured | <del><code>&#x27;f&#x27;</code></del> → <ins><code>&#x27;proced&#x27;</code></ins>, <del><code>&#x27;nction&#x27;</code></del> → <ins><code>&#x27;re&#x27;</code></ins> | 8 | 0.0526 | 0.0134 | 0.0000 | +0.0134 | Qwen 3.8 27B correct → correct, GPT-OSS-120B correct → correct, GPT-OSS-20B correct → correct, ALLaM-2-7B incorrect → incorrect, Gemini 3.1 Flash-Lite correct → correct |
| `word_substitution` | eligible. not flagged by the retrospective audit (every candidate of this operator was audited) | measured | <del><code>&#x27;W&#x27;</code></del> → <ins><code>&#x27;C&#x27;</code></ins>, <del><code>&#x27;i&#x27;</code></del> → <ins><code>&#x27;ea&#x27;</code></ins> | 3 | 0.0197 | 0.0177 | 0.0000 | +0.0177 | Qwen 3.8 27B correct → correct, GPT-OSS-120B correct → correct, GPT-OSS-20B correct → correct, ALLaM-2-7B incorrect → correct, Gemini 3.1 Flash-Lite correct → correct |
| `instruction_reordering` | inapplicable. inapplicable_or_no_op | excluded |  |  |  |  |  |  |  |
| `random_edit` | noise_benchmark. Noise benchmark only. Preservation: unaudited. | measured | <del><code>&#x27;r&#x27;</code></del> → <ins><code>&#x27;&#x27;</code></ins>, <del><code>&#x27;r&#x27;</code></del> → <ins><code>&#x27;h&#x27;</code></ins> | 2 | 0.0132 | 0.0475 | 0.0000 | +0.0475 | Qwen 3.8 27B correct → correct, GPT-OSS-120B correct → correct, GPT-OSS-20B correct → correct, ALLaM-2-7B incorrect → incorrect, Gemini 3.1 Flash-Lite correct → correct |

## Input–output trade-off

Each edit below is on the frontier of character edit count and excess distance.

- `capitalization` · 1 character edit(s) · excess +0.0148
- `word_substitution` · 3 character edit(s) · excess +0.0177
- `word_deletion` · 4 character edit(s) · excess +0.0221
- `word_insertion` · 10 character edit(s) · excess +0.0303

## Source records

The JSON record next to this report contains full responses, per-model scores, candidate IDs, and the treatment and control pair IDs with their generation IDs.
