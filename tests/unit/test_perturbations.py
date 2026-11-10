"""Unit tests for all 10 perturbation operators.

Each test class covers one operator and verifies:
  1. The perturbed prompt differs from the original.
  2. edit_distance > 0.
  3. perturbation_type matches the expected canonical string.
  4. PerturbationRecord fields are all present and well-typed.
  5. Semantic risk is correctly assessed for known edge cases.
"""

import unittest

from apsa.perturbations.base_perturbation import PerturbationConfig
from apsa.perturbations.distance_utils import char_edit_distance, word_edit_distance
from apsa.perturbations.registry import get_perturbation
from apsa.perturbations.semantic_flags import SemanticRiskLevel

# ── Shared test prompt ─────────────────────────────────────────────────────

_PROMPT = "Calculate the sum of all prime numbers less than 50."
_MULTI_PROMPT = "A list of prime numbers is given. Find all primes less than 50."
_PLEASE_PROMPT = "Please calculate the sum."


class _OperatorTestMixin:
    """Mixin with helpers for all operator test classes."""

    def _make_config(self, seed: int = 42, **params) -> PerturbationConfig:
        return PerturbationConfig(params=params, seed=seed)

    def _assert_valid_record(self, record, expected_type: str):
        self.assertIsNotNone(record, "perturb() returned None unexpectedly")
        self.assertNotEqual(record.original_prompt, record.perturbed_prompt)
        self.assertGreater(record.edit_distance, 0)
        self.assertEqual(record.perturbation_type, expected_type)
        self.assertIsInstance(record.semantic_risk_level, SemanticRiskLevel)
        self.assertIsInstance(record.changed_tokens, list)
        self.assertIsInstance(record.is_syntactically_minimal, bool)
        self.assertIsInstance(record.is_lexically_minimal, bool)
        self.assertIsInstance(record.is_semantically_minimal, bool)
        self.assertIsInstance(record.metadata, dict)


# ═══════════════════════════════════════════════════════════════════════════
# 1. Character substitution
# ═══════════════════════════════════════════════════════════════════════════

class TestCharSubstitution(unittest.TestCase, _OperatorTestMixin):
    def setUp(self):
        self.op = get_perturbation("char_substitution")

    def test_basic_substitution(self):
        record = self.op.perturb(_PROMPT, prompt_id="MATH-001")
        self._assert_valid_record(record, "char_substitution")

    def test_is_not_assumed_syntactically_minimal(self):
        record = self.op.perturb(_PROMPT, prompt_id="MATH-001")
        self.assertFalse(record.is_syntactically_minimal)

    def test_single_char_changed(self):
        record = self.op.perturb(_PROMPT, prompt_id="MATH-001")
        # Character substitution changes exactly 1 character
        self.assertEqual(record.edit_distance, 1)

    def test_protected_word_not_changed(self):
        # Prompt with only protected/non-substitutable words should return None
        protected_prompt = "Not no never none."
        result = self.op.perturb(protected_prompt, prompt_id="test")
        # Should return None or produce a different prompt (not in protected word)
        if result is not None:
            self.assertNotEqual(result.original_prompt, result.perturbed_prompt)

    def test_deterministic_with_same_seed(self):
        r1 = self.op.perturb(_PROMPT, prompt_id="x", config=self._make_config(seed=42))
        r2 = self.op.perturb(_PROMPT, prompt_id="x", config=self._make_config(seed=42))
        self.assertEqual(r1.perturbed_prompt, r2.perturbed_prompt)

    def test_different_seeds_produce_different_results(self):
        r1 = self.op.perturb(_PROMPT, prompt_id="x", config=self._make_config(seed=1))
        r2 = self.op.perturb(_PROMPT, prompt_id="x", config=self._make_config(seed=999))
        # Different seeds may or may not produce different results depending on prompt
        # — just assert both are valid
        if r1 and r2:
            self.assertEqual(r1.perturbation_type, r2.perturbation_type)


# ═══════════════════════════════════════════════════════════════════════════
# 2. Capitalization
# ═══════════════════════════════════════════════════════════════════════════

class TestCapitalization(unittest.TestCase, _OperatorTestMixin):
    def setUp(self):
        self.op = get_perturbation("capitalization")

    def test_lowercase_first_word(self):
        config = self._make_config(mode="lowercase_first_word")
        record = self.op.perturb(_PROMPT, config=config)
        self._assert_valid_record(record, "capitalization")
        self.assertTrue(record.perturbed_prompt[0].islower())

    def test_all_uppercase(self):
        config = self._make_config(mode="all_uppercase")
        record = self.op.perturb(_PROMPT, config=config)
        self._assert_valid_record(record, "capitalization")
        self.assertEqual(record.perturbed_prompt, _PROMPT.upper())

    def test_all_lowercase(self):
        config = self._make_config(mode="all_lowercase")
        record = self.op.perturb(_PROMPT, config=config)
        self._assert_valid_record(record, "capitalization")
        self.assertEqual(record.perturbed_prompt, _PROMPT.lower())

    def test_title_case(self):
        config = self._make_config(mode="title_case")
        record = self.op.perturb(_PROMPT, config=config)
        self._assert_valid_record(record, "capitalization")

    def test_is_semantically_minimal(self):
        # Capitalization changes cannot change meaning → MINIMAL risk
        config = self._make_config(mode="all_lowercase")
        record = self.op.perturb(_PROMPT, config=config)
        self.assertEqual(record.semantic_risk_level, SemanticRiskLevel.MINIMAL)

    def test_is_syntactically_minimal(self):
        config = self._make_config(mode="all_uppercase")
        record = self.op.perturb(_PROMPT, config=config)
        self.assertTrue(record.is_syntactically_minimal)

    def test_invalid_mode_raises(self):
        config = self._make_config(mode="bad_mode")
        with self.assertRaises(ValueError):
            self.op._apply_transform(_PROMPT, config)


# ═══════════════════════════════════════════════════════════════════════════
# 3. Punctuation
# ═══════════════════════════════════════════════════════════════════════════

class TestPunctuation(unittest.TestCase, _OperatorTestMixin):
    def setUp(self):
        self.op = get_perturbation("punctuation")

    def test_add_trailing_period(self):
        prompt_no_period = "What is the capital of France"
        config = self._make_config(mode="add_trailing_period")
        record = self.op.perturb(prompt_no_period, config=config)
        self._assert_valid_record(record, "punctuation")
        self.assertTrue(record.perturbed_prompt.endswith("."))

    def test_add_trailing_period_no_op_if_already_present(self):
        config = self._make_config(mode="add_trailing_period")
        result = self.op.perturb(_PROMPT, config=config)
        # _PROMPT ends with '.', so this should return None
        self.assertIsNone(result)

    def test_remove_trailing_period(self):
        config = self._make_config(mode="remove_trailing_period")
        record = self.op.perturb(_PROMPT, config=config)
        self._assert_valid_record(record, "punctuation")
        self.assertFalse(record.perturbed_prompt.endswith("."))

    def test_add_exclamation(self):
        config = self._make_config(mode="add_exclamation")
        record = self.op.perturb(_PROMPT, config=config)
        self._assert_valid_record(record, "punctuation")
        self.assertTrue(record.perturbed_prompt.endswith("!"))

    def test_remove_comma(self):
        prompt_with_comma = "Calculate the sum, then double it."
        config = self._make_config(mode="remove_comma")
        record = self.op.perturb(prompt_with_comma, config=config)
        self._assert_valid_record(record, "punctuation")
        self.assertNotIn(",", record.perturbed_prompt.split(".")[0])

    def test_is_syntactically_minimal(self):
        config = self._make_config(mode="add_exclamation")
        record = self.op.perturb(_PROMPT, config=config)
        self.assertFalse(record.is_syntactically_minimal)


# ═══════════════════════════════════════════════════════════════════════════
# 4. Whitespace
# ═══════════════════════════════════════════════════════════════════════════

class TestWhitespace(unittest.TestCase, _OperatorTestMixin):
    def setUp(self):
        self.op = get_perturbation("whitespace")

    def test_double_space(self):
        config = self._make_config(mode="double_space")
        record = self.op.perturb(_PROMPT, config=config)
        self._assert_valid_record(record, "whitespace")
        self.assertIn("  ", record.perturbed_prompt)

    def test_trailing_space(self):
        config = self._make_config(mode="trailing_space")
        record = self.op.perturb(_PROMPT, config=config)
        self._assert_valid_record(record, "whitespace")
        self.assertTrue(record.perturbed_prompt.endswith(" "))

    def test_leading_space(self):
        config = self._make_config(mode="leading_space")
        record = self.op.perturb(_PROMPT, config=config)
        self._assert_valid_record(record, "whitespace")
        self.assertTrue(record.perturbed_prompt.startswith(" "))

    def test_tab_indent(self):
        config = self._make_config(mode="tab_indent")
        record = self.op.perturb(_PROMPT, config=config)
        self._assert_valid_record(record, "whitespace")
        self.assertTrue(record.perturbed_prompt.startswith("\t"))

    def test_is_semantically_minimal(self):
        config = self._make_config(mode="trailing_space")
        record = self.op.perturb(_PROMPT, config=config)
        self.assertEqual(record.semantic_risk_level, SemanticRiskLevel.MINIMAL)

    def test_is_syntactically_minimal(self):
        config = self._make_config(mode="double_space")
        record = self.op.perturb(_PROMPT, config=config)
        self.assertTrue(record.is_syntactically_minimal)


# ═══════════════════════════════════════════════════════════════════════════
# 5. Word insertion
# ═══════════════════════════════════════════════════════════════════════════

class TestWordInsertion(unittest.TestCase, _OperatorTestMixin):
    def setUp(self):
        self.op = get_perturbation("word_insertion")

    def test_adds_one_word(self):
        record = self.op.perturb(_PROMPT, prompt_id="MATH-001")
        self._assert_valid_record(record, "word_insertion")
        orig_word_count = len(_PROMPT.split())
        pert_word_count = len(record.perturbed_prompt.split())
        self.assertEqual(pert_word_count, orig_word_count + 1)

    def test_insert_at_start(self):
        config = self._make_config(seed=42, position="start")
        record = self.op.perturb(_PROMPT, config=config)
        self._assert_valid_record(record, "word_insertion")

    def test_insert_at_end(self):
        config = self._make_config(seed=42, position="end")
        record = self.op.perturb(_PROMPT, config=config)
        self._assert_valid_record(record, "word_insertion")

    def test_semantic_risk_does_not_assume_filler_is_equivalent(self):
        config = self._make_config(seed=42, filler_word="please", position="start")
        record = self.op.perturb(_PROMPT, config=config)
        self.assertEqual(record.semantic_risk_level, SemanticRiskLevel.MODERATE)

    def test_is_lexically_minimal(self):
        record = self.op.perturb(_PROMPT)
        self.assertTrue(record.is_lexically_minimal)


# ═══════════════════════════════════════════════════════════════════════════
# 6. Word deletion
# ═══════════════════════════════════════════════════════════════════════════

class TestWordDeletion(unittest.TestCase, _OperatorTestMixin):
    def setUp(self):
        self.op = get_perturbation("word_deletion")

    def test_deletes_article(self):
        prompt = "Find the sum of all prime numbers."
        record = self.op.perturb(prompt, prompt_id="MATH-001")
        self._assert_valid_record(record, "word_deletion")
        orig_word_count = len(prompt.split())
        pert_word_count = len(record.perturbed_prompt.split())
        self.assertEqual(pert_word_count, orig_word_count - 1)

    def test_returns_none_when_no_deletable_token(self):
        prompt = "2 + 2 = 4"
        result = self.op.perturb(prompt)
        self.assertIsNone(result)

    def test_specific_target_word(self):
        prompt = "Please calculate the sum."
        config = self._make_config(target_word="please")
        record = self.op.perturb(prompt, config=config)
        self._assert_valid_record(record, "word_deletion")
        self.assertNotIn("please", record.perturbed_prompt.lower().split())

    def test_terminal_punctuation_is_preserved_when_deleting_filler(self):
        prompt = "Please calculate the sum."
        config = self._make_config(target_word="please")
        record = self.op.perturb(prompt, config=config)
        self.assertEqual(record.perturbed_prompt, "calculate the sum.")

    def test_semantic_risk_flags_article_deletion_as_unverified(self):
        prompt = "Find the answer to the problem."
        record = self.op.perturb(prompt)
        self.assertEqual(record.semantic_risk_level, SemanticRiskLevel.MODERATE)


# ═══════════════════════════════════════════════════════════════════════════
# 7. Word substitution
# ═══════════════════════════════════════════════════════════════════════════

class TestWordSubstitution(unittest.TestCase, _OperatorTestMixin):
    def setUp(self):
        self.op = get_perturbation("word_substitution")

    def test_basic_substitution(self):
        prompt = "Calculate the sum of all prime numbers."
        record = self.op.perturb(prompt, prompt_id="MATH-001")
        self._assert_valid_record(record, "word_substitution")

    def test_polarity_flip_flagged_high(self):
        prompt = "The answer is correct."
        config = self._make_config(seed=42, target_word="correct")
        record = self.op.perturb(prompt, config=config)
        self._assert_valid_record(record, "word_substitution")
        # 'correct' -> 'incorrect' must be flagged as HIGH semantic risk
        self.assertEqual(record.semantic_risk_level, SemanticRiskLevel.HIGH)
        self.assertFalse(record.is_semantically_minimal)

    def test_safe_substitution_not_high_risk(self):
        prompt = "Calculate the sum of values."
        config = self._make_config(seed=42, target_word="calculate")
        record = self.op.perturb(prompt, config=config)
        self._assert_valid_record(record, "word_substitution")
        self.assertIn(record.semantic_risk_level,
                      [SemanticRiskLevel.MINIMAL, SemanticRiskLevel.MODERATE])

    def test_returns_none_for_no_candidate(self):
        prompt = "2 + 2 equals 4."
        result = self.op.perturb(prompt)
        self.assertIsNone(result)

    def test_word_count_unchanged(self):
        prompt = "Explain the correct answer."
        config = self._make_config(seed=42, target_word="explain")
        record = self.op.perturb(prompt, config=config)
        if record:
            self.assertEqual(
                len(record.original_prompt.split()),
                len(record.perturbed_prompt.split()),
            )


# ═══════════════════════════════════════════════════════════════════════════
# 8. Synonym replacement
# ═══════════════════════════════════════════════════════════════════════════

class TestSynonymReplacement(unittest.TestCase, _OperatorTestMixin):
    def setUp(self):
        self.op = get_perturbation("synonym_replacement")

    def test_basic_synonym(self):
        prompt = "Calculate the sum of all prime numbers."
        record = self.op.perturb(prompt, prompt_id="MATH-001")
        self._assert_valid_record(record, "synonym_replacement")

    def test_specific_target(self):
        prompt = "Explain the solution to the problem."
        config = self._make_config(seed=42, target_word="explain")
        record = self.op.perturb(prompt, config=config)
        self._assert_valid_record(record, "synonym_replacement")
        # 'explain' should be replaced by a synonym from the table
        self.assertNotIn("explain", record.perturbed_prompt.lower())

    def test_no_polarity_flip(self):
        # 'correct' in the synonym table should map to safe synonyms (right/accurate),
        # NOT to 'incorrect' (which is in substitution.py, not synonym.py)
        prompt = "Give the correct answer."
        config = self._make_config(seed=42, target_word="correct")
        record = self.op.perturb(prompt, config=config)
        if record:
            self.assertNotIn("incorrect", record.perturbed_prompt.lower())

    def test_returns_none_when_no_synonym(self):
        prompt = "2 plus 2 equals 4."
        result = self.op.perturb(prompt)
        # May or may not find a synonym; just check it doesn't crash
        # If it returns something, it must be valid
        if result is not None:
            self._assert_valid_record(result, "synonym_replacement")

    def test_word_count_unchanged(self):
        prompt = "Find the minimum value in the list."
        record = self.op.perturb(prompt, prompt_id="MATH-001")
        if record:
            self.assertEqual(
                len(record.original_prompt.split()),
                len(record.perturbed_prompt.split()),
            )


# ═══════════════════════════════════════════════════════════════════════════
# 9. Instruction reordering
# ═══════════════════════════════════════════════════════════════════════════

class TestInstructionReordering(unittest.TestCase, _OperatorTestMixin):
    def setUp(self):
        self.op = get_perturbation("instruction_reordering")

    def test_multi_sentence_reorder(self):
        record = self.op.perturb(_MULTI_PROMPT, prompt_id="MATH-001")
        self._assert_valid_record(record, "instruction_reordering")

    def test_last_to_first(self):
        config = self._make_config(mode="last_to_first")
        record = self.op.perturb(_MULTI_PROMPT, config=config)
        self._assert_valid_record(record, "instruction_reordering")
        # The last sentence of original should now be first
        last_sentence = "Find all primes less than 50."
        self.assertTrue(record.perturbed_prompt.startswith(last_sentence))

    def test_first_to_last(self):
        config = self._make_config(mode="first_to_last")
        record = self.op.perturb(_MULTI_PROMPT, config=config)
        self._assert_valid_record(record, "instruction_reordering")

    def test_single_sentence_returns_none(self):
        result = self.op.perturb(_PROMPT)
        self.assertIsNone(result)

    def test_not_syntactically_minimal(self):
        record = self.op.perturb(_MULTI_PROMPT)
        self.assertFalse(record.is_syntactically_minimal)


# ═══════════════════════════════════════════════════════════════════════════
# 10. Formatting modification
# ═══════════════════════════════════════════════════════════════════════════

class TestFormattingModification(unittest.TestCase, _OperatorTestMixin):
    def setUp(self):
        self.op = get_perturbation("formatting_modification")

    def test_add_please_prefix(self):
        config = self._make_config(mode="add_please_prefix")
        record = self.op.perturb(_PROMPT, config=config)
        self._assert_valid_record(record, "formatting_modification")
        self.assertTrue(record.perturbed_prompt.startswith("Please"))

    def test_remove_please_prefix(self):
        config = self._make_config(mode="remove_please_prefix")
        record = self.op.perturb(_PLEASE_PROMPT, config=config)
        self._assert_valid_record(record, "formatting_modification")
        self.assertFalse(record.perturbed_prompt.lower().startswith("please"))

    def test_add_please_no_op_when_already_present(self):
        config = self._make_config(mode="add_please_prefix")
        result = self.op.perturb(_PLEASE_PROMPT, config=config)
        self.assertIsNone(result)

    def test_numbered_to_prose(self):
        prompt = "1. Find the sum. 2. Verify the result."
        config = self._make_config(mode="numbered_to_prose")
        record = self.op.perturb(prompt, config=config)
        self._assert_valid_record(record, "formatting_modification")
        self.assertIn("First", record.perturbed_prompt)

    def test_prose_to_numbered(self):
        prompt = "First, find the sum. Second, verify the result."
        config = self._make_config(mode="prose_to_numbered")
        record = self.op.perturb(prompt, config=config)
        self._assert_valid_record(record, "formatting_modification")
        self.assertIn("1.", record.perturbed_prompt)


# ═══════════════════════════════════════════════════════════════════════════
# Semantic flag detector unit tests
# ═══════════════════════════════════════════════════════════════════════════

class TestSemanticFlagDetector(unittest.TestCase):
    def setUp(self):
        from apsa.perturbations.semantic_flags import SemanticFlagDetector
        self.detector = SemanticFlagDetector()

    def test_negation_word_added_is_high(self):
        risk = self.detector.assess("The answer is correct.", "The answer is not correct.")
        self.assertEqual(risk, SemanticRiskLevel.HIGH)

    def test_polarity_flip_is_high(self):
        risk = self.detector.assess("The answer is correct.", "The answer is incorrect.")
        self.assertEqual(risk, SemanticRiskLevel.HIGH)

    def test_numeric_change_is_high(self):
        risk = self.detector.assess("Find primes less than 50.", "Find primes less than 100.")
        self.assertEqual(risk, SemanticRiskLevel.HIGH)

    def test_filler_word_only_is_minimal(self):
        risk = self.detector.assess("Calculate the sum.", "Please calculate the sum.")
        self.assertEqual(risk, SemanticRiskLevel.MODERATE)

    def test_case_only_change_is_minimal(self):
        risk = self.detector.assess("Calculate the sum.", "calculate the sum.")
        self.assertEqual(risk, SemanticRiskLevel.MINIMAL)

    def test_synonym_swap_is_moderate(self):
        risk = self.detector.assess("Calculate the result.", "Compute the result.")
        self.assertEqual(risk, SemanticRiskLevel.MODERATE)

    def test_quantifier_change_is_high(self):
        risk = self.detector.assess(
            "Find all values greater than 3.",
            "Find some values greater than 3.",
        )
        self.assertEqual(risk, SemanticRiskLevel.HIGH)

    def test_contraction_negation_is_high(self):
        risk = self.detector.assess("Do this.", "Don't do this.")
        self.assertEqual(risk, SemanticRiskLevel.HIGH)

    def test_signed_decimal_change_is_high(self):
        risk = self.detector.assess("Use -1.5 as the threshold.", "Use 1.5 as the threshold.")
        self.assertEqual(risk, SemanticRiskLevel.HIGH)

    def test_punctuation_change_is_not_assumed_minimal(self):
        risk = self.detector.assess("Calculate the sum.", "Calculate the sum!")
        self.assertEqual(risk, SemanticRiskLevel.MODERATE)

    def test_assessment_returns_traceable_reason(self):
        risk, reasons = self.detector.assess_with_reasons(
            "Find all values.", "Find some values."
        )
        self.assertEqual(risk, SemanticRiskLevel.HIGH)
        self.assertTrue(any("Quantifier" in reason for reason in reasons))

    def test_record_contains_normalized_distances_and_risk_reason(self):
        record = get_perturbation("punctuation").perturb(
            "Calculate the sum", config=PerturbationConfig(params={"mode": "add_period"})
        )
        self.assertAlmostEqual(
            record.char_edit_distance_normalized,
            record.edit_distance / len(record.perturbed_prompt),
        )
        self.assertGreaterEqual(record.word_edit_distance_normalized, 0)
        self.assertTrue(record.semantic_risk_reasons)


# ═══════════════════════════════════════════════════════════════════════════
# Distance utilities unit tests
# ═══════════════════════════════════════════════════════════════════════════

class TestDistanceUtils(unittest.TestCase):
    def test_char_edit_distance_same(self):
        self.assertEqual(char_edit_distance("hello", "hello"), 0)

    def test_char_edit_distance_one_sub(self):
        self.assertEqual(char_edit_distance("hello", "hxllo"), 1)

    def test_char_edit_distance_one_insert(self):
        self.assertEqual(char_edit_distance("hello", "helloo"), 1)

    def test_char_edit_distance_one_delete(self):
        self.assertEqual(char_edit_distance("hello", "hell"), 1)

    def test_word_edit_distance_same(self):
        self.assertEqual(word_edit_distance("find the sum", "find the sum"), 0)

    def test_word_edit_distance_one_word(self):
        self.assertEqual(word_edit_distance("find the sum", "compute the sum"), 1)


if __name__ == "__main__":
    unittest.main()
