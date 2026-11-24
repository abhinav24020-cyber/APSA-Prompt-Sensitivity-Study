# APSA Implementation Plan for Selecting Perturbation Operators by Prompt Category

For each of the five APSA prompt categories, identify the operator that produces the largest **average change in the model response beyond unchanged-prompt variation**, subject to a common edit budget and preservation of the task. Also report the **largest single change observed** in each category, the prompt and model that produced it, and whether the answer or task behavior changed. The average supports choosing an operator for a new prompt in a category. The single-case maximum documents what happened to one evaluated prompt.

An exploratory analysis of `main_v1` found four operators leading across the five categories. Each leader’s gap over its runner-up had a prompt-level interval that included zero. The results give the paper concrete estimates and cases to discuss, and identify the operators to lock for an independent validation run. [Original analysis plan](analysis_plan.md) · [Main study paper](../paper/APSA_research_paper.md)

## 1. What counts as maximum change

Use `d_out_sem` as the primary response measure so the new analysis is comparable to `main_v1`. It is one minus cosine similarity between normalized `all-MiniLM-L6-v2` embeddings of the anchor and comparison responses, clipped to [0, 1], with identical stripped responses assigned zero. Embedding distance measures change in the whole response and can be high when a model adds an explanation while keeping its answer. Report character and token distance, answer identity, and correctness alongside it. For code, use task-specific test results for behavioral claims. [Main study scoring code](../../experiments/analyze_study.py) · [Sentence-BERT](https://aclanthology.org/D19-1410/)

Apply the same input budget to all operators within a comparison. Use `0 < d_in_char ≤ 0.10` for the main category comparison, where `d_in_char` is Levenshtein edit count divided by the length of the longer prompt. This is one of the study’s existing budget levels. Repeat the analysis at 0.01, 0.02, 0.05, and without a character cap to show how the result changes as edits become larger. Report the absolute character edit count and semantic input distance for examples. [Original budget analysis](analysis_plan.md) · [Input distance implementation](../../src/apsa/metrics/input_distance/lexical.py)

### Control-adjusted effect and category score

For prompt `p`, model `m`, and eligible operator `o`, calculate the difference between the anchor-to-treatment distance and the average anchor-to-control distance from two unchanged repeats on the same model and prompt.

```text
control(p, m) = mean(distance(anchor, repeat_1), distance(anchor, repeat_2))
effect(p, m, o) = distance(anchor, treatment_o) - control(p, m)
prompt_score(p, o) = mean over the fixed model panel of effect(p, m, o)
category_score(c, o) = mean over prompts p in category c of prompt_score(p, o)
```

- **Category-level choice.** Apply one operator to the whole category. If its candidate is inapplicable, exceeds the budget, or fails the meaning audit, the policy sends the original prompt. Assign this fallback zero expected excess distance by definition. Preserve negative measured effects for eligible treatments. Give prompts equal weight and give each of the five models equal weight within a prompt. Rank by the full-precision category score and report any ties.
- **Coverage and head-to-head comparison.** Report the number of eligible prompts before and after generation exclusions. Also report the mean excess among eligible prompts and the paired gap on prompts where both operators qualify. These quantities show whether an operator leads because of wider coverage, stronger edits on the same prompts, or both.
- **Prompt-level choice and observed maximum.** For each prompt, rank eligible operators by mean excess distance across models. For the category’s single-case maximum, find the largest raw `d_out_sem` among eligible cases and report its control average, excess distance, edit, model, output change, and correctness. Also record the largest single excess distance if it identifies a different case. Preserve all tied cases. Both maxima are over the candidates that were actually tested.
- **Incomplete measurements.** Retry a missing or unusable eligible generation under the existing retry policy. If an eligible treatment, anchor, or required control is still missing, empty, truncated, or lacks a finite score, put that prompt outside the common complete cohort for the ranking. Publish the exclusion and reason. This keeps every ranked operator on the same prompts and model panel. Record generation and candidate-building errors independently of the planned unchanged fallback.

## 2. Exploratory results from the existing study

These estimates use the 50 selected `main_v1` prompts, five models, two unchanged repeats, one seed-42 candidate per prompt and operator, and the stored scores. The analysis screens out candidates flagged as meaning-changing in the existing audit. The audit sampled some operator families, so an unflagged candidate carries the level of review described in the audit. The random edit operator serves as a noise benchmark. At the 0.10 budget, the common cohort excludes `LOGIC-007`, `MATH-005`, and `MATH-008` because complete nonempty, untruncated observations were unavailable for all eligible conditions. [Study manifest](../../results/study/main_v1/study_manifest.json) · [Candidates](../../results/study/main_v1/candidates.jsonl) · [Paired scores](../../results/study/main_v1/processed/analysis_pairs.csv) · [Prompt audit](../../config/experiments/main_study_semantic_audit.yaml)

### All operator scores at the 0.10 budget

Each cell shows the mean excess semantic distance and the number of eligible prompts in parentheses. A dash denotes zero eligible prompts and a policy score of zero. Scores use the common category denominator shown in the header.

| Operator | Classification (10) | Code (10) | Logic (9) | Math (8) | QA (10) |
|---|---:|---:|---:|---:|---:|
| `capitalization` | 0.0574 (10) | 0.0226 (10) | 0.0544 (9) | 0.0592 (8) | 0.0341 (10) |
| `char_substitution` | 0.0393 (9) | 0.0312 (7) | 0.0630 (8) | **0.0853 (8)** | 0.0339 (9) |
| `instruction_reordering` | — | — | — | — | — |
| `punctuation` | 0.0638 (10) | 0.0150 (10) | **0.0744 (9)** | 0.0430 (8) | **0.0426 (10)** |
| `synonym` | **0.0761 (10)** | 0.0256 (10) | 0.0471 (5) | 0.0597 (4) | — |
| `whitespace` | — | — | — | — | — |
| `word_deletion` | 0.0407 (10) | 0.0207 (10) | 0.0411 (8) | 0.0442 (8) | 0.0169 (9) |
| `word_insertion` | 0.0701 (10) | **0.0386 (10)** | 0.0552 (8) | 0.0585 (6) | 0.0382 (7) |
| `word_substitution` | 0.0199 (2) | 0.0192 (9) | 0.0071 (2) | 0.0342 (3) | 0.0034 (1) |

### How far the leader was ahead

The intervals below resample paired prompt-level gaps 10,000 times with seed `20261124`. They describe variability for the displayed pairs of operators. The same data selected those pairs, so claims of superiority require the independent validation in Section 4. The shared-eligible gap averages the same contrast only on prompts both operators could edit.

| Prompt category | Leader and runner-up | Paired gap [exploratory 95% interval] | Gap on shared eligible prompts |
|---|---|---:|---:|
| Classification | `synonym` vs `word_insertion` | +0.0060 [−0.0388, +0.0565] | +0.0060 (10) |
| Code generation | `word_insertion` vs `char_substitution` | +0.0074 [−0.0138, +0.0279] | −0.0037 (7) |
| Logical reasoning | `punctuation` vs `char_substitution` | +0.0114 [−0.0115, +0.0404] | +0.0095 (8) |
| Mathematical reasoning | `char_substitution` vs `synonym` | +0.0256 [−0.0474, +0.0882] | −0.0351 (4) |
| Question answering | `punctuation` vs `word_insertion` | +0.0044 [−0.0065, +0.0153] | +0.0020 (7) |

Coverage explains the direction of the code and math rankings. In code, insertion covered 10 prompts to the typo’s 7. In math, character substitution covered 8 prompts to the synonym’s 4. On their shared prompts, the lower-ranked policy had the larger average effect in both categories. Classification also depends on the outcome measure. Filler insertion led for both character and token distance, while synonym substitution led for the embedding distance.

Among eligible, scorable treatment pairs for each leader, the correct-to-incorrect and incorrect-to-correct counts were respectively 1 and 1 in classification (50 pairs), 0 and 2 in code (50), 1 and 2 in logic (45), 1 and 1 in math (40), and 1 and 0 in QA (50). These are recorded score changes. The case review determines which flips reflect a task error, an output-format failure, or a scoring artifact.

### Largest single change observed by category

The matched control mean is zero in each of the displayed cases, so the raw and excess maxima coincide. The denominator in the fourth column counts eligible model–prompt–operator results searched within each category. Every case below kept the correct answer or passed the same task tests in both responses. [Individual paired outputs](../../results/study/main_v1/processed/analysis_pairs.csv)

| Prompt category | Operator and evidence | `d_in_char` | Maximum `d_out_sem` / eligible results searched | Observed output change |
|---|---|---:|---:|---|
| Classification | `synonym`, `CLASS-008`, ALLaM-2-7B | 0.0406 | 0.6848 / 305 | A detailed justification became a short response with the same `Critical` label. |
| Code generation | `word_insertion`, `CODE-007`, Qwen 3.8 27B | 0.0641 | 0.2243 / 330 | The anagram implementation switched from sorting characters to comparing frequency counts. Both passed the existing tests. |
| Logical reasoning | `punctuation`, `LOGIC-010`, GPT-OSS-120B | 0.0135 | 0.7999 / 245 | Removing the final period changed an explanation of implication to a bare `True` answer. |
| Mathematical reasoning | `capitalization`, `synonym`, and `word_substitution` tied on `MATH-010`, GPT-OSS-120B | 0.0128, 0.0625, 0.0625 respectively | 0.7400 / 225 | The response expanded from the answer `31` to a determinant calculation ending in `31`. |
| Question answering | `punctuation`, `QA-013`, GPT-OSS-120B | 0.0091 | 0.3699 / 230 | Removing the final question mark added context about judicial review while retaining `Marbury v. Madison`. |

### Effect of the edit budget

| Prompt category | 0.01 | 0.02 | 0.05 | 0.10 | No character cap |
|---|---|---|---|---|---|
| Classification | Punctuation | Punctuation | Synonym | Synonym | Synonym |
| Code generation | Character substitution | Character substitution | Character substitution | Filler insertion | Filler insertion |
| Logical reasoning | Character substitution | Punctuation | Punctuation | Punctuation | Instruction reordering |
| Mathematical reasoning | Character substitution | Character substitution | Character substitution | Character substitution | Whitespace |
| Question answering | Capitalization | Punctuation | Punctuation | Punctuation | Punctuation |

The table rebuilds the common complete cohort at each budget, so a change in rank can reflect both eligibility and the set of complete prompts. Also rerun on the intersection of cohorts when attributing a change to the budget alone. The existing whitespace operator doubles spaces across the full prompt, and the existing structural operator moves a sentence. Neither implementation yielded an eligible edit at 0.10 in `main_v1`. The uncapped results still require the audit screen. [Whitespace operator](../../src/apsa/perturbations/surface/whitespace.py) · [Instruction reordering operator](../../src/apsa/perturbations/structural/reordering.py)

## 3. Why test these operators in each category

These are explanations to test on held-out prompts. Each rationale identifies which part of the prompt the operator touches, what the audit must preserve, and what output pattern would support the explanation. Prior work on prompt formatting motivates testing response sensitivity to small changes. Behavioral invariance tests motivate checking that the task’s expected answer stays fixed. [Sclar et al., 2024](https://arxiv.org/abs/2310.11324) · [Ribeiro et al., 2020](https://aclanthology.org/2020.acl-main.442/)

| Category and candidate to validate | Reason for testing it | Evidence to collect |
|---|---|---|
| **Classification — `synonym`** | Replacing an instruction verb such as `Classify` with `Categorize` changes the cue used to request a label while preserving the label set and evidence. The operator led on embedding distance and covered 10/10 prompts. Check that label names, quoted inputs, and the mapping from evidence to the gold label are unchanged. | Separate explanation-only changes from label flips and extraction errors. In `CLASS-002` the unchanged repeats and anchor scored `Business`; GPT-OSS-20B returned `Politics` after the verb changed (`d_out_sem = 0.4741`). Check whether instruction-verb substitutions produce label flips consistently across fresh items and models. |
| **Code generation — `word_insertion`** | The seed-42 operator adds `Carefully` at the start. A tone cue can change which implementation the model writes while preserving the signature, input/output contract, and examples. This operator led across the category and covered 10/10 prompts. Character substitution had greater average impact on the seven shared eligible prompts, which makes it a direct competitor. | Verify that the diff only inserts the filler. The current implementation splits and rejoins words, so it can also change spacing on other inputs. Compare normalized syntax or implementation approach, strict signature compliance, and test outcomes. In `CODE-007`, both algorithms passed the available suite. Additional edge cases can detect behavior differences that the shared pass result leaves open. |
| **Logical reasoning — `punctuation`** | A terminal punctuation edit changes the cue at the end of the prompt while leaving premises and the requested conclusion intact. It covered 9/9 complete prompts and led at 0.02, 0.05, and 0.10. Preserve logical operators, negation, entity identities, premise dependencies, and punctuation inside expressions. | Compare normalized conclusions and whether each output provides an explanation. Omitting `LOGIC-010` in discovery moved punctuation to third (0.0476), with filler insertion first (0.0621). Check whether this concentration recurs on new prompts. In the uncapped analysis, include reordering where clause dependencies and scope are preserved. |
| **Mathematical reasoning — `char_substitution`** | A typo in prose can change how the task is rendered while leaving the mathematical problem intact. This operator led at all four bounded budgets and covered 8/8 complete prompts at 0.10. Protect quantities, signs, units, variables, inequalities, and the requested result. In `MATH-009`, `many` became `m@ny` while the answer remained 2 hours. | Score mathematical equivalence, units, and correctness separately from the presence or length of a derivation. Show the comparison against synonyms on their shared prompts because the typo’s category lead depends on broader coverage. Also show model-specific results to reveal whether a small part of the model panel drives the average. |
| **Question answering — `punctuation`** | Editing a question’s final delimiter can change the form or length of the answer while keeping its requested fact fixed. It led at 0.02, 0.05, 0.10, and without a character cap, with full coverage at 0.10. Protect quoted passages, names, dates, requested answer spans, and punctuation that belongs to the source text. | Score equivalent answer aliases and supporting context separately. In `QA-013`, the model added a contextual sentence while returning the same case name. Check fact or entity flips separately and audit answer-marker failures before counting them as factual errors. |

For each category, label inspected cases as response style or format change, answer change, code implementation change, tested behavior change, or scoring artifact as applicable. One case can have multiple labels. Review all observed correct-to-incorrect cases for the five leading operators and a fixed sample of large-distance cases that retained correctness. Record the edit, reference answer, output evidence, and reason for each label. This record supports the paper’s explanations without treating the model’s internal response to an edit as observed.

## 4. How to establish a category winner on new prompts

1. **Lock the protocol before collecting validation outputs.** Freeze the nominated operator in each category, the nine operator policies, the unchanged reference, the 0.10 input budget, one prespecified candidate attempt per prompt–operator using a fixed seed, eligibility rules, model weights, system prompt, decoding settings, metrics, missing-data handling, and analysis family. Record the prompt sampling frame, validation IDs and hashes, and model/provider versions. Choose a target effect for power planning and simulate precision using the observed prompt-level contrasts. Set the validation sample size before viewing new outputs. The unused dataset contains only 2 QA items tagged `exact_match`, so collect new independently scored prompts to obtain adequate QA coverage. Screen for prompt and template overlap with `main_v1`. [Dataset](../../data/baseline_prompts.csv) · [Dataset card](../../data/dataset_card.md)
2. **Verify preservation before generation.** Have two reviewers independently label each candidate `preserved`, `changed`, or `uncertain` from the prompt pair and reference specification, with model outputs hidden. Adjudicate disagreements, report agreement and verdict counts, and allow only the final `preserved` cases into the bounded comparison. Log what changed and why. Use input embedding distance as a descriptive metric. A small embedding distance can coexist with a changed constraint or answer.
3. **Run matched conditions.** Keep the anchor, two unchanged repeats, and eligible treatments within the same model and prompt block. Use the same system message and decoding configuration. Randomize the order of treatment and repeat requests within each block with a recorded seed to reduce time or request-order effects. Preserve retry provenance and publish the denominator for each metric. A fresh model endpoint or changed configuration defines a new validation panel and should be identified in the result.
4. **Compare the locked nominee with every alternative.** On held-out prompts, compute one paired difference per prompt for each nominee-versus-competing-policy contrast, including the unchanged reference. Across five categories and nine contrasts per category, form one-sided family-wise 95% lower bounds using Bonferroni-adjusted paired *t* bounds. For each contrast, the bound is `mean_gap - t_quantile(1 - 0.05/45, n-1) × SD_gap / sqrt(n)`. This is a large-sample mean comparison under independent prompt sampling. Keep related templates within the same sampling unit if they cannot be removed, and use the independent units for inference. Report prompt-level bootstrap intervals for the point estimates and note unstable intervals or degenerate contrasts explicitly. A zero-variance sample warrants a conservative unresolved label unless the contrast is identically zero by design.
5. **Apply the claim rule.** Call the nominee a validated winner for a category only when its adjusted lower bound is above zero against every alternative and the unchanged reference. If the paper claims a practically meaningful improvement, require all bounds to exceed a positive margin fixed in step 1 and justified in semantic-distance units. Otherwise report the held-out leader, rivals whose uncertainty leaves the ranking unresolved, and the supporting effect estimates. Any new leader chosen from validation outputs needs a new independent validation sample for a confirmatory winner claim.

For robustness, show results by model, with each prompt omitted in turn, on shared-eligible prompts, and under the other budgets and output metrics. A shared upper bound allows different actual edit sizes. To assess an operator effect at a comparable edit size, also report paired contrasts on prompts where both edits fall in the same prespecified input-distance band. Report correct-to-incorrect and incorrect-to-correct separately, with a scorable denominator and the anchor-correct denominator for degradation conditional on a correct anchor. For code, report strict entry-point failures and test differences separately. The 0.10 result and its holdout rule govern the main claim. A paper claim that category-specific choices improve on using one operator for all categories also needs a separate held-out comparison against a single global policy selected and frozen on discovery data.

## 5. Repository implementation handoff

| Step | Implementation and verification |
|---|---|
| **Load scored inputs** | Extend `experiments/analyze_study.py` with a category ranking stage that consumes `analysis_pairs.csv`, `candidates.jsonl`, and the study manifest. Use the manifest to enumerate all expected prompts, models, controls, and operators. Join candidate audits by `perturbation_id` in new runs and use `(prompt_id, operator)` for the existing single-candidate run. Check unique treatment keys, distinct control repetitions, candidate consistency, and valid metric ranges. |
| **Build the analysis cohort** | Materialize one row per prompt, model, and operator with an explicit eligibility and measurement state. Include flags for inapplicable, over budget, audit rejected, generator error, and incomplete scoring. Build complete prompt cohorts per budget and preserve exclusions by category. Reuse the existing paired scores, answer keys, and code scoring rather than re-embedding outputs for the retrospective analysis. |
| **Rank and trace the evidence** | Generate `analysis/category_operator_rankings.csv` with the score, coverage, conditional mean, rank, gap, interval, and validation status. Generate `analysis/prompt_operator_maxima.csv` with prompt/category, operator, model scope, candidate and pair IDs, raw distance, control distance, excess distance, input edit count, functional outcome, and tie status. Include an explicit missing or inapplicable status where no result is available. Save run settings, audit versions, and exclusions with machine-readable results. |
| **Add publication outputs** | Produce a category-by-operator heatmap annotated with score and coverage, a paired-gap plot with a zero reference line, and a table of maximum cases with prompt and pair IDs. For held-out results, show the gap against the closest competing policy and the simultaneous lower bound. Label output distance and functional outcomes with their respective units and denominators. |
| **Check before a live run** | Reproduce Section 2 from `main_v1` without provider calls. Run the new ranking logic against a mock or small fixture with unequal coverage, zero controls, a negative effect, duplicate controls, a missing eligible pair, and exact ties. Check the data reconciliation, ranks, fallback arithmetic, and exclusion reasons. Use a separate validation study ID with a locked config and an explicit prompt allowlist so the current runner’s first-in-file selection rule cannot reselect the discovery prompts. |

The current runner already handles candidate provenance, unchanged controls, and provider records. The analysis entry point for an existing study is `python experiments/analyze_study.py --study-dir results/study/main_v1`. The category outputs and validation configuration above are implementation work. This implementation plan includes a read-only reproduction of the exploratory comparison below. [Study runner](../../experiments/run_study.py) · [Study analysis](../../experiments/analyze_study.py) · [Statistics helpers](../../src/apsa/analysis/study_statistics.py)

## 6. Suggested research paper wording

> We compared nine fixed perturbation policies within five task categories, under a normalized character edit budget of 0.10. For each model and prompt, we subtracted the mean response distance from two unchanged repetitions from the response distance produced by an eligible perturbation. We averaged these effects equally across models and prompts and used the unchanged prompt when an operator lacked an eligible candidate. Synonym substitution led for classification (0.0761), filler insertion for code generation (0.0386), punctuation for logical reasoning (0.0744) and question answering (0.0426), and character substitution for mathematical reasoning (0.0853). Each leader–runner-up exploratory interval included zero. The largest single mathematical reasoning change came from three tied edits on one prompt and kept the correct answer. These findings describe the evaluated models, prompts, operators, and budget and nominate operators for independent validation.

## 7. What the final output should show

Each result starts with the selected prompt and its category. It returns the operator, the exact edit, the before-and-after prompts and responses, the matched control distance, and the effect on answer correctness. Include the model or model panel, the budget, the number of eligible alternatives measured, and the evidence status. The paper can summarize these records in one table, with one row per prompt and a reference to the full evidence record. [Stage-by-stage implementation guide](category_operator_stage_by_stage.md)

### How the operator is chosen

1. **Recommend from the category.** At the 0.10 budget, the current starting choices are synonym substitution for classification, filler insertion for code generation, punctuation for logic and QA, and character substitution for math. For a tighter budget, use the matching category ranking in Section 2 and label it exploratory. For a new prompt, recommend only edits that fit the budget and preserve the task. Label a recommendation as unmeasured until the prompt has been run.
2. **Measure the selected prompt.** To establish the best evaluated operator for this prompt, test all eligible alternatives on the same model or fixed model panel with matched unchanged controls. Prefer the largest control-adjusted response change within the chosen budget. Break exact score ties by the fewest character edits and then by the smallest normalized input distance. Preserve all tied operators in the evidence record.
3. **Show the smallest edit that achieves the intended effect.** When a target response change is specified before evaluation, report the eligible edit with the fewest character changes that reaches it. Without a target, show the input–output trade-off alongside the best within-budget edit. Keep an edit on that trade-off if no other evaluated edit is equally small or smaller and yields at least as much change, with a strict improvement on one of those measures. If no edit qualifies or the comparison is incomplete, show the reason and the status instead of claiming a maximum.

### Worked result using an existing prompt

| Field | Example final output |
|---|---|
| Prompt and category | `LOGIC-010` · Logical reasoning |
| Original prompt | Determine the truth value of (P implies Q) when P is False and Q is False. |
| Perturbed prompt | Determine the truth value of (P implies Q) when P is False and Q is False |
| Operator and rationale | `punctuation`. Remove the final period while preserving the logical expression, both truth values, and the question. |
| Input change | **1 character**, normalized distance **0.0135**, within budget **0.10** |
| Model and comparison | GPT-OSS-120B, one evaluated model–prompt pair from `main_v1` |
| Original response | Explained why a false antecedent makes the implication true, then gave `Final answer: True`. |
| Perturbed response | `Final answer: True` |
| Output change | Semantic distance **0.7999**, mean unchanged control distance **0.0000**, excess distance **+0.7999** |
| Functional result | Correct → correct. The edit changed the amount of explanation. |
| Evidence status | Largest observed raw and excess distance among the **245 eligible logic results** searched at this budget. In the separate five-model ranking for `LOGIC-010`, punctuation also led with a mean excess of **0.2891**. |

Store the full response texts and the compared alternatives in the machine-readable result so readers can trace the summary. [Paired outputs](../../results/study/main_v1/processed/analysis_pairs.csv)

## Appendix. Reproduce the exploratory ranking

Run this standard-library Python snippet from the repository root. Change `budget` to reproduce the sensitivity comparisons. It prints the full category scores, top-pair gap interval, both single-case maxima with all ties, and the operator or tied operators leading for each complete prompt.

```python
import csv
import json
import random
from collections import defaultdict
from math import isfinite
from pathlib import Path
from statistics import mean

study = Path("results/study/main_v1")
manifest = json.loads((study / "study_manifest.json").read_text(encoding="utf-8"))
config = manifest["config"]
models = [item["name"] for item in config["models"]]
operators = [op for op in config["operators"] if op != "random_edit"]
budget = 0.10
candidates = {}
for line in (study / "candidates.jsonl").read_text(encoding="utf-8").splitlines():
    candidate = json.loads(line)
    candidates[candidate["prompt_id"], candidate["operator"]] = candidate

with (study / "processed/analysis_pairs.csv").open(encoding="utf-8", newline="") as file:
    pairs = list(csv.DictReader(file))
flagged = {(r["prompt_id"], r["operator"]) for r in pairs if r["audit_meaning_altering"] == "True"}
controls = defaultdict(dict)
treatments = {}
for row in pairs:
    if row["any_empty"] == "True" or row["any_truncated"] == "True":
        continue
    if not row["d_out_sem"] or not isfinite(float(row["d_out_sem"])):
        continue
    prompt, model, operator = row["prompt_id"], row["model"], row["operator"]
    if row["condition"] == "control":
        controls[prompt, model][int(row["repetition"])] = float(row["d_out_sem"])
    else:
        treatments[prompt, model, operator] = row

by_category = defaultdict(list)
for prompt in manifest["selected_prompt_ids"]:
    category = candidates[prompt, operators[0]]["task_category"]
    by_category[category].append(prompt)

for category, prompts in sorted(by_category.items()):
    eligible = defaultdict(list)
    for prompt in prompts:
        for operator in operators:
            candidate = candidates[prompt, operator]
            if candidate["status"] == "accepted" and (prompt, operator) not in flagged:
                distance = candidate["input_distances"]["char_levenshtein_normalized"]
                if 0 < distance <= budget:
                    eligible[prompt].append(operator)

    complete = [prompt for prompt in prompts if all(
        len(controls[prompt, model]) == config["control_repetitions"]
        and all((prompt, model, op) in treatments for op in eligible[prompt])
        for model in models
    )]
    print(category, "complete", len(complete), "excluded", sorted(set(prompts) - set(complete)))
    if not complete:
        continue

    scores = {op: {prompt: 0.0 for prompt in complete} for op in operators}
    observations = []
    for prompt in complete:
        for operator in eligible[prompt]:
            excess = []
            for model in models:
                row = treatments[prompt, model, operator]
                raw = float(row["d_out_sem"])
                effect = raw - mean(controls[prompt, model].values())
                excess.append(effect)
                observations.append((raw, effect, row["pair_id"]))
            scores[operator][prompt] = mean(excess)

    ranking = sorted(operators, key=lambda op: (-mean(scores[op].values()), op))
    for op in ranking:
        supported = [scores[op][prompt] for prompt in complete if op in eligible[prompt]]
        conditional_mean = mean(supported) if supported else None
        print(op, f"{mean(scores[op].values()):.4f}", len(supported), conditional_mean)
    first, second = ranking[:2]
    gaps = [scores[first][p] - scores[second][p] for p in complete]
    rng = random.Random(20261124)
    draws = sorted(mean(rng.choices(gaps, k=len(gaps))) for _ in range(10_000))
    print("gap and interval", mean(gaps), draws[249], draws[9749])
    shared = [p for p in complete if first in eligible[p] and second in eligible[p]]
    if shared:
        print("shared eligible gap", len(shared), mean(scores[first][p] - scores[second][p] for p in shared))

    if observations:
        for index, label in enumerate(("maximum raw", "maximum excess")):
            largest = max(case[index] for case in observations)
            print(label, "of", len(observations), [case for case in observations if case[index] == largest])
    for prompt in complete:
        highest = max((scores[op][prompt] for op in eligible[prompt]), default=None)
        leaders = [op for op in eligible[prompt] if scores[op][prompt] == highest]
        print(prompt, highest, leaders)
```
