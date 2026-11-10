"""Pass@1 delta evaluator for code generation tasks.

Runs generated Python code in a sandboxed subprocess against unit tests.
"""

from dataclasses import dataclass


@dataclass
class CodeExecutionResult:
    applicable: bool
    original_pass: bool
    perturbed_pass: bool
    functional_failure: bool
    original_error: str | None = None
    perturbed_error: str | None = None


class CodeExecutionEvaluator:
    """Execute and test Python code extracted from LLM outputs."""

    def __init__(self, timeout_seconds: int = 10) -> None:
        self._timeout = timeout_seconds

    def evaluate(
        self,
        original_output: str,
        perturbed_output: str,
        test_code: str,
    ) -> CodeExecutionResult:
        # TODO: extract code blocks, run in sandboxed subprocess
        raise NotImplementedError
