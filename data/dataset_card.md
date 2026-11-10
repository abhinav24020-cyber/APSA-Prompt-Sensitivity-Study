# APSA Baseline Prompt Dataset Card

## Purpose and status

`baseline_prompts.csv` is the APSA baseline prompt collection for studying
response changes under controlled prompt edits. It is an experimental
convenience dataset, not a published or independently validated benchmark.
Small surface changes are not assumed to preserve meaning; perturbation
provenance and semantic-risk measurements must be considered when interpreting
results.

## Observed structure

The structural audit (`python experiments/validate_baseline_dataset.py`) found
100 rows, unique prompt IDs and prompt texts, no blank required fields, valid
JSON-object metadata in every row, and a non-empty expected answer in every row.
The machine-readable result is in [baseline_dataset_audit.json](./baseline_dataset_audit.json).
The category distribution is balanced:

| Category | Rows |
|---|---:|
| `mathematical_reasoning` | 20 |
| `logical_reasoning` | 20 |
| `question_answering` | 20 |
| `classification` | 20 |
| `code_generation` | 20 |

The observed overall difficulty distribution is 59 easy, 34 medium, and 7 hard.
This is a structural description, not evidence that difficulty labels are
calibrated or balanced within categories.

## Fields

The CSV contains `prompt_id`, `task_category`, `task_description`,
`original_prompt`, `expected_answer`, `difficulty_level`, and `metadata`.
Metadata is expected to be a JSON object; the audit verifies parseability, not
the semantic accuracy of its values.

## Sampling and exclusions

The lightweight pilot takes the first N rows in CSV order for each of the first
five eligible task categories; `--prompts-per-category` sets N (default 10).
There is no randomization or stratification within categories. The default
pilot therefore selects up to 50 prompts, 10 per category. A prompt/operator
candidate that cannot be applied is skipped by the experiment runner and
reported as inapplicable; it is not replaced with the original prompt or
counted as a completed treatment trial. No dataset rows were excluded by the
structural audit.

## Reference-answer validation and limitations

The structural audit establishes that reference-answer fields are populated;
it does **not** establish that every answer is correct. Targeted review of the
math, logic, QA, and classification references found and corrected these
issues:

- `MATH-002`: corrected the solution to `(34/13, 53/13)`.
- `MATH-010`: corrected the matrix determinant to `31`.
- `LOGIC-006`: listed both valid task orders.
- `LOGIC-008`: added a clue needed to make the pet assignment unique.
- `QA-006`: removed the inaccurate claim that RISC instructions execute in
  exactly one clock cycle.

The code-generation reference strings parse as Python, but their behavior has
not been executed against task-specific tests. No independent expert review or
complete answer-key validation is claimed. The pilot correctness module applies
conservative automated exact/containment checks to selected categories; these
checks have not been independently validated and do not evaluate code
generation. Researchers should review prompts and answer keys before treating
correctness results as ground truth, and should retain category-specific
adjudication rules in any confirmatory study.

The dataset is small, single-turn, and English-oriented. Category balance does
not imply representative coverage of each task domain. Results from it should
not be generalized to all prompts, models, languages, or perturbation types.
