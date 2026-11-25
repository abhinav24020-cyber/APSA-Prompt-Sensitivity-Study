# Perturbation operator result: CODE-008 · Code generation

**Status:** `selected` · **Rule:** budget mode, d_in_char ≤ 0.10 · **Model scope:** fixed panel of 5 models, equal weights · **Evidence:** retrospective

## 1. Category recommendation

- Recommended: **word_insertion** (exploratory (main_v1 discovery ranking); source: category_operator_rankings.csv (code_generation, budget 0.10))
- Category score 0.0386, coverage 10/10 complete prompts
- Why: A leading tone cue ('Carefully') can change which implementation the model writes while preserving the signature and input/output contract.
- A category recommendation is not a measurement of this prompt; the measured result follows.

## 2. Measured result for this prompt

word_insertion produced the largest control-adjusted change (+0.0346) among 6 eligible, measured edits within budget 0.10. The next best eligible edit was synonym (+0.0288). Preservation evidence: not flagged by the retrospective audit (operator audited by a sample of 5 candidates).

| Field | Result |
|---|---|
| Prompt and category | `CODE-008` · Code generation |
| Original prompt | Write a Python class Singleton using the __new__ method to ensure that only one instance of the class can ever be created. |
| Perturbed prompt | Carefully Write a Python class Singleton using the __new__ method to ensure that only one instance of the class can ever be created. |
| Operator | `word_insertion`: `∅` → `Carefully` |
| Input change | **10 character edit(s)**, normalised distance **0.0758**, semantic input distance 0.0130 |
| Model and comparison | fixed panel of 5 models, equal weights; 5 matched model–prompt pair(s) from `main_v1` |
| Output change | Semantic distance **0.0352**, mean unchanged control distance **0.0005**, excess distance **+0.0346** |
| Functional result | Qwen 3.8 27B: correct → correct (unit tests); response length 203 → 203 characters; GPT-OSS-120B: correct → correct (unit tests); response length 658 → 845 characters; GPT-OSS-20B: correct → correct (unit tests); response length 217 → 217 characters; ALLaM-2-7B: incorrect → correct (unit tests); final answer text changed; response length 244 → 326 characters; Gemini 3.1 Flash-Lite: correct → correct (unit tests); response length 348 → 348 characters |
| Tie status | unique |
| Evidence status | Measured retrospectively from stored main_v1 outputs; this prompt belongs to the discovery set that produced the category ranking, so the result is exploratory. |

### Responses of GPT-OSS-120B (largest effect in the panel)

**Original prompt response**

```text
```python
class Singleton:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            # Create the instance and store it
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, value=None):
        # Optional: initialize only once
        if not hasattr(self, "_initialized"):
            self.value = value
            self._initialized = True

# Example usage:
if __name__ == "__main__":
    a = Singleton(10)
    b = Singleton(20)
    print(a is b)          # True
    print(a.value)         # 10 (unchanged after first init)
    print(b.value)         # 10
```
```

**Perturbed prompt response**

```text
```python
class Singleton:
    _instance = None  # Class-level attribute to hold the sole instance

    def __new__(cls, *args, **kwargs):
        # If an instance doesn't exist yet, create one
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        # Return the existing instance (or the newly created one)
        return cls._instance

    def __init__(self, value=None):
        """
        Optional initializer. It will run on every call to the class,
        but you can guard against reinitialization if needed.
        """
        # Example: only set the attribute the first time
        if not hasattr(self, "_initialized"):
            self.value = value
            self._initialized = True

    def __repr__(self):
        return f"<Singleton id={id(self)} value={getattr(self, 'value', None)}>"
```
```

## 3. All operators

| Operator | Status | Char edits | d_in_char | Raw | Control | Excess | Correctness (before → after) |
|---|---|---:|---:|---:|---:|---:|---|
| `word_insertion` **(selected)** | measured | 10 | 0.0758 | 0.0352 | 0.0005 | +0.0346 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→correct; Gemini 3.1 Flash-Lite correct→correct |
| `synonym` | measured | 7 | 0.0565 | 0.0293 | 0.0005 | +0.0288 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→incorrect; Gemini 3.1 Flash-Lite correct→correct |
| `word_substitution` | measured | 3 | 0.0244 | 0.0228 | 0.0005 | +0.0223 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→correct; Gemini 3.1 Flash-Lite correct→correct |
| `punctuation` | measured | 1 | 0.0082 | 0.0107 | 0.0005 | +0.0101 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→correct; Gemini 3.1 Flash-Lite correct→correct |
| `capitalization` | measured | 1 | 0.0082 | 0.0087 | 0.0005 | +0.0082 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→incorrect; Gemini 3.1 Flash-Lite correct→correct |
| `word_deletion` | measured | 4 | 0.0328 | 0.0081 | 0.0005 | +0.0075 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B incorrect→incorrect; Gemini 3.1 Flash-Lite correct→correct |
| `char_substitution` | meaning_changing: retrospective audit flag: specification_changed | 1 | 0.0082 |  |  |  |  |
| `instruction_reordering` | inapplicable: inapplicable_or_no_op |  |  |  |  |  |  |
| `whitespace` | over_budget: d_in_char 0.1469 exceeds budget 0.10 | 21 | 0.1469 |  |  |  |  |

## 4. Input–output trade-off

Eligible edits not dominated by another edit with no more character edits and at least as much excess change:

- `punctuation`: 1 character edit(s) → excess +0.0101
- `word_substitution`: 3 character edit(s) → excess +0.0223
- `synonym`: 7 character edit(s) → excess +0.0288
- `word_insertion`: 10 character edit(s) → excess +0.0346

## 5. Source records

Full responses, per-model scores and record IDs are in the JSON file next to this report.

- `qwen/qwen3.8-27b|CODE-008|treatment|word_insertion|1`: anchor record `c1b0100e-5fd6-4479-bca9-0f198325c815`, comparison record `61967208-7871-47c2-bbb0-02d1d634a773`
- `openai/gpt-oss-120b|CODE-008|treatment|word_insertion|1`: anchor record `8ede7076-7e26-4c32-a605-fd1927e7a014`, comparison record `5797fa17-e5f3-47a3-8e08-85bdbe1d3509`
- `openai/gpt-oss-20b|CODE-008|treatment|word_insertion|1`: anchor record `796ef4f7-d2d8-4f7c-9f36-eaba75b44a85`, comparison record `7e2ff349-0827-4d08-a7ba-fb440469cea6`
- `allam-2-7b|CODE-008|treatment|word_insertion|1`: anchor record `9ae0d953-d2c1-41e7-af75-2fee91bd0177`, comparison record `755fd576-ebca-4cd7-97dd-436626ff7e58`
- `gemini-3.1-flash-lite|CODE-008|treatment|word_insertion|1`: anchor record `801ae53e-08d1-4ad9-aff5-98caa793b8d2`, comparison record `641eaa7d-da2e-4d73-8a47-f1e7c11c1bfa`
