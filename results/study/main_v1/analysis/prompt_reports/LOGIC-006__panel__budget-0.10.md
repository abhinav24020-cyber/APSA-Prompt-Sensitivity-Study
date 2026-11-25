# Perturbation operator result: LOGIC-006 · Logical reasoning

**Status:** `selected` · **Rule:** budget mode, d_in_char ≤ 0.10 · **Model scope:** fixed panel of 5 models, equal weights · **Evidence:** retrospective

## 1. Category recommendation

- Recommended: **punctuation** (exploratory (main_v1 discovery ranking); source: category_operator_rankings.csv (logical_reasoning, budget 0.10))
- Category score 0.0744, coverage 9/9 complete prompts
- Why: A terminal punctuation edit changes the cue at the end of the prompt while leaving premises and the requested conclusion intact.
- A category recommendation is not a measurement of this prompt; the measured result follows.

## 2. Measured result for this prompt

char_substitution produced the largest control-adjusted change (+0.1927) among 5 eligible, measured edits within budget 0.10. The next best eligible edit was punctuation (+0.1866). Preservation evidence: not flagged by the retrospective audit (every candidate of this operator was audited).

| Field | Result |
|---|---|
| Prompt and category | `LOGIC-006` · Logical reasoning |
| Original prompt | Task A must be completed before Task B. Task C can only start after Task B is completed. Task D must happen before Task C but after Task A. List all valid execution orders for these 4 tasks." |
| Perturbed prompt | Task A must be completed before Task B. Task C can only start after Task B is completed. Task D must happen before Task C but after Task A. List all v@lid execution orders for these 4 tasks." |
| Operator | `char_substitution`: `valid` → `v@lid` |
| Input change | **1 character edit(s)**, normalised distance **0.0052**, semantic input distance 0.1410 |
| Model and comparison | fixed panel of 5 models, equal weights; 5 matched model–prompt pair(s) from `main_v1` |
| Output change | Semantic distance **0.1927**, mean unchanged control distance **0.0000**, excess distance **+0.1927** |
| Functional result | Qwen 3.8 27B: correct → correct; final answer text changed; response length 1738 → 1795 characters; GPT-OSS-120B: correct → correct; final answer text changed; response length 72 → 234 characters; GPT-OSS-20B: correct → correct; final answer text changed; response length 410 → 51 characters; ALLaM-2-7B: incorrect → incorrect; response length 671 → 892 characters; Gemini 3.1 Flash-Lite: correct → correct; same final answer; response length 466 → 454 characters |
| Tie status | unique |
| Evidence status | Measured retrospectively from stored main_v1 outputs; this prompt belongs to the discovery set that produced the category ranking, so the result is exploratory. |

### Responses of GPT-OSS-20B (largest effect in the panel)

**Original prompt response**

```text
The constraints are:

- **A** must finish before **B** starts.  
- **D** must finish after **A** but before **C** starts.  
- **C** can only start after **B** is finished.

With these rules, the only possible execution orders for the four tasks are:

1. **A → D → B → C**  
2. **A → B → D → C**  

These two sequences satisfy all the given precedence requirements.  

Final answer: A → D → B → C; A → B → D → C
```

**Perturbed prompt response**

```text
A B D C  
A D B C  

Final answer: A B D C, A D B C
```

## 3. All operators

| Operator | Status | Char edits | d_in_char | Raw | Control | Excess | Correctness (before → after) |
|---|---|---:|---:|---:|---:|---:|---|
| `char_substitution` **(selected)** | measured | 1 | 0.0052 | 0.1927 | 0.0000 | +0.1927 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→incorrect; Gemini 3.1 Flash-Lite correct→correct |
| `punctuation` | measured | 1 | 0.0052 | 0.1866 | 0.0000 | +0.1866 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→incorrect; Gemini 3.1 Flash-Lite correct→correct |
| `word_insertion` | measured | 10 | 0.0498 | 0.1828 | 0.0000 | +0.1828 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→correct; Gemini 3.1 Flash-Lite correct→correct |
| `synonym` | measured | 8 | 0.0410 | 0.1717 | 0.0000 | +0.1717 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→incorrect; Gemini 3.1 Flash-Lite correct→correct |
| `capitalization` | measured | 1 | 0.0052 | 0.0699 | 0.0000 | +0.0699 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→incorrect; Gemini 3.1 Flash-Lite correct→correct |
| `instruction_reordering` | over_budget: d_in_char 0.5445 exceeds budget 0.10 | 104 | 0.5445 |  |  |  |  |
| `whitespace` | over_budget: d_in_char 0.1623 exceeds budget 0.10 | 37 | 0.1623 |  |  |  |  |
| `word_deletion` | meaning_changing: retrospective audit flag: entity_removed | 2 | 0.0105 |  |  |  |  |
| `word_substitution` | meaning_changing: retrospective audit flag: question_changed | 2 | 0.0104 |  |  |  |  |

## 4. Input–output trade-off

Eligible edits not dominated by another edit with no more character edits and at least as much excess change:

- `char_substitution`: 1 character edit(s) → excess +0.1927

## 5. Source records

Full responses, per-model scores and record IDs are in the JSON file next to this report.

- `qwen/qwen3.8-27b|LOGIC-006|treatment|char_substitution|1`: anchor record `89b226c3-4ed8-4838-9817-dcef5804f20b`, comparison record `f3e5e710-91be-40ca-9999-7b491dc30d1b`
- `openai/gpt-oss-120b|LOGIC-006|treatment|char_substitution|1`: anchor record `8a5518da-b0e8-4961-8406-0eac3a936bb7`, comparison record `5df9674f-6119-4eef-9c77-8bfbf63c4d92`
- `openai/gpt-oss-20b|LOGIC-006|treatment|char_substitution|1`: anchor record `2235edbd-47fc-4706-9b9c-d540cab99a0e`, comparison record `591ec343-20e3-44d5-bf44-48924c37fe8e`
- `allam-2-7b|LOGIC-006|treatment|char_substitution|1`: anchor record `f8974086-9177-4062-b0c9-92e64c6be94a`, comparison record `e02eabc0-4f1e-4572-82e6-f8007e692016`
- `gemini-3.1-flash-lite|LOGIC-006|treatment|char_substitution|1`: anchor record `faeee81e-7569-4982-86ff-f216b3ff6c1c`, comparison record `79a3c31d-7ee4-4d2f-b911-6ded42ee9e4f`
