# Perturbation operator result — MATH-001 · Mathematical reasoning

**Status** selected · **Rule** budget mode, maximum input distance 0.10 · **Model scope** fixed panel of 5 models, equal weights · **Evidence** retrospective

**Category source** dataset. Multi-step arithmetic ratio and percentage calculation

**Original prompt** A store sells apples in bags of 5 for $3.00. On Tuesday, they offer a 20% discount on all apple bags. If a customer buys 15 apples on Tuesday, how much do they pay in total?

## Category recommendation

**char_substitution** (exploratory (main_v1 discovery ranking)). Source: category_operator_rankings.csv (mathematical_reasoning, budget 0.10).

Category score 0.0853, coverage 8/8 complete prompts.

A typo in prose changes how the task is rendered while leaving quantities and the requested result intact.

## Measured result for this prompt

char_substitution produced the largest control-adjusted change (+0.0463) among 5 eligible, measured edits within budget 0.10. The gap to word_insertion (+0.0449) was +0.0013. Preservation evidence: not flagged by the retrospective audit (every candidate of this operator was audited).

**Exact edit** <del><code>&#x27;b&#x27;</code></del> → <ins><code>&#x27;6&#x27;</code></ins>

**Edited prompt** A store sells apples in 6ags of 5 for $3.00. On Tuesday, they offer a 20% discount on all apple bags. If a customer buys 15 apples on Tuesday, how much do they pay in total?

**Input distance** 1 Levenshtein character edits / 173 characters in the longer prompt = **0.0058**.

**Comparison with word_insertion** +0.0463 − (+0.0449) = +0.0013 in excess distance. The selected edit uses 1 character edit(s) and the rival uses 10.

### Raw output distance and unchanged controls

The raw output distance is the study’s clipped 1 − cosine between response embeddings. Excess is raw distance minus the mean of the unchanged repeats. Calculations use full-precision values.

| Model | Raw distance | Mean of unchanged repeats | Excess |
|---|---:|---:|---:|
| Qwen 3.8 27B | 0.0919 | (0.0000 + 0.0000) / 2 = 0.0000 | 0.0919 − 0.0000 = **+0.0919** |
| GPT-OSS-120B | 0.0530 | (0.0000 + 0.0000) / 2 = 0.0000 | 0.0530 − 0.0000 = **+0.0530** |
| GPT-OSS-20B | 0.0000 | (0.0000 + 0.0000) / 2 = 0.0000 | 0.0000 − 0.0000 = **+0.0000** |
| ALLaM-2-7B | 0.0848 | (0.0020 + 0.0000) / 2 = 0.0010 | 0.0848 − 0.0010 = **+0.0838** |
| Gemini 3.1 Flash-Lite | 0.0026 | (0.0000 + 0.0000) / 2 = 0.0000 | 0.0026 − 0.0000 = **+0.0026** |

**Equal-weight panel excess** [(+0.0919) + (+0.0530) + (+0.0000) + (+0.0838) + (+0.0026)] / 5 = **+0.0463**.

### Responses for Qwen 3.8 27B

correct → correct; same final answer; response length 1013 → 1329 characters.
Normalized final answers (original → perturbed) 7.20 → 7.20.

<table><thead><tr><th>Original response</th><th>Perturbed response</th></tr></thead><tbody>
<tr><td><pre>To determine the total cost, we need to calculate the number of bags required and apply the discount.

1.  **Calculate the number of bags needed:**
    The customer buys 15 apples, and each bag contains 5 apples.
    $$ \text{Number of bags} = \frac{15 \text{ apples}}{5 \text{ apples/bag}} = 3 \text{ bags} $$

2.  **Calculate the original total cost:**
    Each bag costs $\$3.00$.
    $$ \text{Original Cost} = 3 \text{ bags} \times \$3.00/\text{bag} = \$9.00 $$

3.  **Apply the discount:**
    The store offers a 20% discount on Tuesday.
    $$ \text{Discount Amount} = \$9.00 \times 0.20 = \$1.80 $$
    $$ \text{Final Price} = \text{Original Cost} - \text{Discount Amount} $$
    $$ \text{Final Price} = \$9.00 - \$1.80 = \$7.20 $$

Alternatively, you can calculate the discounted price per bag:
$$ \text{Discounted Price per Bag} = \$3.00 \times (1 - 0.20) = \$3.00 \times 0.80 = \$2.40 $$
$$ \text{Total Cost} = 3 \text{ bags} \times \$2.40/\text{bag} = \$7.20 $$

Final answer: $7.20</pre></td><td><pre>To determine the total cost, we need to calculate the price per apple, apply the discount, and then multiply by the number of apples purchased.

**Step 1: Determine the original price per apple.**
The store sells 5 apples for $3.00.
$$ \text{Price per apple} = \frac{\$3.00}{5} = \$0.60 $$

**Step 2: Calculate the discounted price per apple.**
On Tuesday, there is a 20% discount.
$$ \text{Discount amount} = \$0.60 \times 0.20 = \$0.12 $$
$$ \text{Discounted price per apple} = \$0.60 - \$0.12 = \$0.48 $$

Alternatively, you can calculate the discounted price directly:
$$ \text{Discounted price per apple} = \$0.60 \times (1 - 0.20) = \$0.60 \times 0.80 = \$0.48 $$

**Step 3: Calculate the total cost for 15 apples.**
The customer buys 15 apples at the discounted price.
$$ \text{Total Cost} = 15 \times \$0.48 $$

Calculation:
$$ 15 \times 0.48 = 15 \times \left(\frac{48}{100}\right) = \frac{720}{100} = 7.20 $$

So, the total cost is $7.20.

**Alternative Method:**
1. Calculate the original cost for 15 apples:
   Since 5 apples cost $3.00, 15 apples (which is 3 sets of 5) would cost:
   $$ 3 \times \$3.00 = \$9.00 $$
2. Apply the 20% discount to the total:
   $$ \text{Discount} = \$9.00 \times 0.20 = \$1.80 $$
   $$ \text{Total Cost} = \$9.00 - \$1.80 = \$7.20 $$

Final answer: $7.20</pre></td></tr>
</tbody></table>

Exploratory measurement from stored main_v1 outputs.

## All operators

| Operator | Eligibility and reason | Measurement | Exact edit | Edits | Input distance | Raw | Control | Excess | Correctness (before → after) |
|---|---|---|---|---:|---:|---:|---:|---:|---|
| `char_substitution` **(selected)** | eligible. not flagged by the retrospective audit (every candidate of this operator was audited) | measured | <del><code>&#x27;b&#x27;</code></del> → <ins><code>&#x27;6&#x27;</code></ins> | 1 | 0.0058 | 0.0465 | 0.0002 | +0.0463 | Qwen 3.8 27B correct → correct, GPT-OSS-120B correct → correct, GPT-OSS-20B correct → correct, ALLaM-2-7B correct → incorrect, Gemini 3.1 Flash-Lite correct → correct |
| `capitalization` | eligible. not flagged by the retrospective audit (operator audited by a sample of 5 candidates) | measured | <del><code>&#x27;A&#x27;</code></del> → <ins><code>&#x27;a&#x27;</code></ins> | 1 | 0.0058 | 0.0262 | 0.0002 | +0.0260 | Qwen 3.8 27B correct → correct, GPT-OSS-120B correct → correct, GPT-OSS-20B correct → correct, ALLaM-2-7B correct → incorrect, Gemini 3.1 Flash-Lite correct → correct |
| `punctuation` | eligible. not flagged by the retrospective audit (operator audited by a sample of 5 candidates) | measured | <del><code>&#x27;?&#x27;</code></del> → <ins><code>&#x27;&#x27;</code></ins> | 1 | 0.0058 | 0.0172 | 0.0002 | +0.0170 | Qwen 3.8 27B correct → correct, GPT-OSS-120B correct → correct, GPT-OSS-20B correct → correct, ALLaM-2-7B correct → incorrect, Gemini 3.1 Flash-Lite correct → correct |
| `whitespace` | over_budget. d_in_char 0.1683 exceeds budget 0.10 | excluded | <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins> | 35 | 0.1683 |  |  |  |  |
| `word_insertion` | eligible. not flagged by the retrospective audit (operator audited by a sample of 5 candidates) | measured | <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27;Carefully &#x27;</code></ins> | 10 | 0.0546 | 0.0451 | 0.0002 | +0.0449 | Qwen 3.8 27B correct → correct, GPT-OSS-120B correct → correct, GPT-OSS-20B correct → correct, ALLaM-2-7B correct → correct, Gemini 3.1 Flash-Lite correct → correct |
| `word_deletion` | eligible. not flagged by the retrospective audit (every candidate of this operator was audited) | measured | <del><code>&#x27;A &#x27;</code></del> → <ins><code>&#x27;&#x27;</code></ins> | 2 | 0.0116 | 0.0343 | 0.0002 | +0.0341 | Qwen 3.8 27B correct → correct, GPT-OSS-120B correct → correct, GPT-OSS-20B correct → correct, ALLaM-2-7B correct → incorrect, Gemini 3.1 Flash-Lite correct → correct |
| `synonym` | inapplicable. inapplicable_or_no_op | excluded |  |  |  |  |  |  |  |
| `word_substitution` | inapplicable. inapplicable_or_no_op | excluded |  |  |  |  |  |  |  |
| `instruction_reordering` | over_budget. d_in_char 0.7283 exceeds budget 0.10 | excluded | <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27;If a customer buys 15 apples on Tuesday, how much do they pay in total? &#x27;</code></ins>, <del><code>&#x27; If a customer buys 15 apples on Tuesday, how much do they pay in total?&#x27;</code></del> → <ins><code>&#x27;&#x27;</code></ins> | 126 | 0.7283 |  |  |  |  |
| `random_edit` | noise_benchmark. Noise benchmark only. Preservation: unaudited. | measured | <del><code>&#x27; &#x27;</code></del> → <ins><code>&#x27;&#x27;</code></ins>, <del><code>&#x27;0&#x27;</code></del> → <ins><code>&#x27;h&#x27;</code></ins> | 2 | 0.0116 | 0.0891 | 0.0002 | +0.0889 | Qwen 3.8 27B correct → incorrect, GPT-OSS-120B correct → incorrect, GPT-OSS-20B correct → incorrect, ALLaM-2-7B correct → incorrect, Gemini 3.1 Flash-Lite correct → correct |

## Input–output trade-off

Each edit below is on the frontier of character edit count and excess distance.

- `char_substitution` · 1 character edit(s) · excess +0.0463

## Source records

The JSON record next to this report contains full responses, per-model scores, candidate IDs, and the treatment and control pair IDs with their generation IDs.
