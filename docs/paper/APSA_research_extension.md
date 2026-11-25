# APSA research protocol for judging perturbation effects

## 1. Audit of the recorded study

The `main_v1` manifest and candidate ledger enumerate 50 prompts, five models, ten operators, and 500 candidate attempts. The ledger contains 425 accepted and 75 rejected candidates. The raw artifacts contain 2,870 successful generations. The scored data contain 2,120 treatment pairs and 500 unchanged control pairs. Text changed in 1,393 of 2,120 treatments (65.7%) and 36 of 500 controls (7.2%). The functional scores record 92 treatment flips and zero control flips. The taxonomy calls 91 pairs flips because truncation takes precedence in that taxonomy. [Study artifacts](../../results/study/main_v1/) · [Original analysis plan](../roadmap/analysis_plan.md)

**Discrepancy to resolve in the paper.** Section 3.6 reports 14 flagged candidates and 50 treatment pairs. The scored data contain 15 distinct flagged candidates across 74 treatment pairs, consistent with Table 2 and Section 4.5. The `audit_valid` label means unflagged under a partial retrospective review. It covers 360 candidates and 1,796 pairs and does not establish independent preservation for each candidate. Pair-weighted semantic means (0.0626 treatment and 0.0027 control) and the paper's model–prompt-weighted means (about 0.061 and 0.003) have different denominators. [Existing paper](APSA_research_paper.md) · [Audit configuration](../../config/experiments/main_study_semantic_audit.yaml)

The category rankings use the same discovery prompts. They nominate operators for fresh prompts. The `LOGIC-010` worked example is a measured prompt-level case. New input preservation labels, the accuracy of either judge, and the advantage of category-specific selection on fresh prompts are pending. [Implementation plan](../roadmap/category_operator_implementation_plan.md) · [Stage-by-stage guide](../roadmap/category_operator_stage_by_stage.md)

## 2. Research questions and testable hypotheses

| Question | Outcome and design | Evidence that would weaken the hypothesis |
|---|---|---|
| RQ1. Which small edits preserve the task? | Estimate preservation by operator and annotated edit location within the 0.10 normalized character budget. Compare protected spans with surrounding prose. Record inapplicability, audit abstentions, and coverage separately. | The preservation gap disappears after matching category, operator, and edit size. |
| RQ2. What changes after meaning-preserving edits? | Compare treatment and unchanged controls within model and prompt. Measure surface, explanation, answer, apparent behavior, and tested correctness separately. | Equivalent shifts occur just as often in the paired unchanged controls. |
| RQ3. Which measurements agree with human judgments? | Compare blinded model judgments and distances with independently adjudicated human labels on identical held-out cases. Compare failures at small and large distances. | The judge adds little discrimination or agreement on the common human-labeled sample. |
| RQ4. Does category-specific selection outperform a global policy? | Lock the category and global choices on discovery data. Evaluate both on the same fresh prompts and fixed model panel, under the same budget and eligibility rule. Use unchanged fallback for inapplicable, over-budget, or rejected candidates. | The prespecified paired lower confidence bound is at or below zero or the declared practical margin. |

The primary input constraint is `0 < normalized character Levenshtein distance ≤ 0.10`. The primary output measure remains matched MiniLM excess distance. The prespecified judge outcome is a substantive answer, task-relevant claim, or apparent behavior change. The original answer keys and task tests supply functional outcomes. Compare the nine primary operators and show `random_edit` as a separate benchmark. [Prompt-format sensitivity](https://arxiv.org/abs/2310.11324) · [CheckList invariance tests](https://aclanthology.org/2020.acl-main.442/)

## 3. Why test these edits

| Category | Protected requirements | Example hypothesis and observable test |
|---|---|---|
| Classification | Label set, label definitions, and source text | Changing the classification verb can change label choice. Compare audited verb substitutions with unchanged repeats and count normalized label flips. An explanation-only shift weakens the label hypothesis. |
| Code generation | Signature, constraints, and examples | Inserting a filler cue can change the implementation. Compare structural changes and available tests. Equal test outcomes support an implementation change only. |
| Logical reasoning | Premises, negation, quantifiers, and requested conclusion | Removing terminal punctuation can change whether a derivation appears. Count derivation changes while tracking conclusion identity separately. Compare same-size edits in matched locations. |
| Mathematical reasoning | Quantities, units, operations, and unknowns | A typo in surrounding prose can change the derivation while leaving the task unchanged. Compare derivations, normalized answers and units. Check nearby arithmetic symbols separately in a deliberately labeled diagnostic stratum. |
| Question answering | Entities, quotations, dates, and requested facts | Removing a terminal delimiter can change answer framing. Check explanation and entity agreement separately. A factual change beyond unchanged repetitions is stronger evidence of answer sensitivity. |

The candidate export includes both texts, character offsets and changed spans, seed, protected requirements, and the testable hypothesis. Character offsets describe the diff. The edit-distance algorithm supplies its own minimum cost. A causal effect of location requires new randomized matched edits with the same operator, comparable size, equivalent task, and only location varied. Observations on the discovered edits motivate that experiment.

## 4. Blinding, calibration, and validation

Use two separate rubrics. Input reviewers see the task and prompt pair only. Output reviewers see the original task and anonymously ordered responses A and B, using the same rubric for controls and treatments. They score wording, explanation, final answer or claim, code implementation, and apparent behavior separately. A change that only expands an explanation can be `equivalent` on the task outcome. Apparent code behavior requires independent tests before making a functional claim. Save verbatim excerpts and a short rationale. Treat uncertain judgments and unusable pairs as missing for binary analysis and publish their counts. Counterbalance a prespecified subset by swapping response order, and use a second judge on the same frozen items if resources permit. [LLM judge bias and limitations](https://arxiv.org/abs/2306.05685) · [Structured LLM evaluation](https://aclanthology.org/2023.emnlp-main.153/)

Shuffle prompt groups within each category using a recorded seed. Put related templates in the same group and keep them in one split. Supply `--groups` with reviewed prompt-to-template assignments before drawing a confirmatory sample. The default retrospective split assigns two prompt groups per category to calibration and four to evaluation, using the full panel and all usable comparisons from those groups. Inspect the emitted coverage before collecting annotations. A separately identified diagnostic set can summarize uncommon cases such as correctness flips or distance/answer disagreements outside that sample. Use it for diagnostic examples and keep it out of sampled rate estimates. Select and freeze sample size and scope before annotation, with cost and expected coverage in mind.

Two human reviewers independently fill their blinded CSVs. Record pre-adjudication agreement and Cohen's kappa. Use their consensus or an explicit adjudication for disagreements. Calibrate binary mathematical thresholds only on calibration human labels. Evaluate each threshold and judge against human labels on the evaluation split, showing confusion matrices, per-class precision and recall, sample size and abstention. Also report performance on the common scorable subset. Resample prompt/template groups for uncertainty. Use the stored functional labels when interpreting examples and keep classifier, judge, and human measures in separate columns.

For a judge that is independent of the generation panel, choose an endpoint outside that panel and preserve its version or record `provider-unreported` if unavailable. Freeze the rubric, sample, and cutoff procedure before sending requests. Record any omissions caused by the request limit. Judge scores and human annotations of the discovery study remain retrospective.

### Reproduce the diagnostic offline

Run these commands from the repository root in PowerShell. Pick fresh output folders for a new run.

```powershell
$py = '.\.venv\Scripts\python.exe'
& $py experiments/research_judging.py prepare --out results/research-demo/logic --prompt-id LOGIC-010
& $py experiments/research_judging.py judge --package results/research-demo/logic --out results/research-demo/mock --mode mock
& $py experiments/research_judging.py assess --package results/research-demo/logic --out results/research-demo/assessment --judge-run results/research-demo/mock --prompt-id LOGIC-010 --model gpt-oss-120b
```

Omit `--prompt-id` during preparation for the stratified calibration and evaluation sample. Add `--models-per-prompt 1` for a smaller pilot that keeps both control repeats in each sampled block. Give each reviewer `blinded_items.jsonl`, `rubrics.md`, and their own CSV. Keep `private_key.json` and the other review files with the coordinator. Fill `adjudicator.csv` after both reviews for cases with disagreements. The assessed `preservation_verdicts.csv` can be passed to the existing study runner and ranking CLI once reviewed for the intended study. Use `comparison_table.csv` for case-level evidence, `method_comparison.csv` for held-out agreement, and `summary.json` for matched effects and coverage.

For real grading, use `judge --mode live` with `--package`, `--out`, `--provider`, `--model`, `--version`, and `--max-requests`. Optional `--kind` and `--split` restrict the work. Provide `--price-per-million INPUT_USD OUTPUT_USD` to record an estimate for requests with token counts. Real grading sends the blinded texts to the named provider. Pass repeated `--judge-run` paths to `assess` to compare two frozen judge runs. Mock results appear in run diagnostics and are excluded from agreement and effect estimates.

For RQ4, use `lock-policy --groups <discovery-groups.csv> --out <lock.json> --margin 0` before collecting validation outcomes. The global policy maximizes the average discovery score across categories. Set a positive margin if the study requires a practically meaningful difference. Then run `evaluate-policy --study-dir <held-out-dir> --groups <holdout-groups.csv> --verdicts <holdout-verdicts.csv> --lock <lock.json> --out <paired-result.json>`. Assign stable, shared template group names across both datasets so the overlap check can detect related items. The primary contrast is the average holdout prompt-level gap between the category policy and global policy. Report prompt-level and category results and the group-bootstrap 95% interval. Claim an advantage only if the overall interval’s lower bound exceeds the locked margin and every category contributes usable prompts.

## 5. Paper draft

### Methods

We compare accepted prompt edits with two unchanged repetitions on the same original prompt and model. We subtract the mean semantic distance of the two repeats from the treatment distance. The input-preservation rubric evaluates task equivalence before considering model responses. The response rubric analyzes blinded pairs and predicts changes in individual response dimensions. We compare both automatic methods against independent human review and retain answer-key and code-test outcomes as separate measures. For substantive change, the paired rate difference is the average treatment indicator minus the average unchanged-repeat indicator in the same model–prompt unit. The comparison requires both controls and at least one scorable, human-preserved primary treatment. Prompt groups are the resampling unit.

### Results available now

The existing case `LOGIC-010` changed one final period, yielding normalized input distance `1/74 = 0.0135`. For GPT-OSS-120B, raw output distance `0.7999` minus mean unchanged-repeat distance `0.0000` gave excess `0.7999`. Both answers were correct and the visible explanation was removed. The five-model excess was `0.2891`, compared with `0.1798` for character substitution on the same prompt. Judge and human evaluations of this example, aggregate judge agreement, and held-out category policy advantages are pending. [Recorded ranking and case details](../roadmap/category_operator_implementation_plan.md)

### Limitations

The discovery dataset is small and already analyzed. Some audit labels reflect a partial retrospective screen. Embedding distance can react to response length and formatting. Judges may exhibit order, verbosity, or model preference effects. A grader can disagree with humans and may be unable to infer code behavior. The held-out policy comparison requires independent prompts, a locked discovery policy, and explicit uncertainty. The short sample defaults support a feasibility run. Choose a larger sample using the planned effect and available resources before drawing general claims.
