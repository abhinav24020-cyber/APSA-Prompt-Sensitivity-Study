# Perturbation operator result: QA-007 · Question answering

**Status:** `selected` · **Rule:** budget mode, d_in_char ≤ 0.10 · **Model scope:** fixed panel of 5 models, equal weights · **Evidence:** retrospective

## 1. Category recommendation

- Recommended: **punctuation** (exploratory (main_v1 discovery ranking); source: category_operator_rankings.csv (question_answering, budget 0.10))
- Category score 0.0426, coverage 10/10 complete prompts
- Why: Editing the question's final delimiter can change the form or length of the answer while keeping the requested fact fixed.
- A category recommendation is not a measurement of this prompt; the measured result follows.

## 2. Measured result for this prompt

word_insertion produced the largest control-adjusted change (+0.0624) among 5 eligible, measured edits within budget 0.10. The next best eligible edit was punctuation (+0.0601). Preservation evidence: not flagged by the retrospective audit (operator audited by a sample of 5 candidates).

| Field | Result |
|---|---|
| Prompt and category | `QA-007` · Question answering |
| Original prompt | Which planet in the Solar System has the highest average surface temperature, and why is it hotter than Mercury? |
| Perturbed prompt | Carefully Which planet in the Solar System has the highest average surface temperature, and why is it hotter than Mercury? |
| Operator | `word_insertion`: `∅` → `Carefully` |
| Input change | **10 character edit(s)**, normalised distance **0.0820**, semantic input distance 0.0096 |
| Model and comparison | fixed panel of 5 models, equal weights; 5 matched model–prompt pair(s) from `main_v1` |
| Output change | Semantic distance **0.0733**, mean unchanged control distance **0.0110**, excess distance **+0.0624** |
| Functional result | Qwen 3.8 27B: correct → correct; same final answer; response length 557 → 993 characters; GPT-OSS-120B: correct → correct; same final answer; response length 1148 → 1553 characters; GPT-OSS-20B: correct → correct; same final answer; response length 874 → 1295 characters; ALLaM-2-7B: correct → correct; final answer text changed; response length 668 → 846 characters; Gemini 3.1 Flash-Lite: correct → correct; same final answer; response length 588 → 600 characters |
| Tie status | unique |
| Evidence status | Measured retrospectively from stored main_v1 outputs; this prompt belongs to the discovery set that produced the category ranking, so the result is exploratory. |

### Responses of GPT-OSS-20B (largest effect in the panel)

**Original prompt response**

```text
The planet with the highest average surface temperature in the Solar System is **Venus**.  

Venus is hotter than Mercury for two main reasons:

1. **Atmospheric Composition** – Venus has a dense atmosphere rich in carbon‑dioxide (≈96 %) and clouds of sulfuric acid. This composition creates a powerful greenhouse effect that traps heat radiated from the surface, raising the average temperature to about 735 K (462 °C).

2. **Atmospheric Pressure** – The surface pressure on Venus is roughly 92 times that of Earth, which further enhances the greenhouse effect by increasing the optical depth of the atmosphere and preventing heat from escaping into space.

Mercury, by contrast, has virtually no atmosphere to retain heat, so its surface temperature varies dramatically between day and night, with an average temperature far lower than Venus’s.  

**Final answer:** Venus.
```

**Perturbed prompt response**

```text
The planet with the highest average surface temperature in the Solar System is **Venus**.  

**Why Venus is hotter than Mercury**

| Factor | Venus | Mercury |
|--------|-------|---------|
| **Atmospheric pressure** | ~92 bar (≈92 × Earth’s) | ~0 bar (essentially vacuum) |
| **Atmospheric composition** | ~96 % CO₂, trace N₂, H₂O vapor | Thin exosphere, negligible greenhouse gases |
| **Greenhouse effect** | Extremely strong; CO₂ traps infrared radiation, raising surface temperature to ~735 K (462 °C) | Minimal; surface radiates heat back to space |
| **Solar flux** | Receives ~1.9 × the solar energy that Earth receives (same as Mercury) | Same solar flux as Venus |
| **Albedo** | Low (~0.75) – absorbs most sunlight | High (~0.39) – reflects more sunlight |
| **Rotation** | Slow, 243 days, leading to long days and nights but the greenhouse effect dominates | Fast rotation (58.6 days) but still no greenhouse effect |

Because Venus has a dense, CO₂‑rich atmosphere, the greenhouse effect traps heat far more efficiently than on Mercury, which has almost no atmosphere. Even though both planets receive similar amounts of solar energy, Venus’s atmosphere keeps the heat from escaping, making its average surface temperature the highest in the Solar System.  

**Final answer:** Venus.
```

## 3. All operators

| Operator | Status | Char edits | d_in_char | Raw | Control | Excess | Correctness (before → after) |
|---|---|---:|---:|---:|---:|---:|---|
| `word_insertion` **(selected)** | measured | 10 | 0.0820 | 0.0733 | 0.0110 | +0.0624 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `punctuation` | measured | 1 | 0.0089 | 0.0711 | 0.0110 | +0.0601 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `word_deletion` | measured | 4 | 0.0357 | 0.0699 | 0.0110 | +0.0589 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `char_substitution` | measured | 1 | 0.0089 | 0.0529 | 0.0110 | +0.0419 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `capitalization` | measured | 1 | 0.0089 | 0.0513 | 0.0110 | +0.0403 | Qwen 3.8 27B correct→correct; GPT-OSS-120B correct→correct; GPT-OSS-20B correct→correct; ALLaM-2-7B correct→correct; Gemini 3.1 Flash-Lite correct→correct |
| `instruction_reordering` | inapplicable: inapplicable_or_no_op |  |  |  |  |  |  |
| `synonym` | inapplicable: inapplicable_or_no_op |  |  |  |  |  |  |
| `whitespace` | over_budget: d_in_char 0.1385 exceeds budget 0.10 | 18 | 0.1385 |  |  |  |  |
| `word_substitution` | inapplicable: inapplicable_or_no_op |  |  |  |  |  |  |

## 4. Input–output trade-off

Eligible edits not dominated by another edit with no more character edits and at least as much excess change:

- `punctuation`: 1 character edit(s) → excess +0.0601
- `word_insertion`: 10 character edit(s) → excess +0.0624

## 5. Source records

Full responses, per-model scores and record IDs are in the JSON file next to this report.

- `qwen/qwen3.8-27b|QA-007|treatment|word_insertion|1`: anchor record `ed9e5d75-da9e-4ad8-afb7-1e9210c6b1a2`, comparison record `a9ab483b-3e7f-4445-a1e9-7849fa2df17c`
- `openai/gpt-oss-120b|QA-007|treatment|word_insertion|1`: anchor record `200cb63a-420f-4c2c-ab90-3cba5e6e9e03`, comparison record `161d9872-fb96-48ce-a14f-3c64b69bd2c0`
- `openai/gpt-oss-20b|QA-007|treatment|word_insertion|1`: anchor record `7544fe8d-820d-4158-a15c-078772165df1`, comparison record `d398a0a7-3304-4bb1-ba7c-82de2c4ff4ae`
- `allam-2-7b|QA-007|treatment|word_insertion|1`: anchor record `ebe2bded-0926-4338-ad84-2d99a18a4aff`, comparison record `e6f896be-1972-4b2d-9579-8c277fb762b8`
- `gemini-3.1-flash-lite|QA-007|treatment|word_insertion|1`: anchor record `eff3fe6d-e7d2-4296-a76a-7392a3d6ca67`, comparison record `6740d347-ea91-48f9-ac55-94a2403ea1c5`
