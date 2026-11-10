"""End-to-end tests for PerturbationEngine."""

import unittest

from apsa.perturbations.engine import PerturbationEngine
from apsa.perturbations.perturbation_record import PerturbationRecord
from apsa.perturbations.semantic_flags import SemanticRiskLevel

_SINGLE_SENTENCE = "Calculate the sum of all prime numbers less than 50."
_MULTI_SENTENCE = "A sequence of integers is provided. Find all prime numbers less than 50."


class TestPerturbationEngine(unittest.TestCase):

    def setUp(self):
        self.engine = PerturbationEngine()

    def test_apply_all_returns_list(self):
        records = self.engine.apply_all(_SINGLE_SENTENCE, prompt_id="MATH-001", seed=42)
        self.assertIsInstance(records, list)
        self.assertGreater(len(records), 0)

    def test_all_records_are_valid_type(self):
        records = self.engine.apply_all(_SINGLE_SENTENCE, prompt_id="MATH-001", seed=42)
        for rec in records:
            self.assertIsInstance(rec, PerturbationRecord)

    def test_all_perturbation_ids_unique(self):
        records = self.engine.apply_all(_SINGLE_SENTENCE, prompt_id="MATH-001", seed=42)
        ids = [r.perturbation_id for r in records]
        self.assertEqual(len(ids), len(set(ids)), "Duplicate perturbation_ids found")

    def test_all_records_have_nonzero_edit_distance(self):
        records = self.engine.apply_all(_SINGLE_SENTENCE, prompt_id="MATH-001", seed=42)
        for rec in records:
            self.assertGreater(
                rec.edit_distance, 0,
                f"Zero edit distance for {rec.perturbation_type}"
            )

    def test_all_records_have_semantic_risk(self):
        records = self.engine.apply_all(_SINGLE_SENTENCE, prompt_id="MATH-001", seed=42)
        for rec in records:
            self.assertIsInstance(rec.semantic_risk_level, SemanticRiskLevel)

    def test_multi_sentence_enables_reordering(self):
        records = self.engine.apply_all(_MULTI_SENTENCE, prompt_id="MATH-002", seed=42)
        types = [r.perturbation_type for r in records]
        self.assertIn("instruction_reordering", types)

    def test_single_sentence_skips_reordering(self):
        records = self.engine.apply_all(_SINGLE_SENTENCE, prompt_id="MATH-001", seed=42)
        types = [r.perturbation_type for r in records]
        self.assertNotIn("instruction_reordering", types)

    def test_to_dict_serializable(self):
        records = self.engine.apply_all(_SINGLE_SENTENCE, prompt_id="MATH-001", seed=42)
        for rec in records:
            d = rec.to_dict()
            self.assertIn("perturbation_id", d)
            self.assertIn("perturbation_type", d)
            self.assertIn("semantic_risk_level", d)
            self.assertIn("edit_distance", d)

    def test_apply_single(self):
        record = self.engine.apply_single(
            _SINGLE_SENTENCE,
            perturbation_type="capitalization",
            prompt_id="MATH-001",
            seed=42,
            params={"mode": "all_lowercase"},
        )
        self.assertIsNotNone(record)
        self.assertEqual(record.perturbation_type, "capitalization")

    def test_unknown_operator_is_not_silently_ignored(self):
        engine = PerturbationEngine(custom_configs=[("misspelled_operator", {})])
        with self.assertRaisesRegex(KeyError, "Unknown perturbation"):
            engine.apply_all(_SINGLE_SENTENCE)

    def test_same_operator_with_distinct_parameters_has_distinct_ids(self):
        engine = PerturbationEngine(custom_configs=[
            ("capitalization", {"mode": "all_lowercase"}),
            ("capitalization", {"mode": "all_uppercase"}),
        ])
        records = engine.apply_all(_SINGLE_SENTENCE, prompt_id="MATH-001", seed=42)
        self.assertEqual(len(records), 2)
        self.assertEqual(len({record.perturbation_id for record in records}), 2)

    def test_deterministic_with_same_seed(self):
        records1 = self.engine.apply_all(_SINGLE_SENTENCE, prompt_id="X", seed=42)
        records2 = self.engine.apply_all(_SINGLE_SENTENCE, prompt_id="X", seed=42)
        for r1, r2 in zip(records1, records2):
            self.assertEqual(r1.perturbed_prompt, r2.perturbed_prompt)
            self.assertEqual(r1.perturbation_id, r2.perturbation_id)

    def test_different_seeds_can_produce_different_results(self):
        records1 = self.engine.apply_all(_SINGLE_SENTENCE, prompt_id="X", seed=1)
        records2 = self.engine.apply_all(_SINGLE_SENTENCE, prompt_id="X", seed=999)
        prompts1 = {r.perturbation_type: r.perturbed_prompt for r in records1}
        prompts2 = {r.perturbation_type: r.perturbed_prompt for r in records2}
        # At least one operator should differ between seeds
        differs = any(
            prompts1.get(t) != prompts2.get(t)
            for t in prompts1 if t in prompts2
        )
        self.assertTrue(differs, "All operators produced identical results for different seeds")


if __name__ == "__main__":
    unittest.main()
