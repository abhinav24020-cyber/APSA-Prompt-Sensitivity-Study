# Perturbation operator result: CODE-005 · Code generation

**Status:** `selected` · **Rule:** budget mode, d_in_char ≤ 0.10 · **Model scope:** fixed panel of 5 models, equal weights · **Evidence:** retrospective

## 1. Category recommendation

- Recommended: **word_insertion** (exploratory (main_v1 discovery ranking); source: category_operator_rankings.csv (code_generation, budget 0.10))
- Category score 0.0386, coverage 10/10 complete prompts
- Why: A leading tone cue ('Carefully') can change which implementation the model writes while preserving the signature and input/output contract.
- A category recommendation is not a measurement of this prompt; the measured result follows.

## 2. Measured result for this prompt

word_insertion produced the largest control-adjusted change (+0.0618) among 7 eligible, measured edits within budget 0.10. The next best eligible edit was char_substitution (+0.0509). Preservation evidence: not flagged by the retrospective audit (operator audited by a sample of 5 candidates).

| Field | Result |
|---|---|
| Prompt and category | `CODE-005` · Code generation |
| Original prompt | Write a Python function word_frequencies(text: str) -> dict[str, int] that converts text to lowercase, strips punctuation, and returns a dictionary of word counts. |
| Perturbed prompt | Carefully Write a Python function word_frequencies(text: str) -> dict[str, int] that converts text to lowercase, strips punctuation, and returns a dictionary of word counts. |
| Operator | `word_insertion`: `∅` → `Carefully` |
| Input change | **10 character edit(s)**, normalised distance **0.0578**, semantic input distance 0.0035 |
| Model and comparison | fixed panel of 5 models, equal weights; 5 matched model–prompt pair(s) from `main_v1` |
| Output change | Semantic distance **0.0628**, mean unchanged control distance **0.0010**, excess distance **+0.0618** |
| Functional result | Qwen 3.8 27B: correct → correct (unit tests); response length 383 → 385 characters; GPT-OSS-120B: correct → correct (unit tests); response length 704 → 704 characters; GPT-OSS-20B: correct → correct (unit tests); response length 394 → 541 characters; ALLaM-2-7B: incorrect → incorrect (unit tests); response length 711 → 979 characters; Gemini 3.1 Flash-Lite: correct → correct (unit tests); response length 362 → 466 characters |
| Tie status | unique |
| Evidence status | Measured retrospectively from stored main_v1 outputs; this prompt belongs to the discovery set that produced the category ranking, so the result is exploratory. |

### Responses of Gemini 3.1 Flash-Lite (largest effect in the panel)

**Original prompt response**

```text
```python
import re
from collections import Counter

def word_frequencies(text: str) -> dict[str, int]:
    text = text.lower()
    words = re.findall(r'\b\w+\b', text)
    return dict(Counter(words))
```

Final answer: The provided Python function uses `re.findall` to extract words while ignoring punctuation and `collections.Counter` to tally the frequencies.
```

**Perturbed prompt response**

```text
```python
import string

def word_frequencies(text: str) -> dict[str, int]:
    translator = str.maketrans('', '', string.punctuation)
    words = text.lower().translate(translator).split()
    counts = {}
    for word in words:
        counts[word] = counts.get(word, 0) + 1
    return counts
```

Final answer: The provided Python function uses `str.maketrans` to remove punctuation, converts the text to lowercase, and uses a dictionary to count word occurrences.
```

## 3. All operators

| Operator | Status | Char edits | d_in_char | Raw | Control | Excess | Correctness (before → after) |
|---|---|---:|---:|---:|---:|---:|---|
| `word_insertion` **(selected)** | measured | 10 | 0.0578 | 0.0628 | 0.0010 | +0.0618 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→incorrect; Gemini 3.1 Flash-Lite correct→correct |
| `char_substitution` | measured | 1 | 0.0061 | 0.0519 | 0.0010 | +0.0509 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→incorrect; Gemini 3.1 Flash-Lite correct→correct |
| `synonym` | measured | 6 | 0.0364 | 0.0383 | 0.0010 | +0.0373 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→correct; Gemini 3.1 Flash-Lite correct→correct |
| `capitalization` | measured | 1 | 0.0061 | 0.0294 | 0.0010 | +0.0283 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→correct; Gemini 3.1 Flash-Lite correct→correct |
| `word_deletion` | measured | 2 | 0.0123 | 0.0239 | 0.0010 | +0.0229 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→correct; Gemini 3.1 Flash-Lite correct→correct |
| `word_substitution` | measured | 3 | 0.0183 | 0.0235 | 0.0010 | +0.0225 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→correct; Gemini 3.1 Flash-Lite correct→correct |
| `punctuation` | measured | 1 | 0.0061 | 0.0097 | 0.0010 | +0.0086 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→correct; Gemini 3.1 Flash-Lite correct→correct |
| `instruction_reordering` | inapplicable: inapplicable_or_no_op |  |  |  |  |  |  |
| `whitespace` | over_budget: d_in_char 0.1189 exceeds budget 0.10 | 22 | 0.1189 |  |  |  |  |

## 4. Input–output trade-off

Eligible edits not dominated by another edit with no more character edits and at least as much excess change:

- `char_substitution`: 1 character edit(s) → excess +0.0509
- `word_insertion`: 10 character edit(s) → excess +0.0618

## 5. Source records

Full responses, per-model scores and record IDs are in the JSON file next to this report.

- `qwen/qwen3.8-27b|CODE-005|treatment|word_insertion|1`: anchor record `11a22faf-3b5f-4550-a644-d9f6fdd9f020`, comparison record `70087f70-04a6-4d86-9e17-93731095eeed`
- `openai/gpt-oss-120b|CODE-005|treatment|word_insertion|1`: anchor record `9c48f386-8573-427d-b2e6-151120fbb805`, comparison record `94e32f3c-a66d-420a-b49b-622a9c0c9aaf`
- `openai/gpt-oss-20b|CODE-005|treatment|word_insertion|1`: anchor record `fcf75053-c58b-4741-a062-c4c118b153e5`, comparison record `99d24330-818e-4654-b5b6-5ff1c5262f03`
- `allam-2-7b|CODE-005|treatment|word_insertion|1`: anchor record `c9452d7b-deed-4895-a57d-71dff36fa4ad`, comparison record `5488fe3b-69d5-4f8c-8cfe-f2f12ab4de04`
- `gemini-3.1-flash-lite|CODE-005|treatment|word_insertion|1`: anchor record `2f8581be-3b07-41c9-9d11-07448478df3a`, comparison record `2c995933-de7f-46f0-af00-63fa81024ea9`
