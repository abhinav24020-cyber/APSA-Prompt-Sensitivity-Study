# Perturbation Methodology

**Project:** Adversarial Prompt Sensitivity Analysis (APSA)
**Phase:** 4 — Minimal Prompt Perturbation Engine
**Version:** 1.1
**Date:** November 2026

---

## 1. Overview

The APSA Perturbation Engine generates controlled candidate modifications to baseline prompts. It supports experiments on output sensitivity, but candidate generation alone neither establishes semantic preservation nor identifies a maximum-output-change perturbation.

Every perturbation is described along three distinct dimensions. These fields are measurements or heuristics, not certificates that a perturbation preserves meaning:

| Dimension | Definition | Assessed By |
|---|---|---|
| **Syntactic Minimality** | Conservative operator-level label; it is not a parse-tree comparison. | `is_syntactically_minimal` in the record |
| **Lexical Minimality** | The normalised word-level edit distance ≤ 0.15. | `is_lexically_minimal()` in `distance_utils.py` |
| **Semantic Risk** | Rule-based risk flags; `MINIMAL` means only case/whitespace-only, not proven equivalence. | `SemanticFlagDetector.assess_with_reasons()` |

---

## 2. Perturbation Taxonomy

The engine implements **10 perturbation operators**, grouped into 4 subdirectories:

### 2.1 Surface Perturbations (`surface/`)

These modify surface form. Character substitutions can change a word, and punctuation can change intent or parsing; neither is assumed syntactically or semantically minimal.

| Operator | Canonical Name | Description |
|---|---|---|
| `CharSubstitutionPerturbation` | `char_substitution` | Replaces one character in an unprotected word with a visually similar alternative (e.g., `o→0`, `a→@`). This can change tokenization or meaning. |
| `CapitalizationPerturbation` | `capitalization` | Alters casing of the prompt via one of 5 modes: `lowercase_first_word`, `uppercase_first_word`, `title_case`, `all_uppercase`, `all_lowercase`. |
| `PunctuationPerturbation` | `punctuation` | Adds or removes punctuation marks. Such changes are at least `MODERATE` risk because they can affect intent or parsing. |
| `WhitespacePerturbation` | `whitespace` | Injects or removes whitespace: `double_space`, `trailing_space`, `leading_space`, `tab_indent`, `add_newline`, `compress_spaces`. |

### 2.2 Lexical Perturbations (`lexical/`)

These modify the token sequence of the prompt. Insertion and deletion target one token; substitutions and synonym replacements use one table entry. Distances are still recorded because token counts or character edits can vary by operator.

| Operator | Canonical Name | Description |
|---|---|---|
| `AdditionPerturbation` | `word_insertion` | Inserts one configured/default word at a seed-determined position (`start`, `after_first`, or `end`) without silently changing another word's case. A filler is not assumed semantically inert. |
| `DeletionPerturbation` | `word_deletion` | Removes the first matching configured/default article or filler (`the`, `a`, `an`, `please`, etc.). Returns `None` if no candidate is present; deletions are not assumed meaning-preserving. |
| `SubstitutionPerturbation` | `word_substitution` | Replaces one content word with an entry from a **static substitution table**. Includes both neutral swaps (`calculate→compute`) and polarity-flip entries (`correct→incorrect`). Polarity flips are automatically flagged `HIGH` risk. |
| `SynonymPerturbation` | `synonym_replacement` | Replaces one word with a candidate from the static table. The table is not embedding-validated; semantic similarity and preservation must be measured independently. |

### 2.3 Structural Perturbations (`structural/`)

These change the ordering of multi-sentence prompt structures.

| Operator | Canonical Name | Description |
|---|---|---|
| `ReorderingPerturbation` | `instruction_reordering` | For prompts with ≥ 2 sentences: swaps the position of the first and last sentence. Modes: `last_to_first` (default), `first_to_last`. Returns `None` for single-sentence prompts. |

### 2.4 Syntactic/Formatting Perturbations (`syntactic/`)

These apply presentational and formatting changes without modifying word content.

| Operator | Canonical Name | Description |
|---|---|---|
| `RephrasingPerturbation` | `formatting_modification` | Applies surface formatting transforms: `add_please_prefix`, `remove_please_prefix`, `numbered_to_prose` (e.g., `1. → First,`), `prose_to_numbered` (e.g., `First, → 1.`). |

---

## 3. PerturbationRecord Schema

Every successful perturbation produces a `PerturbationRecord` dataclass with these fields:

| Field | Type | Description |
|---|---|---|
| `perturbation_id` | `str` | Stable key containing prompt ID, operator, seed, and a hash of parameters and generated variant. |
| `original_prompt` | `str` | Unmodified baseline prompt |
| `perturbed_prompt` | `str` | Generated candidate prompt |
| `perturbation_type` | `str` | Canonical operator name (e.g., `"capitalization"`) |
| `changed_tokens` | `list[str]` | Word tokens added or removed (multiset diff) |
| `num_changed_characters` | `int` | Character-level Levenshtein distance |
| `num_changed_words` | `int` | Token-level Levenshtein distance (punctuation is tokenized separately) |
| `edit_distance` | `int` | Raw character edit distance (same as `num_changed_characters`) |
| `char_edit_distance_normalized` | `float` | Character distance divided by the longer prompt length |
| `word_edit_distance_normalized` | `float` | Word distance divided by the longer token count |
| `semantic_risk_level` | `SemanticRiskLevel` | `MINIMAL` / `MODERATE` / `HIGH` |
| `semantic_risk_reasons` | `list[str]` | Rule-based rationale(s), not a semantic judgment |
| `is_syntactically_minimal` | `bool` | `True` only for capitalization and whitespace operators |
| `is_lexically_minimal` | `bool` | `True` if normalised word edit distance ≤ 0.15 |
| `is_semantically_minimal` | `bool` | `True` only for case/whitespace-only changes; not proof of equivalence |
| `metadata` | `dict` | Seed, mode, and operator-specific parameters |

---

## 4. Semantic Risk Flagging

### 4.1 Motivation

> **Example:** Changing `"correct"` → `"incorrect"` is a one-word edit with word edit distance = 1 (lexically minimal). However, this single edit flips the entire truth value of the assertion. A naive minimality check would incorrectly classify this as a semantically safe perturbation.

The detector applies rule-based heuristics before any LLM call. It can flag known high-risk patterns but cannot establish semantic equivalence or replace task-specific validation, human review, or measured embedding distance.

### 4.2 Risk Levels

| Level | Criteria | Example |
|---|---|---|
| `MINIMAL` | Only case and/or whitespace changed | `"Calculate the sum."` → `"calculate the sum."` |
| `MODERATE` | A lexical or non-lexical text change occurred and no known high-risk rule fired; preservation is unverified. | `"Calculate the sum."` → `"Compute the sum."` |
| `HIGH` | Negation, known polarity, critical quantifier, or numeric value changed | `"Find all values."` → `"Find some values."` |

### 4.3 Detection Rules (in priority order)

1. **Negation Detection**: If any token in `{not, no, never, none, nor, without, cannot, ...}` appears in the symmetric multiset diff → `HIGH`.
2. **Polarity Flip Detection**: If a polarity-flip pair is present (e.g., one of `{correct/incorrect, true/false, always/never, ...}`) → `HIGH`.
3. **Quantifier Detection**: Changes to `{all, every, each, any, some, none, neither, either, both, only, exactly}` → `HIGH`.
4. **Numeric Change Detection**: Changes to signed, decimal, grouped, exponent, or percentage values → `HIGH`.
5. **Whitespace/Case Only**: If removing whitespace and case-folding makes the strings equal → `MINIMAL`.
6. **Default**: → `MODERATE`, with an explicit reason that semantic preservation is unverified.

> [!NOTE]
> The detector uses **Counter-based multiset difference** (not set difference) to correctly handle repeated tokens. For example, deleting one instance of `"the"` from `"Find the answer to the problem."` still leaves `"the"` in the perturbed string — a set diff would miss this. The multiset approach correctly identifies `"the"` as the changed token.

### 4.4 Separation of Concerns (Future Upgrade Path)

The semantic flagging module (`semantic_flags.py`) is cleanly isolated from all perturbation operators. To upgrade from rule-based detection to embedding-based detection in a future phase:

1. Subclass `SemanticFlagDetector` and override `assess()`.
2. Inject a `sentence-transformers` model into the subclass constructor.
3. Compute `1 - cosine(embed(original), embed(perturbed))` as the semantic distance.
4. Apply the `EpsilonBudget.semantic_cosine` threshold (default: 0.05) to determine risk level.

No changes to any operator files are required.

---

## 5. Static Synonym Table Design (`synonym.py`)

The synonym table is a small, manually curated set of candidate replacements focused on task vocabulary. It is not automatically checked for polarity, part of speech, contextual fit, or embedding similarity. Do not treat the table name as evidence that any replacement is a synonym in context.

The table is marked with a `# STATIC_SYNONYM_TABLE` comment. No measured cosine-similarity threshold, part-of-speech validation, or contextual equivalence check is performed by the implementation.

---

## 6. Determinism and Reproducibility

All 10 operators are fully deterministic given a fixed `seed` integer:

- `CharSubstitutionPerturbation`, `AdditionPerturbation`, `SubstitutionPerturbation`, and `SynonymPerturbation` use `random.Random(seed)` for local RNG that does not share state with the global `random` module.
- All other operators are mode-deterministic (no randomness required).

Repeated runs with the same prompt, operator configuration, and seed are deterministic in the current implementation. Cross-version/platform bitwise reproducibility is not guaranteed; record the Python version and configuration.

---

## 7. Distance Metrics

The perturbation record computes raw and normalized character and word-level edit distances. Semantic embedding distance is separate and is not computed by the perturbation engine:

| Metric | Formula | Module |
|---|---|---|
| Character Levenshtein distance | Wagner-Fischer DP, O(m·n) time, O(min(m,n)) space | `distance_utils.char_edit_distance()` |
| Word Levenshtein distance | Same DP over word token lists | `distance_utils.word_edit_distance()` |
| Normalised word edit distance | `WED / max(|w(X)|, |w(X')|)` | `distance_utils.is_lexically_minimal()` |

All computations use **Python stdlib only** (`re`, `collections.Counter`) — no `python-Levenshtein` or NLTK dependency in Phase 4.

---

## 8. Known Limitations

1. **Static synonym table coverage and quality**: The table is small and not contextually validated. Its entries are candidate substitutions, not confirmed semantic equivalents.

2. **No syntactic tree analysis**: Syntactic minimality is assessed by operator class membership (surface/non-surface), not by actual parse-tree edit distance. A later phase will integrate spaCy dependency parsing.

3. **Rule-based semantic detection is approximate**: The heuristics do not handle complex cases such as double negatives (`"not incorrect"`), rhetorical questions, scope, or domain-specific meanings. A `MINIMAL` flag is not an equivalence certificate.

4. **English-only**: All operators assume English text. Multilingual perturbations are out of scope for Phase 4.

5. **Edit scope varies by operator**: Lexical insertion/deletion/substitution operators target one token (punctuation is a token for the distance calculation), while case, formatting, and sentence-reordering operators may change many characters or tokens. Inspect recorded distances instead of assuming a fixed budget.

6. **`instruction_reordering` requires multi-sentence prompts**: Single-sentence prompts return `None` from this operator. Approximately 15–20% of the baseline prompts are single-sentence and will not have a reordering perturbation generated.
7. **Candidate generation is not adversarial optimization**: `apply_all()` enumerates configured operators; it does not search for or guarantee a maximum-output-change variant. Enforce declared input budgets and use a reproducible search/evaluation protocol.

8. **Rejected or failed trials are not successful perturbations**: Inapplicable operators and over-budget candidates must not be replaced with the original prompt or sent to the model. The experiment runner records failed trials separately in `failures.jsonl`; only completed prompt pairs belong in `results.jsonl`.
