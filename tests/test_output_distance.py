import pytest
from apsa.metrics.output_distance import OutputDeviationMetrics, CorrectnessEvaluator

def test_exact_match():
    metrics = OutputDeviationMetrics(use_semantic=False)
    assert metrics.exact_match("hello world", "hello world") is True
    assert metrics.exact_match("hello world", "hello world ") is True
    assert metrics.exact_match("hello world", "hello  world") is False
    assert metrics.exact_match(None, "hello world") is False
    assert metrics.exact_match("hello world", None) is False
    assert metrics.exact_match(None, None) is False

def test_normalized_string_similarity():
    metrics = OutputDeviationMetrics(use_semantic=False)
    sim = metrics.normalized_string_similarity("kitten", "sitting")
    # kitten -> sitting: Levenshtein distance is 3. Max len is 7. Similarity = 1 - 3/7 = 4/7 ≈ 0.5714
    assert abs(sim - (4/7)) < 1e-4
    assert metrics.normalized_string_similarity(None, "abc") == 0.0
    assert metrics.normalized_string_similarity("abc", None) == 0.0

def test_normalized_character_distance():
    metrics = OutputDeviationMetrics(use_semantic=False)
    dist = metrics.normalized_character_distance("kitten", "sitting")
    assert abs(dist - (3/7)) < 1e-4
    assert metrics.normalized_character_distance("same", "same") == 0.0
    assert metrics.normalized_character_distance(None, "abc") == 1.0

def test_character_level_distance():
    metrics = OutputDeviationMetrics(use_semantic=False)
    assert metrics.character_level_distance("kitten", "sitting") == 3
    assert metrics.character_level_distance("same", "same") == 0
    assert metrics.character_level_distance(None, "same") == -1

def test_token_level_distance():
    metrics = OutputDeviationMetrics(use_semantic=False)
    dist = metrics.token_level_distance("a b c", "b c d")
    assert abs(dist - 0.5) < 1e-4
    assert metrics.token_level_distance(None, "a b") == 1.0

def test_compute_all():
    metrics = OutputDeviationMetrics(use_semantic=False)
    res_valid = metrics.compute_all("hello", "hello world")
    assert res_valid["is_valid"] is True
    assert "normalized_character_distance" in res_valid
    assert 0.0 <= res_valid["normalized_character_distance"] <= 1.0

    res_invalid = metrics.compute_all(None, "hello")
    assert res_invalid["is_valid"] is False
    assert res_invalid["error"] is not None

def test_correctness_evaluator_classification():
    assert CorrectnessEvaluator.evaluate_classification(True, False) == "correct -> incorrect"
    assert CorrectnessEvaluator.evaluate_classification(False, True) == "incorrect -> correct"
    assert CorrectnessEvaluator.evaluate_classification(True, True) == "same class"
    assert CorrectnessEvaluator.evaluate_classification(False, False) == "same class"
    assert CorrectnessEvaluator.evaluate_classification(None, True) == "unknown / unevaluated"

def test_correctness_evaluator_reasoning():
    assert CorrectnessEvaluator.evaluate_reasoning(True, False) == "correct -> incorrect"
    assert CorrectnessEvaluator.evaluate_reasoning(False, True) == "incorrect -> correct"
    assert CorrectnessEvaluator.evaluate_reasoning(True, True) == "same answer"
    assert CorrectnessEvaluator.evaluate_reasoning(False, False) == "same answer"
    assert CorrectnessEvaluator.evaluate_reasoning(True, None) == "unknown / unevaluated"
