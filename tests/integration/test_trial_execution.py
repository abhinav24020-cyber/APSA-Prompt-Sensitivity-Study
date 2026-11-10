"""Integration test for a single trial execution (uses mock providers)."""

import pytest
from apsa.llm_providers import MockProvider
from apsa.perturbations import get_perturbation
from apsa.perturbations.base_perturbation import PerturbationConfig
from apsa.metrics.input_distance import LexicalDistanceCalculator
from apsa.metrics.output_distance import OutputDeviationMetrics
from apsa.analysis.sensitivity import SensitivityRecord, SensitivityAnalyzer
from apsa.execution.budget_enforcer import BudgetEnforcer
from apsa.config.schema import EpsilonBudget


class TestTrialRunner:
    def test_trial_runner_with_mock_provider(self):
        # 1. Setup mock provider and prompt
        provider = MockProvider("mock-test-model")
        original_prompt = "Calculate the sum of 2 and 2"
        
        # 2. Apply perturbation
        pert = get_perturbation("punctuation")
        config = PerturbationConfig(params={"mode": "add_trailing_period"}, seed=42)
        pert_record = pert.perturb(original_prompt, prompt_id="MATH-001", config=config)
        assert pert_record is not None
        perturbed_prompt = pert_record.perturbed_prompt
        assert perturbed_prompt == "Calculate the sum of 2 and 2."

        # 3. Input distance & budget enforcement
        lex_calc = LexicalDistanceCalculator()
        lex_res = lex_calc.compute(original_prompt, perturbed_prompt)
        assert lex_res.char_levenshtein == 1
        assert 0.0 < lex_res.char_levenshtein_normalized < 0.1

        budget = EpsilonBudget(lexical_char_normalized=0.15, lexical_word_normalized=0.25)
        enforcer = BudgetEnforcer(budget)
        assert enforcer.is_within_budget(
            lexical_result=lex_res,
            original_prompt=original_prompt,
            perturbed_prompt=perturbed_prompt,
            run_id="trial-1"
        ) is True

        # 4. Model execution
        gen_cfg = {"temperature": 0.0, "max_tokens": 128}
        orig_gen = provider.generate(original_prompt, gen_cfg)
        pert_gen = provider.generate(perturbed_prompt, gen_cfg)
        assert orig_gen.output != ""
        assert pert_gen.output != ""

        # 5. Output distance calculation
        out_metrics = OutputDeviationMetrics(use_semantic=False)
        out_comp = out_metrics.compute_all(orig_gen.output, pert_gen.output)
        assert out_comp["is_valid"] is True
        assert 0.0 <= out_comp["normalized_character_distance"] <= 1.0

        # 6. Sensitivity scoring
        sens_record = SensitivityRecord(
            experiment_id="int_test_exp",
            model=provider.model_name,
            task_category="question_answering",
            prompt_id="QA-001",
            perturbation_type="punctuation",
            d_input=lex_res.char_levenshtein_normalized,
            d_semantic_input=0.01,
            d_output=out_comp["normalized_character_distance"]
        )
        analyzer = SensitivityAnalyzer([sens_record])
        s_score = analyzer.calculate_sensitivity(sens_record)
        assert s_score >= 0.0
