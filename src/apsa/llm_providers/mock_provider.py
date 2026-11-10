import time
from typing import Dict, Any, Optional
from .base import BaseLLMProvider, GenerationResult

class MockProvider(BaseLLMProvider):
    """Mock LLM Provider for safe testing and integration verification without API credentials."""
    
    def __init__(self, model_name: str = "mock-model"):
        super().__init__(model_name)
        self._canned_response: Optional[str] = None
        self._simulate_error: bool = False

    def set_canned_response(self, response: str) -> None:
        self._canned_response = response

    def set_simulate_error(self, simulate_error: bool) -> None:
        self._simulate_error = simulate_error

    def generate(self, prompt: str, configuration: Dict[str, Any]) -> GenerationResult:
        if self._simulate_error or "[TRIGGER_ERROR]" in prompt:
            from .exceptions import GenerationError
            raise GenerationError("Simulated mock generation failure")

        if self._canned_response is not None:
            output = self._canned_response
        else:
            # Deterministic pseudo-generation based on prompt
            # For deterministic tasks, produce a consistent answer
            if "capital of France" in prompt:
                output = "The capital of France is Paris."
            elif "2 + 2" in prompt or "2+2" in prompt:
                output = "4"
            else:
                # Produce a predictable output incorporating prompt length and hash
                output = f"Mock response for prompt: {prompt[:30]}... (len={len(prompt)})"

        input_tokens = len(prompt.split())
        output_tokens = len(output.split())

        return GenerationResult(
            model_name=self.model_name,
            prompt=prompt,
            output=output,
            latency=0.005,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            generation_configuration=configuration
        )
