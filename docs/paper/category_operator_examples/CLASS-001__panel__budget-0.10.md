# Perturbation operator result — CLASS-001 · Classification

**Status** selected · **Rule** budget mode, maximum input distance 0.10 · **Model scope** fixed panel of 5 models, equal weights · **Evidence** retrospective

**Category source** dataset. Product review sentiment classification

**Original prompt** Classify the sentiment of the following product review as Positive, Negative, or Neutral: &#x27;The battery life is acceptable, but the screen scratches easily and customer support was unhelpful.&#x27;

## Category recommendation

**synonym** (exploratory (main_v1 discovery ranking)). Source: category_operator_rankings.csv (classification, budget 0.10).

Category score 0.0761, coverage 10/10 complete prompts.

Replacing an instruction verb (e.g. Classify -> Categorize) changes the cue used to request a label while preserving the label set and evidence.

## Measured result for this prompt

capitalization produced the largest control-adjusted change (+0.0950) among 6 eligible, measured edits within budget 0.10. The gap to synonym (+0.0846) was +0.0104. Preservation evidence: not flagged by the retrospective audit (operator audited by a sample of 5 candidates).

**Exact edit** <del><code>&#x27;C&#x27;</code></del> → <ins><code>&#x27;c&#x27;</code></ins>

**Edited prompt** classify the sentiment of the following product review as Positive, Negative, or Neutral: &#x27;The battery life is acceptable, but the screen scratches easily and customer support was unhelpful.&#x27;

**Input distance** 1 Levenshtein character edits / 191 characters in the longer prompt = **0.0052**.

**Comparison with synonym** +0.0950 − (+0.0846) = +0.0104 in excess distance. The selected edit uses 1 character edit(s) and the rival uses 8.

### Raw output distance and unchanged controls

The raw output distance is the study’s clipped 1 − cosine between response embeddings. Excess is raw distance minus the mean of the unchanged repeats. Calculations use full-precision values.

| Model | Raw distance | Mean of unchanged repeats | Excess |
|---|---:|---:|---:|
| Qwen 3.8 27B | 0.0803 | (0.0000 + 0.0000) / 2 = 0.0000 | 0.0803 − 0.0000 = **+0.0803** |
| GPT-OSS-120B | 0.0000 | (0.0000 + 0.0000) / 2 = 0.0000 | 0.0000 − 0.0000 = **+0.0000** |
| GPT-OSS-20B | 0.0000 | (0.0000 + 0.0000) / 2 = 0.0000 | 0.0000 − 0.0000 = **+0.0000** |
| ALLaM-2-7B | 0.3948 | (0.0000 + 0.0000) / 2 = 0.0000 | 0.3948 − 0.0000 = **+0.3948** |
| Gemini 3.1 Flash-Lite | 0.0000 | (0.0000 + 0.0000) / 2 = 0.0000 | 0.0000 − 0.0000 = **+0.0000** |

**Equal-weight panel excess** [(+0.0803) + (+0.0000) + (+0.0000) + (+0.3948) + (+0.0000)] / 5 = **+0.0950**.

### Responses for ALLaM-2-7B

incorrect → correct; final answer text changed; response length 427 → 162 characters.
Normalized final answers (original → perturbed) negativecodeimporttextblobreviewthebatterylifeisacceptablebutthescreenscratcheseasilyandcustomersupportwasunhelpfulsentimenttextblobtextblobreviewsentimentifsentimentpolarity0sentimentlabelnegativeeli → negativethesentimentofthereviewcanbeclassifiedasnegativeduetothementionofissueswithbatterylifescreenandcustomersupport.

<table><thead><tr><th>Original response</th><th>Perturbed response</th></tr></thead><tbody>
<tr><td><pre>Final answer: Negative

Code:
import textblob

review = &quot;The battery life is acceptable, but the screen scratches easily and customer support was unhelpful.&quot;
sentiment = textblob.TextBlob(review).sentiment

if sentiment.polarity &lt; 0:
    sentiment_label = &quot;Negative&quot;
elif sentiment.polarity == 0:
    sentiment_label = &quot;Neutral&quot;
else:
    sentiment_label = &quot;Positive&quot;

print(&quot;Sentiment label:&quot;, sentiment_label) </pre></td><td><pre>Final answer: Negative

The sentiment of the review can be classified as negative due to the mention of issues with battery life, screen, and customer support. </pre></td></tr>
</tbody></table>

Exploratory measurement from stored main_v1 outputs.

## All operators

| Operator | Eligibility and reason | Measurement | Exact edit | Edits | Input distance | Raw | Control | Excess | Correctness (before → after) |
|---|---|---|---|---:|---:|---:|---:|---:|---|
| `char_substitution` | eligible. not flagged by the retrospective audit (every candidate of this operator was audited) | measured | <del><code>&#x27;s&#x27;</code></del> → <ins><code>&#x27;5&#x27;</code></ins> | 1 | 0.0052 | 0.0446 | 0.0000 | +0.0446 | Qwen 3.8 27B correct → correct, GPT-OSS-120B correct → correct, GPT-OSS-20B correct → correct, ALLaM-2-7B incorrect → incorrect, Gemini 3.1 Flash-Lite correct → correct |
| `capitalization` **(selected)** | eligible. not flagged by the retrospective audit (operator audited by a sample of 5 candidates) | measured | <del><code>&#x27;C&#x27;</code></del> → <ins><code>&#x27;c&#x27;</code></ins> | 1 | 0.0052 | 0.0950 | 0.0000 | +0.0950 | Qwen 3.8 27B correct → correct, GPT-OSS-120B correct → correct, GPT-OSS-20B correct → correct, ALLaM-2-7B incorrect → correct, Gemini 3.1 Flash-Lite correct → correct |
| `punctuation` | eligible. not flagged by the retrospective audit (operator audited by a sample of 5 candidates) | measured | <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27;.&#x27;</code></ins> | 1 | 0.0052 | 0.0154 | 0.0000 | +0.0154 | Qwen 3.8 27B correct → correct, GPT-OSS-120B correct → correct, GPT-OSS-20B correct → correct, ALLaM-2-7B incorrect → incorrect, Gemini 3.1 Flash-Lite correct → correct |
| `whitespace` | over_budget. d_in_char 0.1239 exceeds budget 0.10 | excluded | <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins>, <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27; &#x27;</code></ins> | 27 | 0.1239 |  |  |  |  |
| `word_insertion` | eligible. not flagged by the retrospective audit (operator audited by a sample of 5 candidates) | measured | <del><code>&#x27;&#x27;</code></del> → <ins><code>&#x27;Carefully &#x27;</code></ins> | 10 | 0.0498 | 0.0474 | 0.0000 | +0.0474 | Qwen 3.8 27B correct → correct, GPT-OSS-120B correct → correct, GPT-OSS-20B correct → correct, ALLaM-2-7B incorrect → incorrect, Gemini 3.1 Flash-Lite correct → correct |
| `word_deletion` | eligible. not flagged by the retrospective audit (every candidate of this operator was audited) | measured | <del><code>&#x27; the&#x27;</code></del> → <ins><code>&#x27;&#x27;</code></ins> | 4 | 0.0209 | 0.0473 | 0.0000 | +0.0473 | Qwen 3.8 27B correct → correct, GPT-OSS-120B correct → correct, GPT-OSS-20B correct → correct, ALLaM-2-7B incorrect → incorrect, Gemini 3.1 Flash-Lite correct → correct |
| `synonym` | eligible. not flagged by the retrospective audit (every candidate of this operator was audited) | measured | <del><code>&#x27;l&#x27;</code></del> → <ins><code>&#x27;&#x27;</code></ins>, <del><code>&#x27;ss&#x27;</code></del> → <ins><code>&#x27;tegor&#x27;</code></ins>, <del><code>&#x27;fy&#x27;</code></del> → <ins><code>&#x27;ze&#x27;</code></ins> | 8 | 0.0415 | 0.0846 | 0.0000 | +0.0846 | Qwen 3.8 27B correct → correct, GPT-OSS-120B correct → correct, GPT-OSS-20B correct → correct, ALLaM-2-7B incorrect → correct, Gemini 3.1 Flash-Lite correct → correct |
| `word_substitution` | inapplicable. inapplicable_or_no_op | excluded |  |  |  |  |  |  |  |
| `instruction_reordering` | inapplicable. inapplicable_or_no_op | excluded |  |  |  |  |  |  |  |
| `random_edit` | noise_benchmark. Noise benchmark only. Preservation: unaudited. | measured | <del><code>&#x27;e&#x27;</code></del> → <ins><code>&#x27;&#x27;</code></ins>, <del><code>&quot;&#x27;&quot;</code></del> → <ins><code>&#x27;i&#x27;</code></ins> | 2 | 0.0105 | 0.1783 | 0.0000 | +0.1783 | Qwen 3.8 27B correct → correct, GPT-OSS-120B correct → correct, GPT-OSS-20B correct → correct, ALLaM-2-7B incorrect → correct, Gemini 3.1 Flash-Lite correct → correct |

## Input–output trade-off

Each edit below is on the frontier of character edit count and excess distance.

- `capitalization` · 1 character edit(s) · excess +0.0950

## Source records

The JSON record next to this report contains full responses, per-model scores, candidate IDs, and the treatment and control pair IDs with their generation IDs.
