"""JSON schema validation failure indicator for structured extraction tasks."""

from dataclasses import dataclass
from typing import Any


@dataclass
class SchemaValidationResult:
    applicable: bool
    original_pass: bool
    perturbed_pass: bool
    functional_failure: bool


class SchemaValidationEvaluator:
    """Validate that Y' conforms to JSON schema when Y is valid JSON."""

    def evaluate(
        self,
        original_output: str,
        perturbed_output: str,
        expected_schema: dict[str, Any] | None = None,
    ) -> SchemaValidationResult:
        # TODO: implement via jsonschema library
        raise NotImplementedError
