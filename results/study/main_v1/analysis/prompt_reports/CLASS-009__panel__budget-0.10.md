# Perturbation operator result: CLASS-009 · Classification

**Status:** `selected` · **Rule:** budget mode, d_in_char ≤ 0.10 · **Model scope:** fixed panel of 5 models, equal weights · **Evidence:** retrospective

## 1. Category recommendation

- Recommended: **synonym** (exploratory (main_v1 discovery ranking); source: category_operator_rankings.csv (classification, budget 0.10))
- Category score 0.0761, coverage 10/10 complete prompts
- Why: Replacing an instruction verb (e.g. Classify -> Categorize) changes the cue used to request a label while preserving the label set and evidence.
- A category recommendation is not a measurement of this prompt; the measured result follows.

## 2. Measured result for this prompt

word_insertion produced the largest control-adjusted change (+0.1196) among 6 eligible, measured edits within budget 0.10. The next best eligible edit was char_substitution (+0.1055). Preservation evidence: not flagged by the retrospective audit (operator audited by a sample of 5 candidates).

| Field | Result |
|---|---|
| Prompt and category | `CLASS-009` · Classification |
| Original prompt | Classify the literary genre of this passage into [Science Fiction, Fantasy, Historical Fiction, Mystery]: 'The starship hyperdrive hummed as Captain Vance prepared to warp into sector 9 beyond the outer rim.' |
| Perturbed prompt | Carefully Classify the literary genre of this passage into [Science Fiction, Fantasy, Historical Fiction, Mystery]: 'The starship hyperdrive hummed as Captain Vance prepared to warp into sector 9 beyond the outer rim.' |
| Operator | `word_insertion`: `∅` → `Carefully` |
| Input change | **10 character edit(s)**, normalised distance **0.0459**, semantic input distance 0.0050 |
| Model and comparison | fixed panel of 5 models, equal weights; 5 matched model–prompt pair(s) from `main_v1` |
| Output change | Semantic distance **0.1199**, mean unchanged control distance **0.0003**, excess distance **+0.1196** |
| Functional result | Qwen 3.8 27B: correct → correct; same final answer; response length 376 → 383 characters; GPT-OSS-120B: correct → correct; same final answer; response length 47 → 29 characters; GPT-OSS-20B: correct → correct; same final answer; response length 46 → 46 characters; ALLaM-2-7B: correct → correct; final answer text changed; response length 30 → 129 characters; Gemini 3.1 Flash-Lite: correct → correct; same final answer; response length 180 → 175 characters |
| Tie status | unique |
| Evidence status | Measured retrospectively from stored main_v1 outputs; this prompt belongs to the discovery set that produced the category ranking, so the result is exploratory. |

### Responses of ALLaM-2-7B (largest effect in the panel)

**Original prompt response**

```text
Final answer: Science Fiction
```

**Perturbed prompt response**

```text
Final answer: Science Fiction

The passage mentions a starship, hyperdrive, and warping, which are all science fiction elements.
```

## 3. All operators

| Operator | Status | Char edits | d_in_char | Raw | Control | Excess | Correctness (before → after) |
|---|---|---:|---:|---:|---:|---:|---|
| `word_insertion` **(selected)** | measured | 10 | 0.0459 | 0.1199 | 0.0003 | +0.1196 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `char_substitution` | measured | 1 | 0.0048 | 0.1058 | 0.0003 | +0.1055 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `punctuation` | measured | 1 | 0.0048 | 0.0179 | 0.0003 | +0.0176 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `word_deletion` | measured | 4 | 0.0192 | 0.0172 | 0.0003 | +0.0169 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `synonym` | measured | 8 | 0.0381 | 0.0170 | 0.0003 | +0.0166 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `capitalization` | measured | 1 | 0.0048 | 0.0050 | 0.0003 | +0.0046 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `instruction_reordering` | inapplicable: inapplicable_or_no_op |  |  |  |  |  |  |
| `whitespace` | over_budget: d_in_char 0.1260 exceeds budget 0.10 | 30 | 0.1260 |  |  |  |  |
| `word_substitution` | inapplicable: inapplicable_or_no_op |  |  |  |  |  |  |

## 4. Input–output trade-off

Eligible edits not dominated by another edit with no more character edits and at least as much excess change:

- `char_substitution`: 1 character edit(s) → excess +0.1055
- `word_insertion`: 10 character edit(s) → excess +0.1196

## 5. Source records

Full responses, per-model scores and record IDs are in the JSON file next to this report.

- `qwen/qwen3.8-27b|CLASS-009|treatment|word_insertion|1`: anchor record `f150fa9c-5a36-4700-ad3b-4814f41e6431`, comparison record `298a9926-4676-4a66-9fee-5570478c01e5`
- `openai/gpt-oss-120b|CLASS-009|treatment|word_insertion|1`: anchor record `9be73ae1-682f-4cb5-a84f-f14f710f0ed1`, comparison record `bf69fb98-5dbf-4675-a2ce-7bbd0a0bac52`
- `openai/gpt-oss-20b|CLASS-009|treatment|word_insertion|1`: anchor record `c7f9a845-dde4-4b3b-b776-7e5c63217708`, comparison record `c9ce1729-5b5a-4771-86b8-245a43618380`
- `allam-2-7b|CLASS-009|treatment|word_insertion|1`: anchor record `1731fc97-f7f7-4492-beb1-c8737766a540`, comparison record `9d0aa43c-d0b5-4c03-af4a-72c2a3ccc006`
- `gemini-3.1-flash-lite|CLASS-009|treatment|word_insertion|1`: anchor record `d42eac14-6c65-42ac-b4d2-c1e9be08971c`, comparison record `4deb5008-7d10-48ba-a165-9a8c7b74742a`
