# Perturbation operator result: QA-016 · Question answering

**Status:** `selected` · **Rule:** budget mode, d_in_char ≤ 0.10 · **Model scope:** fixed panel of 5 models, equal weights · **Evidence:** retrospective

## 1. Category recommendation

- Recommended: **punctuation** (exploratory (main_v1 discovery ranking); source: category_operator_rankings.csv (question_answering, budget 0.10))
- Category score 0.0426, coverage 10/10 complete prompts
- Why: Editing the question's final delimiter can change the form or length of the answer while keeping the requested fact fixed.
- A category recommendation is not a measurement of this prompt; the measured result follows.

## 2. Measured result for this prompt

punctuation produced the largest control-adjusted change (+0.1572) among 6 eligible, measured edits within budget 0.10. The next best eligible edit was char_substitution (+0.1397). Preservation evidence: not flagged by the retrospective audit (operator audited by a sample of 5 candidates).

| Field | Result |
|---|---|
| Prompt and category | `QA-016` · Question answering |
| Original prompt | List the three TCP packets exchanged in sequence during a standard TCP three-way handshake. |
| Perturbed prompt | List the three TCP packets exchanged in sequence during a standard TCP three-way handshake |
| Operator | `punctuation`: `handshake.` → `handshake` |
| Input change | **1 character edit(s)**, normalised distance **0.0110**, semantic input distance 0.0218 |
| Model and comparison | fixed panel of 5 models, equal weights; 5 matched model–prompt pair(s) from `main_v1` |
| Output change | Semantic distance **0.1599**, mean unchanged control distance **0.0027**, excess distance **+0.1572** |
| Functional result | Qwen 3.8 27B: correct → correct; same final answer; response length 474 → 215 characters; GPT-OSS-120B: incorrect → incorrect; final answer text changed; response length 234 → 601 characters; GPT-OSS-20B: incorrect → incorrect; final answer text changed; response length 19 → 245 characters; ALLaM-2-7B: correct → correct; final answer text changed; response length 1373 → 1840 characters; Gemini 3.1 Flash-Lite: correct → correct; same final answer; response length 463 → 416 characters |
| Tie status | unique |
| Evidence status | Measured retrospectively from stored main_v1 outputs; this prompt belongs to the discovery set that produced the category ranking, so the result is exploratory. |

### Responses of GPT-OSS-20B (largest effect in the panel)

**Original prompt response**

```text
SYN → SYN‑ACK → ACK
```

**Perturbed prompt response**

```text
1. **SYN** – the client initiates the connection.  
2. **SYN‑ACK** – the server acknowledges the SYN and sends its own SYN.  
3. **ACK** – the client acknowledges the server’s SYN‑ACK, completing the handshake.  

Final answer: SYN, SYN‑ACK, ACK
```

## 3. All operators

| Operator | Status | Char edits | d_in_char | Raw | Control | Excess | Correctness (before → after) |
|---|---|---:|---:|---:|---:|---:|---|
| `punctuation` **(selected)** | measured | 1 | 0.0110 | 0.1599 | 0.0027 | +0.1572 | Qwen 3.8 27B correct→correct; GPT-OSS-120B incorrect→incorrect; GPT-OSS-20B incorrect→incorrect; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `char_substitution` | measured | 1 | 0.0110 | 0.1424 | 0.0027 | +0.1397 | Qwen 3.8 27B correct→correct; GPT-OSS-120B incorrect→incorrect; GPT-OSS-20B incorrect→incorrect; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `word_insertion` | measured | 10 | 0.0990 | 0.1218 | 0.0027 | +0.1191 | Qwen 3.8 27B correct→correct; GPT-OSS-120B incorrect→incorrect; GPT-OSS-20B incorrect→incorrect; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `capitalization` | measured | 1 | 0.0110 | 0.0925 | 0.0027 | +0.0898 | Qwen 3.8 27B correct→correct; GPT-OSS-120B incorrect→incorrect; GPT-OSS-20B incorrect→incorrect; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `word_deletion` | measured | 4 | 0.0440 | 0.0630 | 0.0027 | +0.0603 | Qwen 3.8 27B correct→correct; GPT-OSS-120B incorrect→incorrect; GPT-OSS-20B incorrect→incorrect; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `word_substitution` | measured | 7 | 0.0769 | 0.0368 | 0.0027 | +0.0341 | Qwen 3.8 27B correct→correct; GPT-OSS-120B incorrect→incorrect; GPT-OSS-20B incorrect→incorrect; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `instruction_reordering` | inapplicable: inapplicable_or_no_op |  |  |  |  |  |  |
| `synonym` | over_budget: d_in_char 0.1158 exceeds budget 0.10 | 11 | 0.1158 |  |  |  |  |
| `whitespace` | over_budget: d_in_char 0.1250 exceeds budget 0.10 | 13 | 0.1250 |  |  |  |  |

## 4. Input–output trade-off

Eligible edits not dominated by another edit with no more character edits and at least as much excess change:

- `punctuation`: 1 character edit(s) → excess +0.1572

## 5. Source records

Full responses, per-model scores and record IDs are in the JSON file next to this report.

- `qwen/qwen3.8-27b|QA-016|treatment|punctuation|1`: anchor record `0e2e6241-14d7-489f-9778-730352c76c2b`, comparison record `7f37ed5f-574d-4a5a-b071-f84616196008`
- `openai/gpt-oss-120b|QA-016|treatment|punctuation|1`: anchor record `03650262-397b-4d2f-bc7f-c7b3da873f01`, comparison record `dc578e45-6b36-4171-a471-a475ed39d232`
- `openai/gpt-oss-20b|QA-016|treatment|punctuation|1`: anchor record `d13632be-1483-4b98-be42-80e668bd6e84`, comparison record `79e09bc4-0936-40f9-bd0f-568b500f75b1`
- `allam-2-7b|QA-016|treatment|punctuation|1`: anchor record `9fb06af4-17d5-4040-9c78-f53da1147ca8`, comparison record `562b8b7f-d6c3-442d-a3dd-d601ed9e0122`
- `gemini-3.1-flash-lite|QA-016|treatment|punctuation|1`: anchor record `536c090c-6fea-49aa-9c14-b937eb725fd5`, comparison record `98e7c9f3-3c63-4e14-993b-1829c7e78fb0`
