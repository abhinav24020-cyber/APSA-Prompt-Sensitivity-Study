# APSA local judge pilot: LOGIC-010

This exploratory pilot evaluates how a local Gemma 4 E4B judge describes prompt and response changes for one stored logical-reasoning task. The response pairs come from Qwen 3.8 27B in `main_v1`. The earlier Groq GPT-OSS-20B pilot judged the same blinded items.

## Measured operator result

**Original prompt:** Determine the truth value of (P implies Q) when P is False and Q is False.

**Edited prompt:** Determine the truth value of (P implies Q) when P is False and Q is False

Deleting the final period changes one of 74 characters, for a normalized edit distance of `1 / 74 ≈ 0.0135`. The logical expression, premises, and requested conclusion stay the same. The edit tests whether terminal punctuation affects the way the model presents its derivation.

| Measure | Qwen 3.8 27B result |
|---|---:|
| Input edit budget | 0.10 |
| Raw MiniLM response distance | 0.1967 |
| First unchanged repeat distance | 0.0000 |
| Second unchanged repeat distance | 0.0000 |
| Mean unchanged repeat distance | 0.0000 |
| Adjusted change | **0.1967** |
| Gap to word deletion | **0.0432** |

Adjusted change is raw response distance minus the mean of the two unchanged repeat distances. Punctuation had the largest adjusted change among the five eligible measured edits. The numbers here are for Qwen 3.8 27B. The separate five-model mean for punctuation was 0.2891.

| Operator | Adjusted change | Selection status |
|---|---:|---|
| Punctuation | **0.1967** | Winner |
| Word deletion | 0.1535 | Runner-up |
| Synonym | 0.1070 | Eligible |
| Character substitution | 0.0703 | Eligible |
| Capitalization | 0.0000 | Eligible |
| Random edit | 0.1248 | Noise benchmark outside primary selection |
| Whitespace | — | Over budget |
| Word insertion | — | Over budget |
| Word substitution | — | Changed a truth value in the prompt |
| Instruction reordering | — | Inapplicable |

## Judge results

The local run used Google's quantized Gemma 4 E4B weights and llama.cpp build `b12728`. A compact JSON grammar constrained the verdict fields and let the judge select from exact excerpts on each side. APSA then validated the returned fields and evidence. Local inference incurred no API charges.

| Judge | Valid input requests | Valid output requests | Invalid responses | Rate-limited requests |
|---|---:|---:|---:|---:|
| Groq GPT-OSS-20B | 9 | 0 | 3 | 12 |
| Local Gemma 4 E4B | 11 | 13 | 0 | 0 |

There were 20 unique items and four order-swapped checks. All 24 local responses passed validation and none of the four swaps changed the overall verdict. Gemma judged eight of nine unique input pairs as preserving the task and flagged the substitution of `False` with `True`. It judged all 11 unique response pairs equivalent on the task outcome, including both unchanged controls.

### What changed in the punctuation case

Both Qwen responses ended with “Final answer: True” and matched the stored answer key. The original explained the truth-table rule. The edited response also presented a derivation using the equivalence `P implies Q ≡ ¬P ∨ Q`. Gemma recognized the unchanged correct answer and marked the pair equivalent on the task outcome, but its separate explanation-change flag missed the added derivation.

The completion counts compare two pilot configurations, including their output constraints and execution conditions. They establish that the local setup produced more usable results for this run. Estimating judgment accuracy or generalizing to other prompts requires independent human annotations and a wider evaluation sample.

## Local evidence files

- Blinded items and pairing key: `results/research-evidence/logic-010-free-pilot-package/`
- Local judgments and request metadata: `results/research-evidence/logic-010-local-gemma4-grammar/`
- Assessment and side-by-side response report: `results/research-evidence/logic-010-local-gemma4-report/`
- Earlier Groq pilot: `results/research-evidence/logic-010-groq-pilot-full/`
- Protocol and judging rubrics: [APSA research extension](APSA_research_extension.md)
