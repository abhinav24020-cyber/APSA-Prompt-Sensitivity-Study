from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from apsa.config.schema import PerturbationConfig
from apsa.execution.trial import TrialRunner
from apsa.metrics.input_distance.lexical import LexicalDistanceCalculator


def _trial_runner() -> TrialRunner:
    runner = object.__new__(TrialRunner)
    runner._config = SimpleNamespace(
        system_prompt="",
        experiment=SimpleNamespace(seed=42),
    )
    return runner


def _patch_formatter(monkeypatch, original_prompt: str) -> None:
    formatter = SimpleNamespace(
        format=Mock(return_value=SimpleNamespace(original_prompt=original_prompt))
    )
    monkeypatch.setattr(
        "apsa.prompts.registry.get_formatter",
        lambda _task_category: formatter,
    )


def _item():
    return SimpleNamespace(
        id="QA-001",
        task_category=SimpleNamespace(value="question_answering"),
        gold_answer="answer",
    )


def test_inapplicable_perturbation_does_not_make_model_request(monkeypatch):
    _patch_formatter(monkeypatch, "A one-sentence prompt.")
    operator = SimpleNamespace(perturb=Mock(return_value=None))
    monkeypatch.setattr(
        "apsa.perturbations.registry.get_perturbation",
        lambda _name: operator,
    )
    runner = _trial_runner()
    runner._get_provider = Mock()

    with pytest.raises(ValueError, match="not applicable"):
        runner.execute(
            run_id="run-1",
            item=_item(),
            model_config=None,
            perturbation_config=PerturbationConfig(type="unsupported_here"),
        )

    runner._get_provider.assert_not_called()


def test_over_budget_perturbation_does_not_make_model_request(monkeypatch):
    _patch_formatter(monkeypatch, "Calculate the answer")
    runner = _trial_runner()
    runner._lexical_calc = LexicalDistanceCalculator()
    runner._compute_semantic_cosine = Mock(return_value=0.5)
    runner._budget_enforcer = SimpleNamespace(
        is_within_budget=Mock(return_value=False)
    )
    runner._get_provider = Mock()

    with pytest.raises(ValueError, match="exceeds"):
        runner.execute(
            run_id="run-2",
            item=_item(),
            model_config=None,
            perturbation_config=PerturbationConfig(
                type="punctuation",
                params={"mode": "add_trailing_period"},
            ),
        )

    runner._get_provider.assert_not_called()


def test_missing_semantic_encoder_does_not_fall_back_to_lexical_distance():
    runner = _trial_runner()
    runner._get_embedder = Mock(return_value=None)

    with pytest.raises(RuntimeError, match="Semantic input distance is unavailable"):
        runner._compute_semantic_cosine("original", "perturbed")


def test_default_config_stores_no_fake_sensitivity_for_missing_syntax_metric():
    # The runner records a missing score when syntactic distance has positive weight.
    # This assertion protects the storage schema's explicit missing-value contract.
    from apsa.storage.schema import ExperimentRun

    assert ExperimentRun.model_fields["sensitivity_coefficient"].annotation == float | None

