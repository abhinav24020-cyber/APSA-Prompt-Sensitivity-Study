"""End-to-end pilot test: runs a minimal experiment config with mock providers."""

import json
from types import SimpleNamespace

from apsa.llm_providers import MockProvider
from apsa.llm_providers.exceptions import RateLimitError
from experiments.pilot_experiment import run_pilot


class FakeSemanticCalculator:
    embedding_model_name = "test-embedding-model"

    def compute(self, original, perturbed):
        return SimpleNamespace(
            cosine_distance=0.02,
            cosine_similarity=0.98,
            embedding_model=self.embedding_model_name,
        )


class TestEndToEndPilot:
    def test_pilot_experiment_produces_runs_jsonl(self, tmp_path):
        # 1. Setup mock provider tuple
        mock_provider = MockProvider("mock-pilot-model")
        providers = [(mock_provider, {"temperature": 0.0, "max_tokens": 128})]

        # 2. Setup minimal prompts sample
        sample_prompts = [
            {
                "prompt_id": "MATH-001",
                "task_category": "mathematical_reasoning",
                "original_prompt": "Calculate 2 + 2.",
                "expected_answer": "4"
            },
            {
                "prompt_id": "QA-001",
                "task_category": "question_answering",
                "original_prompt": "What is the capital of France?",
                "expected_answer": "Paris"
            }
        ]

        # 3. Run pilot with mock provider
        output_dir = tmp_path / "raw"
        run_dir = run_pilot(
            providers,
            sample_prompts,
            output_dir,
            repetitions=1,
            is_mock=True,
            control_repetitions=1,
            max_tokens=512,
            semantic_calculator=FakeSemanticCalculator(),
        )

        # 4. Verify outputs
        jsonl_files = list(output_dir.rglob("raw_results.jsonl"))
        assert len(jsonl_files) == 1
        results_file = jsonl_files[0]

        records = []
        with open(results_file, "r", encoding="utf-8") as f:
            for line in f:
                records.append(json.loads(line))

        assert len(records) > 0
        first = records[0]
        assert "experiment_id" in first
        assert "model" in first
        assert "task_category" in first
        assert "prompt_id" in first
        assert "original_prompt" in first
        assert "perturbed_prompt" in first
        assert "input_distances" in first
        assert "original_output" in first
        assert "perturbed_output" in first
        assert first["status"] == "success"

        # 5. Verify report is generated
        report_file = run_dir / "pilot_report.md"
        assert report_file.exists()
        report_text = report_file.read_text(encoding="utf-8")
        assert "Mock Provider" in report_text
        assert "Inapplicable Perturbation Candidates" in report_text
        assert "word_substitution" in report_text
        assert "control repetitions" in report_text
        manifest = json.loads((run_dir / "run_manifest.json").read_text(encoding="utf-8"))
        assert manifest["execution_mode"] == "mock"
        assert manifest["generation"]["semantic_input_model"] == "test-embedding-model"
        assert manifest["models"][0]["generation_config"]["max_tokens"] == 512
        assert manifest["counts"]["successful_trials"] == len(records)
        assert any(row["condition"] == "control" for row in records)
        assert any(
            row.get("finish_reasons", {}).get("original") is None
            for row in records
            if row["condition"] == "treatment"
        )
        treatment = next(row for row in records if row["condition"] == "treatment")
        assert treatment["input_distances"]["semantic_cosine_distance"] == 0.02

    def test_pilot_stops_after_rate_limit_and_persists_failure(self, tmp_path):
        class LimitedProvider:
            model_name = "limited-model"

            def generate(self, prompt, configuration):
                raise RateLimitError("provider rate limit", retry_after=120)

        output_dir = tmp_path / "raw"
        run_pilot(
            [(LimitedProvider(), {})],
            [{
                "prompt_id": "QA-001",
                "task_category": "question_answering",
                "original_prompt": "What is the capital of France?",
            }],
            output_dir,
            repetitions=1,
            semantic_calculator=FakeSemanticCalculator(),
        )

        result_file = next(output_dir.rglob("raw_results.jsonl"))
        records = [json.loads(line) for line in result_file.read_text(encoding="utf-8").splitlines()]
        assert records == []
        failures_file = result_file.with_name("failed_trials.jsonl")
        failures = [
            json.loads(line)
            for line in failures_file.read_text(encoding="utf-8").splitlines()
        ]
        assert len(failures) == 1
        assert failures[0]["status"] == "failed"
        assert failures[0]["error_type"] == "RateLimitError"
        assert failures[0]["retry_after_seconds"] == 120
        assert failures[0]["remaining_trials_aborted"] is True

        report = result_file.parent.joinpath("pilot_report.md").read_text(encoding="utf-8")
        assert "Partially Completed" in report
        assert "Failed Trials**: 1" in report

    def test_pilot_finalizes_partial_artifacts_after_interrupt(self, tmp_path):
        class InterruptedProvider:
            model_name = "interrupted-model"

            def generate(self, prompt, configuration):
                raise KeyboardInterrupt

        run_dir = run_pilot(
            [(InterruptedProvider(), {})],
            [{
                "prompt_id": "QA-001",
                "task_category": "question_answering",
                "original_prompt": "What is the capital of France?",
            }],
            tmp_path / "output",
            repetitions=1,
            semantic_calculator=FakeSemanticCalculator(),
        )

        manifest = json.loads((run_dir / "run_manifest.json").read_text(encoding="utf-8"))
        report = (run_dir / "pilot_report.md").read_text(encoding="utf-8")
        assert manifest["status"] == "interrupted"
        assert "Interrupted (partial results saved)" in report
        assert (run_dir / "raw_results.jsonl").read_text(encoding="utf-8") == ""
        assert (run_dir / "failed_trials.jsonl").read_text(encoding="utf-8") == ""

    def test_pilot_preserves_one_sided_response_when_paired_call_fails(self, tmp_path):
        class PartialProvider:
            model_name = "partial-model"

            def __init__(self):
                self.calls = 0

            def generate(self, prompt, configuration):
                self.calls += 1
                if self.calls == 2:
                    raise RateLimitError("provider rate limit", retry_after=30)
                return SimpleNamespace(
                    output="saved partial response",
                    latency=0.1,
                    input_tokens=3,
                    output_tokens=4,
                    finish_reason="stop",
                )

        run_dir = run_pilot(
            [(PartialProvider(), {})],
            [{
                "prompt_id": "QA-001",
                "task_category": "question_answering",
                "original_prompt": "What is the capital of France?",
            }],
            tmp_path / "output",
            repetitions=1,
            semantic_calculator=FakeSemanticCalculator(),
        )

        failures = [
            json.loads(line)
            for line in (run_dir / "failed_trials.jsonl").read_text(
                encoding="utf-8"
            ).splitlines()
        ]
        assert failures[0]["partial_generations"]["original"]["output"] == (
            "saved partial response"
        )
        assert failures[0]["partial_generations"]["perturbed"] is None
