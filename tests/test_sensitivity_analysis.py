import pytest
import numpy as np
from apsa.analysis.sensitivity import SensitivityRecord, SensitivityAnalyzer

@pytest.fixture
def sample_records():
    return [
        SensitivityRecord(
            experiment_id="exp1", model="gpt-4o", task_category="math", prompt_id="p1", perturbation_type="word_deletion",
            d_input=0.1, d_semantic_input=0.01, d_output=0.5
        ),
        SensitivityRecord(
            experiment_id="exp1", model="gpt-4o", task_category="math", prompt_id="p2", perturbation_type="word_insertion",
            d_input=0.2, d_semantic_input=0.06, d_output=0.8
        ),
        SensitivityRecord(
            experiment_id="exp1", model="gemini-1.5-flash", task_category="coding", prompt_id="p1", perturbation_type="word_deletion",
            d_input=0.1, d_semantic_input=0.02, d_output=0.1
        )
    ]

def test_calculate_sensitivity(sample_records):
    analyzer = SensitivityAnalyzer(sample_records, epsilon=1e-4)
    record = sample_records[0]
    expected_s = 0.5 / (0.1 + 1e-4)
    assert abs(analyzer.calculate_sensitivity(record) - expected_s) < 1e-6

def test_calculate_sensitivity_methodology_bounded(sample_records):
    analyzer = SensitivityAnalyzer(sample_records, eta=1e-4)
    record = sample_records[0]
    # S = D_out / max(eta, D_in) -> 0.5 / max(1e-4, 0.1) = 0.5 / 0.1 = 5.0
    expected_s = 0.5 / max(1e-4, 0.1)
    assert abs(analyzer.calculate_sensitivity(record, method="methodology_bounded") - expected_s) < 1e-6

def test_sensitivity_zero_distances():
    zero_rec = SensitivityRecord(
        experiment_id="exp1", model="gpt-4o", task_category="math", prompt_id="p0", perturbation_type="control",
        d_input=0.0, d_semantic_input=0.0, d_output=0.0
    )
    analyzer = SensitivityAnalyzer([zero_rec])
    assert analyzer.calculate_sensitivity(zero_rec) == 0.0

def test_sensitivity_negative_distances():
    bad_rec = SensitivityRecord(
        experiment_id="exp1", model="gpt-4o", task_category="math", prompt_id="p0", perturbation_type="control",
        d_input=-0.1, d_semantic_input=0.0, d_output=0.5
    )
    analyzer = SensitivityAnalyzer([bad_rec])
    with pytest.raises(ValueError, match="non-negative"):
        analyzer.calculate_sensitivity(bad_rec)

def test_statistical_aggregations(sample_records):
    analyzer = SensitivityAnalyzer(sample_records)
    assert analyzer.mean_output_deviation() == pytest.approx((0.5 + 0.8 + 0.1) / 3)
    assert analyzer.median_output_deviation() == pytest.approx(0.5)

def test_confidence_interval(sample_records):
    analyzer = SensitivityAnalyzer(sample_records)
    ci_low, ci_high = analyzer.confidence_interval_output_deviation(confidence=0.95)
    assert ci_low < ci_high
    assert ci_low <= analyzer.mean_output_deviation() <= ci_high

def test_confidence_interval_single_item():
    single = [SensitivityRecord(
        experiment_id="exp1", model="gpt-4o", task_category="math", prompt_id="p1", perturbation_type="word_deletion",
        d_input=0.1, d_semantic_input=0.01, d_output=0.5
    )]
    analyzer = SensitivityAnalyzer(single)
    ci_low, ci_high = analyzer.confidence_interval_output_deviation()
    assert ci_low == 0.5
    assert ci_high == 0.5

def test_max_output_deviation_under_budget(sample_records):
    analyzer = SensitivityAnalyzer(sample_records)
    # Budget 0.05 excludes the second record (d_semantic=0.06)
    max_dev = analyzer.max_output_deviation_under_budget(semantic_budget=0.05)
    assert max_dev == 0.5  # From the first record

    # Test joint budget (semantic and lexical)
    max_dev_joint = analyzer.max_output_deviation_under_budget(semantic_budget=0.05, lexical_budget=0.05)
    assert max_dev_joint == 0.0  # none satisfy d_input <= 0.05

def test_top_k_cases(sample_records):
    analyzer = SensitivityAnalyzer(sample_records)
    top_k = analyzer.top_k_sensitivity_cases(k=1)
    assert len(top_k) == 1
    assert top_k[0][0].model == "gpt-4o"
    assert top_k[0][0].prompt_id == "p1"

def test_highest_sensitivity_per_group(sample_records):
    analyzer = SensitivityAnalyzer(sample_records)
    
    per_model = analyzer.highest_sensitivity_per_model()
    assert per_model["gpt-4o"] == pytest.approx(0.5 / (0.1 + 1e-4))
    assert per_model["gemini-1.5-flash"] == pytest.approx(0.1 / (0.1 + 1e-4))
    
    per_task = analyzer.highest_sensitivity_per_task()
    assert "math" in per_task
    assert "coding" in per_task
    
    per_pert = analyzer.highest_sensitivity_per_perturbation()
    assert "word_deletion" in per_pert
    assert "word_insertion" in per_pert
