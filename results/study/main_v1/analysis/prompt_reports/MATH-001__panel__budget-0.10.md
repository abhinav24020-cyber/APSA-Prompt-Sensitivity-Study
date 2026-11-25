# Perturbation operator result: MATH-001 · Mathematical reasoning

**Status:** `selected` · **Rule:** budget mode, d_in_char ≤ 0.10 · **Model scope:** fixed panel of 5 models, equal weights · **Evidence:** retrospective

## 1. Category recommendation

- Recommended: **char_substitution** (exploratory (main_v1 discovery ranking); source: category_operator_rankings.csv (mathematical_reasoning, budget 0.10))
- Category score 0.0853, coverage 8/8 complete prompts
- Why: A typo in prose changes how the task is rendered while leaving quantities and the requested result intact.
- A category recommendation is not a measurement of this prompt; the measured result follows.

## 2. Measured result for this prompt

char_substitution produced the largest control-adjusted change (+0.0463) among 5 eligible, measured edits within budget 0.10. The next best eligible edit was word_insertion (+0.0449). Preservation evidence: not flagged by the retrospective audit (every candidate of this operator was audited).

| Field | Result |
|---|---|
| Prompt and category | `MATH-001` · Mathematical reasoning |
| Original prompt | A store sells apples in bags of 5 for $3.00. On Tuesday, they offer a 20% discount on all apple bags. If a customer buys 15 apples on Tuesday, how much do they pay in total? |
| Perturbed prompt | A store sells apples in 6ags of 5 for $3.00. On Tuesday, they offer a 20% discount on all apple bags. If a customer buys 15 apples on Tuesday, how much do they pay in total? |
| Operator | `char_substitution`: `bags` → `6ags` |
| Input change | **1 character edit(s)**, normalised distance **0.0058**, semantic input distance 0.0268 |
| Model and comparison | fixed panel of 5 models, equal weights; 5 matched model–prompt pair(s) from `main_v1` |
| Output change | Semantic distance **0.0465**, mean unchanged control distance **0.0002**, excess distance **+0.0463** |
| Functional result | Qwen 3.8 27B: correct → correct; same final answer; response length 993 → 1298 characters; GPT-OSS-120B: correct → correct; same final answer; response length 263 → 190 characters; GPT-OSS-20B: correct → correct; same final answer; response length 26 → 26 characters; ALLaM-2-7B: correct → incorrect; final answer text changed; response length 648 → 434 characters; Gemini 3.1 Flash-Lite: correct → correct; same final answer; response length 390 → 393 characters |
| Tie status | unique |
| Evidence status | Measured retrospectively from stored main_v1 outputs; this prompt belongs to the discovery set that produced the category ranking, so the result is exploratory. |

### Responses of Qwen 3.8 27B (largest effect in the panel)

**Original prompt response**

```text
To determine the total cost, we need to calculate the number of bags required and apply the discount.

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

Final answer: $7.20
```

**Perturbed prompt response**

```text
To determine the total cost, we need to calculate the price per apple, apply the discount, and then multiply by the number of apples purchased.

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

Final answer: $7.20
```

## 3. All operators

| Operator | Status | Char edits | d_in_char | Raw | Control | Excess | Correctness (before → after) |
|---|---|---:|---:|---:|---:|---:|---|
| `char_substitution` **(selected)** | measured | 1 | 0.0058 | 0.0465 | 0.0002 | +0.0463 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→incorrect; Gemini 3.1 Flash-Lite correct→correct |
| `word_insertion` | measured | 10 | 0.0546 | 0.0451 | 0.0002 | +0.0449 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `word_deletion` | measured | 2 | 0.0116 | 0.0343 | 0.0002 | +0.0341 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→incorrect; Gemini 3.1 Flash-Lite correct→correct |
| `capitalization` | measured | 1 | 0.0058 | 0.0262 | 0.0002 | +0.0260 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→incorrect; Gemini 3.1 Flash-Lite correct→correct |
| `punctuation` | measured | 1 | 0.0058 | 0.0172 | 0.0002 | +0.0170 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→incorrect; Gemini 3.1 Flash-Lite correct→correct |
| `instruction_reordering` | over_budget: d_in_char 0.7283 exceeds budget 0.10 | 126 | 0.7283 |  |  |  |  |
| `synonym` | inapplicable: inapplicable_or_no_op |  |  |  |  |  |  |
| `whitespace` | over_budget: d_in_char 0.1683 exceeds budget 0.10 | 35 | 0.1683 |  |  |  |  |
| `word_substitution` | inapplicable: inapplicable_or_no_op |  |  |  |  |  |  |

## 4. Input–output trade-off

Eligible edits not dominated by another edit with no more character edits and at least as much excess change:

- `char_substitution`: 1 character edit(s) → excess +0.0463

## 5. Source records

Full responses, per-model scores and record IDs are in the JSON file next to this report.

- `qwen/qwen3.8-27b|MATH-001|treatment|char_substitution|1`: anchor record `04410e83-86b0-4ba9-b910-a0e3c20a2991`, comparison record `fc7a6b10-aa79-4f23-9eb5-abb9fb9841b0`
- `openai/gpt-oss-120b|MATH-001|treatment|char_substitution|1`: anchor record `f1b0fe7b-747d-4093-9e8f-7f471d75744c`, comparison record `3942dceb-ce57-4cd7-9a64-0626004ae1b4`
- `openai/gpt-oss-20b|MATH-001|treatment|char_substitution|1`: anchor record `7dad7eb5-9ee8-4095-bc85-2ac308e4d594`, comparison record `8533bf72-df1a-471c-9d7c-cadee00ba99c`
- `allam-2-7b|MATH-001|treatment|char_substitution|1`: anchor record `0706a8fd-b7e2-4f96-85c5-a26dbb9d9334`, comparison record `53bcb16f-a602-4fd3-b106-b0bd419b8b2a`
- `gemini-3.1-flash-lite|MATH-001|treatment|char_substitution|1`: anchor record `e989c003-8409-456d-8049-ddca6410254f`, comparison record `d1fb7ef4-448f-4ee4-8338-5d90423c6807`
