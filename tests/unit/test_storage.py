"""Unit tests for storage layer (schema, writer, reader)."""

from datetime import UTC, datetime

from apsa.storage.schema import (
    EpsilonBudgetUsed,
    ExperimentFailure,
    ExperimentRun,
    FunctionalMetrics,
    GenerationConfigSnapshot,
    InputDistanceMetrics,
    OutputDistanceMetrics,
)
from apsa.storage.writer import ResultWriter


class TestExperimentRunSchema:
    def test_minimal_valid_run(self):
        run = ExperimentRun(
            experiment_id="test_exp_001",
            run_id="run_001",
            timestamp=datetime.now(UTC),
            condition="treatment",
            model_name="gemini-1.5-flash",
            task_category="mathematical_reasoning",
            perturbation_type="punctuation",
            dataset_item_id="MATH-001",
            generation_config=GenerationConfigSnapshot(
                temperature=0.0,
                top_p=0.95,
                max_tokens=1024,
                seed=42,
            ),
            original_prompt="Calculate 2 + 2.",
            perturbed_prompt="Calculate 2 + 2. ",
            original_output="4",
            perturbed_output="4",
            original_token_count=5,
            perturbed_token_count=5,
            input_distance=InputDistanceMetrics(
                lexical_char_levenshtein=1.0,
                lexical_word_levenshtein=0.0,
                lexical_jaccard_bigram=0.0,
                syntactic_tree_edit_distance=0.0,
                semantic_cosine_distance=0.001,
            ),
            output_distance=OutputDistanceMetrics(
                textual_levenshtein=0.0,
                rouge_1_f1=1.0,
                rouge_2_f1=1.0,
                rouge_l_f1=1.0,
                bleu_score=1.0,
                token_jaccard=0.0,
                semantic_bertscore_f1_disparity=0.0,
                semantic_embedding_cosine=0.0,
                llm_judge_score_delta=0.0,
            ),
            functional_metrics=FunctionalMetrics(
                applicable=True,
                original_pass=True,
                perturbed_pass=True,
                functional_failure=False,
            ),
            composite_output_divergence=0.0,
            sensitivity_coefficient=0.0,
            original_latency_ms=120.0,
            perturbed_latency_ms=115.0,
            epsilon_budget_used=EpsilonBudgetUsed(
                lexical_char_normalized=0.05,
                semantic_cosine=0.001,
            ),
        )
        data = run.model_dump()
        assert data["experiment_id"] == "test_exp_001"
        assert data["condition"] == "treatment"
        assert data["input_distance"]["lexical_char_levenshtein"] == 1.0

    def test_failure_records_are_written_separately(self, tmp_path):
        writer = ResultWriter(tmp_path / "results.jsonl")
        failure = ExperimentFailure(
            experiment_id="test_exp_001",
            run_id="run_002",
            timestamp=datetime.now(UTC),
            model_name="mock-model",
            task_category="question_answering",
            perturbation_type="punctuation",
            dataset_item_id="QA-001",
            error_type="RuntimeError",
            error_message="provider request failed",
        )

        writer.write_failure(failure)

        failure_path = tmp_path / "failures.jsonl"
        stored = failure_path.read_text(encoding="utf-8").splitlines()
        assert len(stored) == 1
        assert '"run_id":"run_002"' in stored[0]
        assert '"error_type":"RuntimeError"' in stored[0]
