# Perturbation operator result: QA-015 · Question answering

**Status:** `selected` · **Rule:** budget mode, d_in_char ≤ 0.10 · **Model scope:** fixed panel of 5 models, equal weights · **Evidence:** retrospective

## 1. Category recommendation

- Recommended: **punctuation** (exploratory (main_v1 discovery ranking); source: category_operator_rankings.csv (question_answering, budget 0.10))
- Category score 0.0426, coverage 10/10 complete prompts
- Why: Editing the question's final delimiter can change the form or length of the answer while keeping the requested fact fixed.
- A category recommendation is not a measurement of this prompt; the measured result follows.

## 2. Measured result for this prompt

capitalization produced the largest control-adjusted change (+0.0185) among 3 eligible, measured edits within budget 0.10. The next best eligible edit was word_insertion (+0.0176). Preservation evidence: not flagged by the retrospective audit (operator audited by a sample of 5 candidates).

| Field | Result |
|---|---|
| Prompt and category | `QA-015` · Question answering |
| Original prompt | Extract all personal names and location names from this text: 'Dr. Sophia Martinez presented her oncology findings in Zurich after consulting with Dr. Liam Chen in Tokyo.' |
| Perturbed prompt | extract all personal names and location names from this text: 'Dr. Sophia Martinez presented her oncology findings in Zurich after consulting with Dr. Liam Chen in Tokyo.' |
| Operator | `capitalization`: `Extract` → `extract` |
| Input change | **1 character edit(s)**, normalised distance **0.0058**, semantic input distance 0.0000 |
| Model and comparison | fixed panel of 5 models, equal weights; 5 matched model–prompt pair(s) from `main_v1` |
| Output change | Semantic distance **0.0185**, mean unchanged control distance **0.0000**, excess distance **+0.0185** |
| Functional result | Qwen 3.8 27B: correct → correct; same final answer; response length 287 → 281 characters; GPT-OSS-120B: correct → correct; same final answer; response length 136 → 136 characters; GPT-OSS-20B: correct → correct; response length 105 → 74 characters; ALLaM-2-7B: correct → correct; response length 92 → 92 characters; Gemini 3.1 Flash-Lite: correct → correct; same final answer; response length 129 → 129 characters |
| Tie status | unique |
| Evidence status | Measured retrospectively from stored main_v1 outputs; this prompt belongs to the discovery set that produced the category ranking, so the result is exploratory. |

### Responses of GPT-OSS-20B (largest effect in the panel)

**Original prompt response**

```text
**Personal names:**  
- Dr. Sophia Martinez  
- Dr. Liam Chen  

**Location names:**  
- Zurich  
- Tokyo
```

**Perturbed prompt response**

```text
Personal names: Sophia Martinez, Liam Chen  
Location names: Zurich, Tokyo
```

## 3. All operators

| Operator | Status | Char edits | d_in_char | Raw | Control | Excess | Correctness (before → after) |
|---|---|---:|---:|---:|---:|---:|---|
| `capitalization` **(selected)** | measured | 1 | 0.0058 | 0.0185 | 0.0000 | +0.0185 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `word_insertion` | measured | 10 | 0.0552 | 0.0176 | 0.0000 | +0.0176 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `punctuation` | measured | 1 | 0.0058 | 0.0172 | 0.0000 | +0.0172 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `char_substitution` | meaning_changing: retrospective audit flag: answer_entity_changed | 1 | 0.0058 |  |  |  |  |
| `instruction_reordering` | over_budget: d_in_char 0.2456 exceeds budget 0.10 | 42 | 0.2456 |  |  |  |  |
| `synonym` | inapplicable: inapplicable_or_no_op |  |  |  |  |  |  |
| `whitespace` | over_budget: d_in_char 0.1320 exceeds budget 0.10 | 26 | 0.1320 |  |  |  |  |
| `word_deletion` | inapplicable: inapplicable_or_no_op |  |  |  |  |  |  |
| `word_substitution` | inapplicable: inapplicable_or_no_op |  |  |  |  |  |  |

## 4. Input–output trade-off

Eligible edits not dominated by another edit with no more character edits and at least as much excess change:

- `capitalization`: 1 character edit(s) → excess +0.0185

## 5. Source records

Full responses, per-model scores and record IDs are in the JSON file next to this report.

- `qwen/qwen3.8-27b|QA-015|treatment|capitalization|1`: anchor record `cde1ff8c-c459-477d-b221-20df4e6687d2`, comparison record `e3d4f354-15d6-4946-9b63-5d987bc424aa`
- `openai/gpt-oss-120b|QA-015|treatment|capitalization|1`: anchor record `84f54d90-6ab3-43b9-9052-f1d7e3315921`, comparison record `d128a7fa-1fc6-4de4-94aa-93a44485706f`
- `openai/gpt-oss-20b|QA-015|treatment|capitalization|1`: anchor record `af5a3829-01f1-478e-ae3e-c273211990b4`, comparison record `959a73e0-94e8-4dc8-b9b7-f86e70329155`
- `allam-2-7b|QA-015|treatment|capitalization|1`: anchor record `255a7624-3d82-4247-9906-5efff79b7d84`, comparison record `0d53b804-dfa0-48e1-af68-06e920f7c368`
- `gemini-3.1-flash-lite|QA-015|treatment|capitalization|1`: anchor record `220daefe-4680-463c-94b3-7aa57635aaa2`, comparison record `b242d879-796e-46ae-ae69-a85041e7e08e`
