# APSA study outputs: which operator to choose, and why

Evidence snapshot: 26 November 2026. Source: stored main_v1 responses, retrospective audit, and existing APSA scoring implementation. No new model responses, real LLM judge calls, or human annotations were collected for this document.

## 1. What the user selects

Select a prompt (or select a stored response and follow its prompt ID). The operator edits the input prompt; the study measures changes in the resulting response. Identify the task category from what the prompt asks the model to return. Stored examples use the dataset label.

The output has two distinct decisions: an exploratory category recommendation, and the measured winner for this individual prompt on the fixed five-model panel. They can differ. A category recommendation alone cannot establish the best operator for an unmeasured new prompt.

## 2. Selection rule and mathematical evidence

The default input budget is epsilon = 0.10. Among eligible measured candidates within this budget, maximize mean control-adjusted semantic distance. Exact score ties prefer fewer character edits, then smaller normalized input distance; preserve remaining ties. This is maximum observed response change within a budget, not proof of the globally smallest edit or the best possible edit.

```text
edit_count = Levenshtein(original_prompt, edited_prompt)
D_in = edit_count / max(len(original_prompt), len(edited_prompt))
D_out = study MiniLM semantic distance between anchor and edited response
control(model) = (distance(anchor, unchanged_repeat_1)
                  + distance(anchor, unchanged_repeat_2)) / 2
excess(model) = D_out(model) - control(model)
panel_score = mean(excess(model)) over the fixed five-model panel
rival_gap = selected_panel_score - closest_eligible_rival_panel_score
```

Keep negative excess values. Semantic distance is not a percentage of incorrectness. Unchanged repeats estimate response variation without an input edit. Missing required measurements produce an incomplete result, not a zero effect. Target mode instead minimizes edits subject to reaching a specified output-change threshold; the trade-off frontier shows alternatives with fewer edits.

The panel is qwen/qwen3.8-27b, openai/gpt-oss-120b, openai/gpt-oss-20b, allam-2-7b, and gemini-3.1-flash-lite, equally weighted.

## 3. Category-level findings at budget 0.10

The category score averages prompt scores across complete prompts. An ineligible operator uses the unchanged-prompt fallback, contributing zero. Coverage therefore matters: this score differs from the average restricted to eligible prompts. Incomplete prompts are excluded under the existing protocol.

| Category | Exploratory recommendation | Category score | Eligible / complete prompts | Runner-up | Gap | Stored 95% paired bootstrap interval for gap |
|---|---|---:|---:|---|---:|---|
| classification | synonym | 0.0761 | 10/10 | word_insertion | 0.0060 | [-0.0388, 0.0565] |
| code_generation | word_insertion | 0.0386 | 10/10 | char_substitution | 0.0074 | [-0.0138, 0.0279] |
| logical_reasoning | punctuation | 0.0744 | 9/9 | char_substitution | 0.0114 | [-0.0115, 0.0404] |
| mathematical_reasoning | char_substitution | 0.0853 | 8/8 | synonym | 0.0256 | [-0.0474, 0.0882] |
| question_answering | punctuation | 0.0426 | 10/10 | word_insertion | 0.0044 | [-0.0065, 0.0153] |

All five intervals include zero. These data nominate operators for further testing; they do not establish reliable superiority over the runner-up or a benefit on fresh prompts. The stored intervals use 10,000 prompt bootstrap draws, seed 20261124. Only 8 mathematical and 9 logical prompts enter their complete comparisons, versus 10 in each other category.

### Category-specific research hypotheses

| Category and nominated operator | Why this is worth testing | Evidence that would support or weaken the hypothesis |
|---|---|---|
| Mathematical reasoning ? character substitution | A typo in nonnumeric prose may alter interpretation or explanation while leaving the quantities and arithmetic task fixed. | Support: preserved quantities and task, with repeatable excess response change on new prompts. Weaken: changed mathematical meaning or effects no larger than unchanged repeats. |
| Logical reasoning ? punctuation | A terminal delimiter may influence how an explanation is presented without changing premises or the requested conclusion. | Support: independently preserved premises with more explanation/answer changes than controls. Weaken: no held-out effect, or changes explained by control variation. |
| Question answering ? punctuation | Changing the final delimiter may alter answer form while leaving the entity, date, and requested fact fixed. | Support: preserved fact request and reproducible changes beyond controls. Weaken: different question meaning, or unchanged responses on fresh prompts. |
| Classification ? synonym | Replacing an instruction verb may affect the response while preserving the evidence and permitted class labels. | Support: reviewers confirm equivalent label task and a held-out effect. Weaken: altered label meaning or no advantage over the global operator. |
| Code generation ? word insertion | Adding a cue such as Carefully may affect implementation choices without changing the signature, restrictions, or required behavior. | Support: preserved contract and reproducible implementation/test-outcome differences. Weaken: no effect beyond controls or an altered contract. |

These are behavioral hypotheses, not verified accounts of model internals. Testing edit location requires matched edits of the same type at different locations. The present winners do not isolate location as a causal factor.

## 4. Worked prompt outputs from all five categories

Example selection was fixed for illustration: the first stored prompt ID in each category, except the previously specified acceptance example LOGIC-010. These five cases are not a representative effect estimate or a selection of the five largest effects. Each linked appendix includes all ten operators, exact edits, full response pairs, control arithmetic, correctness evidence, and source IDs.

### CLASS-001 ? classification

**Category source:** dataset. Product review sentiment classification

**Original prompt**

```text
Classify the sentiment of the following product review as Positive, Negative, or Neutral: 'The battery life is acceptable, but the screen scratches easily and customer support was unhelpful.'
```

**Selected edited prompt**

```text
classify the sentiment of the following product review as Positive, Negative, or Neutral: 'The battery life is acceptable, but the screen scratches easily and customer support was unhelpful.'
```

**Measured decision:** capitalization produced the largest control-adjusted change (+0.0950) among 6 eligible, measured edits within budget 0.10. The gap to synonym (+0.0846) was +0.0104. Preservation evidence: not flagged by the retrospective audit (operator audited by a sample of 5 candidates).

**Input arithmetic:** 1 / 191 = 0.005236, within 0.10.

**Output arithmetic (panel means):** raw 0.095022 - control 0.000000 = excess 0.095022.

**Rival arithmetic:** 0.095022 - 0.084637 = 0.010385, using unrounded values internally.

**Reason for testing the edit:** Only the initial C in Classify becomes lowercase. The label set and review text remain identical. A change in response framing is plausible, but the mechanism has not been tested. The category nominee is synonym; this individual prompt instead selects capitalization from measured results.

**Recorded answer or behavior outcomes:**

| Model | Before correct | After correct | Recorded answer/functional change | Scoring evidence |
|---|---|---|---|---|
| qwen/qwen3.8-27b | yes | yes | no | answer_key |
| openai/gpt-oss-120b | yes | yes | no | answer_key |
| openai/gpt-oss-20b | yes | yes | no | answer_key |
| allam-2-7b | no | yes | yes | answer_key |
| gemini-3.1-flash-lite | yes | yes | no | answer_key |

These are stored answer-key or unit-test outcomes. Passing the recorded tests does not prove correctness on all possible inputs. An improvement from incorrect to correct also counts as a change; maximizing distance does not specifically maximize failure.

**Independent input-preservation judge:** pending. **Output-difference judge:** pending. **Independent human validation:** pending. Retrospective audit eligibility is not equivalent to universal human-confirmed preservation.

[Full measured report](category_operator_examples/CLASS-001__panel__budget-0.10.md) ? [Reproducibility record](category_operator_examples/CLASS-001__panel__budget-0.10.json)

### CODE-001 ? code_generation

**Category source:** dataset. Python string reversal without slice step

**Original prompt**

```text
Write a Python function reverse_string(s: str) -> str that returns the reversed string without using Python's built-in slice step [::-1] or reversed().
```

**Selected edited prompt**

```text
Carefully Write a Python function reverse_string(s: str) -> str that returns the reversed string without using Python's built-in slice step [::-1] or reversed().
```

**Measured decision:** word_insertion produced the largest control-adjusted change (+0.0303) among 6 eligible, measured edits within budget 0.10. The gap to word_deletion (+0.0221) was +0.0083. Preservation evidence: not flagged by the retrospective audit (operator audited by a sample of 5 candidates).

**Input arithmetic:** 10 / 161 = 0.062112, within 0.10.

**Output arithmetic (panel means):** raw 0.030322 - control 0.000000 = excess 0.030322.

**Rival arithmetic:** 0.030322 - 0.022054 = 0.008268, using unrounded values internally.

**Reason for testing the edit:** A leading tone cue ('Carefully') can change which implementation the model writes while preserving the signature and input/output contract. This motivates the comparison; the measured score and eligibility rule, rather than this hypothesis alone, justify selection.

**Recorded answer or behavior outcomes:**

| Model | Before correct | After correct | Recorded answer/functional change | Scoring evidence |
|---|---|---|---|---|
| qwen/qwen3.8-27b | yes | yes | no | unit_tests |
| openai/gpt-oss-120b | yes | yes | no | unit_tests |
| openai/gpt-oss-20b | yes | yes | no | unit_tests |
| allam-2-7b | no | yes | yes | unit_tests |
| gemini-3.1-flash-lite | yes | yes | no | unit_tests |

These are stored answer-key or unit-test outcomes. Passing the recorded tests does not prove correctness on all possible inputs. An improvement from incorrect to correct also counts as a change; maximizing distance does not specifically maximize failure.

**Independent input-preservation judge:** pending. **Output-difference judge:** pending. **Independent human validation:** pending. Retrospective audit eligibility is not equivalent to universal human-confirmed preservation.

[Full measured report](category_operator_examples/CODE-001__panel__budget-0.10.md) ? [Reproducibility record](category_operator_examples/CODE-001__panel__budget-0.10.json)

### LOGIC-010 ? logical_reasoning

**Category source:** dataset. Material implication truth value evaluation

**Original prompt**

```text
Determine the truth value of (P implies Q) when P is False and Q is False.
```

**Selected edited prompt**

```text
Determine the truth value of (P implies Q) when P is False and Q is False
```

**Measured decision:** punctuation produced the largest control-adjusted change (+0.2891) among 5 eligible, measured edits within budget 0.10. The gap to char_substitution (+0.1798) was +0.1093. Preservation evidence: not flagged by the retrospective audit (operator audited by a sample of 5 candidates).

**Input arithmetic:** 1 / 74 = 0.013514, within 0.10.

**Output arithmetic (panel means):** raw 0.289093 - control 0.000000 = excess 0.289093.

**Rival arithmetic:** 0.289093 - 0.179823 = 0.109270, using unrounded values internally.

**Reason for testing the edit:** A terminal punctuation edit changes the cue at the end of the prompt while leaving premises and the requested conclusion intact. This motivates the comparison; the measured score and eligibility rule, rather than this hypothesis alone, justify selection.

**Recorded answer or behavior outcomes:**

| Model | Before correct | After correct | Recorded answer/functional change | Scoring evidence |
|---|---|---|---|---|
| qwen/qwen3.8-27b | yes | yes | no | answer_key |
| openai/gpt-oss-120b | yes | yes | no | answer_key |
| openai/gpt-oss-20b | yes | yes | no | answer_key |
| allam-2-7b | no | yes | yes | answer_key |
| gemini-3.1-flash-lite | yes | yes | no | answer_key |

These are stored answer-key or unit-test outcomes. Passing the recorded tests does not prove correctness on all possible inputs. An improvement from incorrect to correct also counts as a change; maximizing distance does not specifically maximize failure.

**Independent input-preservation judge:** pending. **Output-difference judge:** pending. **Independent human validation:** pending. Retrospective audit eligibility is not equivalent to universal human-confirmed preservation.

[Full measured report](category_operator_examples/LOGIC-010__panel__budget-0.10.md) ? [Reproducibility record](category_operator_examples/LOGIC-010__panel__budget-0.10.json)

### MATH-001 ? mathematical_reasoning

**Category source:** dataset. Multi-step arithmetic ratio and percentage calculation

**Original prompt**

```text
A store sells apples in bags of 5 for $3.00. On Tuesday, they offer a 20% discount on all apple bags. If a customer buys 15 apples on Tuesday, how much do they pay in total?
```

**Selected edited prompt**

```text
A store sells apples in 6ags of 5 for $3.00. On Tuesday, they offer a 20% discount on all apple bags. If a customer buys 15 apples on Tuesday, how much do they pay in total?
```

**Measured decision:** char_substitution produced the largest control-adjusted change (+0.0463) among 5 eligible, measured edits within budget 0.10. The gap to word_insertion (+0.0449) was +0.0013. Preservation evidence: not flagged by the retrospective audit (every candidate of this operator was audited).

**Input arithmetic:** 1 / 173 = 0.005780, within 0.10.

**Output arithmetic (panel means):** raw 0.046472 - control 0.000196 = excess 0.046275.

**Rival arithmetic:** 0.046275 - 0.044943 = 0.001333, using unrounded values internally.

**Reason for testing the edit:** A typo in prose changes how the task is rendered while leaving quantities and the requested result intact. This motivates the comparison; the measured score and eligibility rule, rather than this hypothesis alone, justify selection.

**Recorded answer or behavior outcomes:**

| Model | Before correct | After correct | Recorded answer/functional change | Scoring evidence |
|---|---|---|---|---|
| qwen/qwen3.8-27b | yes | yes | no | answer_key |
| openai/gpt-oss-120b | yes | yes | no | answer_key |
| openai/gpt-oss-20b | yes | yes | no | answer_key |
| allam-2-7b | yes | no | yes | answer_key |
| gemini-3.1-flash-lite | yes | yes | no | answer_key |

These are stored answer-key or unit-test outcomes. Passing the recorded tests does not prove correctness on all possible inputs. An improvement from incorrect to correct also counts as a change; maximizing distance does not specifically maximize failure.

**Independent input-preservation judge:** pending. **Output-difference judge:** pending. **Independent human validation:** pending. Retrospective audit eligibility is not equivalent to universal human-confirmed preservation.

[Full measured report](category_operator_examples/MATH-001__panel__budget-0.10.md) ? [Reproducibility record](category_operator_examples/MATH-001__panel__budget-0.10.json)

### QA-001 ? question_answering

**Category source:** dataset. Physics Nobel prize discovery query

**Original prompt**

```text
Which physicist received the Nobel Prize in Physics in 1921 for his discovery of the law of the photoelectric effect?
```

**Selected edited prompt**

```text
Which physicist received the Nobel Prize in Physics in 1921 for his discovery of the law of the photoelectric effect
```

**Measured decision:** punctuation produced the largest control-adjusted change (+0.0225) among 5 eligible, measured edits within budget 0.10. The gap to word_deletion (+0.0105) was +0.0120. Preservation evidence: not flagged by the retrospective audit (operator audited by a sample of 5 candidates).

**Input arithmetic:** 1 / 117 = 0.008547, within 0.10.

**Output arithmetic (panel means):** raw 0.022504 - control 0.000000 = excess 0.022504.

**Rival arithmetic:** 0.022504 - 0.010522 = 0.011981, using unrounded values internally.

**Reason for testing the edit:** Editing the question's final delimiter can change the form or length of the answer while keeping the requested fact fixed. This motivates the comparison; the measured score and eligibility rule, rather than this hypothesis alone, justify selection.

**Recorded answer or behavior outcomes:**

| Model | Before correct | After correct | Recorded answer/functional change | Scoring evidence |
|---|---|---|---|---|
| qwen/qwen3.8-27b | yes | yes | no | answer_key |
| openai/gpt-oss-120b | yes | yes | no | answer_key |
| openai/gpt-oss-20b | yes | yes | no | answer_key |
| allam-2-7b | yes | no | yes | answer_key |
| gemini-3.1-flash-lite | yes | yes | no | answer_key |

These are stored answer-key or unit-test outcomes. Passing the recorded tests does not prove correctness on all possible inputs. An improvement from incorrect to correct also counts as a change; maximizing distance does not specifically maximize failure.

**Independent input-preservation judge:** pending. **Output-difference judge:** pending. **Independent human validation:** pending. Retrospective audit eligibility is not equivalent to universal human-confirmed preservation.

[Full measured report](category_operator_examples/QA-001__panel__budget-0.10.md) ? [Reproducibility record](category_operator_examples/QA-001__panel__budget-0.10.json)

## 5. Reading LOGIC-010 correctly

For GPT-OSS-120B alone, deleting the final period changes 1/74 characters (0.0135). The original response explains material implication and ends with Final answer: True; the edited response contains only Final answer: True. Response length falls from 209 to 18 characters. Both answers are correct.

```text
single-model control = (0.0000 + 0.0000) / 2 = 0.0000
single-model excess = 0.7999 - 0.0000 = 0.7999
five-model mean excess = 0.2891
five-model rival gap = 0.2891 - 0.1798 = 0.1093 (rounded)
```

Thus a large semantic distance can accompany explanation removal with an unchanged correct final answer. Do not describe this single-model case as an answer failure. Other panel members must be checked separately, as the table above shows. The five-model score is not the single-model 0.7999 score.

## 6. What happened to the ten operators?

Each appendix includes char_substitution, capitalization, punctuation, whitespace, word_insertion, word_deletion, synonym, word_substitution, instruction_reordering, and random_edit. A row can be eligible/measured, over budget, meaning-changing, inapplicable, or incomplete. Excluded rows cannot win merely because their raw distance is large.

random_edit remains a noise benchmark, outside the primary meaning-preserving selection. For LOGIC-010 on GPT-OSS-120B it also produces about 0.7999 excess, but it is unaudited and does not replace punctuation as the primary winner. This exclusion comes from the study protocol, not from suppressing an inconvenient result.

## 7. What can be claimed in the research paper?

**Supported descriptive claim:** Under the stated budget, panel, retrospective eligibility rules, and evaluated edits, the selected operator achieved the largest measured control-adjusted response distance for the displayed prompt. Exact source pairs and alternative scores are provided.

**Exploratory claim:** The category leaders suggest hypotheses about which operators to try on fresh prompts. They are not established category-wide optima. A single generated candidate per operator/seed does not exhaust all possible edits.

**Pending evidence:** Independent preservation annotations, live LLM judgments, judge agreement against independently adjudicated human labels, matched edit-location experiments, and fresh held-out comparisons against a fixed global policy. Mock evaluations provide workflow checks only.

A research explanation should combine the exact edit, the numeric comparison, and the observed answer or behavior outcome. It should distinguish why an experiment was designed from why its observed candidate was selected. Neither the distances nor a persuasive rationale establishes the internal cause of the model response.

## 8. Reproduce or inspect a prompt

Run from the repository root in PowerShell. These commands reuse stored evidence and do not make paid API calls.

```powershell
$py = ".\.venv\Scripts\python.exe"
foreach ($id in @("CLASS-001", "CODE-001", "LOGIC-010", "MATH-001", "QA-001")) {
    & $py experiments/category_operators.py prompt --prompt-id $id --budget 0.10
}
& $py experiments/category_operators.py prompt --prompt-id LOGIC-010 --model gpt-oss-120b --budget 0.10
```

For a different stored prompt, replace the ID. For pasted text, prepare and review candidates first; their output effects remain unmeasured until matching responses and controls exist. Do not copy a category-average score onto a new prompt.

## 9. Evidence and implementation sources

- [Category rankings](../../results/study/main_v1/analysis/category_operator_rankings.csv)
- [Locked exploratory nominees and source hashes](../../results/study/main_v1/analysis/category_operator_nominees.json)
- [Scoring settings and bootstrap specification](../../results/study/main_v1/analysis/category_operator_settings.json)
- [Shared scoring and selection implementation](../../src/apsa/analysis/category_operators.py)
- [Shared report implementation](../../src/apsa/analysis/category_operator_reports.py)
- [Research protocol, judging rubrics, and limitations](APSA_research_extension.md)
- [Quickstart](../category_operator_quickstart.md)
