"""Unit tests for metric calculators and budget enforcement."""

import pytest
from apsa.metrics.composite import CompositeOutputDivergence
from apsa.config.schema import MetricWeights, EpsilonBudget
from apsa.execution.budget_enforcer import BudgetEnforcer
from apsa.metrics.input_distance.lexical import LexicalDistanceResult


class TestCompositeOutputDivergence:
    def test_weighted_sum(self):
        weights = MetricWeights(w1_textual=0.33, w2_semantic=0.34, w3_functional=0.33)
        calc = CompositeOutputDivergence(weights)
        d_out = calc.compute(d_text_out=1.0, d_sem_out=0.5, delta_f_task=1.0)
        expected = 0.33 * 1.0 + 0.34 * 0.5 + 0.33 * 1.0
        assert abs(d_out - expected) < 1e-6


class TestBudgetEnforcer:
    def test_within_budget(self):
        budget = EpsilonBudget(
            lexical_char_normalized=0.10,
            lexical_word_normalized=0.15,
            semantic_cosine=0.05,
        )
        enforcer = BudgetEnforcer(budget)
        lex_res = LexicalDistanceResult(
            char_levenshtein=2,
            char_levenshtein_normalized=0.05,
            word_levenshtein=1,
            num_words_changed=10,
            num_chars_changed=2,
            pct_prompt_changed=5.0,
        )
        assert enforcer.is_within_budget(lexical_result=lex_res) is True

    def test_exceed_budget(self):
        budget = EpsilonBudget(
            lexical_char_normalized=0.10,
            lexical_word_normalized=0.15,
            semantic_cosine=0.05,
        )
        enforcer = BudgetEnforcer(budget)
        lex_res = LexicalDistanceResult(
            char_levenshtein=10,
            char_levenshtein_normalized=0.25,
            word_levenshtein=3,
            num_words_changed=5,
            num_chars_changed=10,
            pct_prompt_changed=25.0,
        )
        assert enforcer.is_within_budget(lexical_result=lex_res) is False
