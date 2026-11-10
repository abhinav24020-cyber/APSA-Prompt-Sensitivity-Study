"""Mock provider for unit/integration testing without API credentials."""

from apsa.config.schema import ModelConfig
from .base_provider import BaseLLMProvider, Message, GenerationConfig, GenerationResult


class MockProvider(BaseLLMProvider):
    def __init__(self, model_config: ModelConfig) -> None:
        self._config = model_config

    def generate(self, messages: list[Message], config: GenerationConfig) -> GenerationResult:
        full_text = " ".join(m.content for m in messages)
        if "2 + 2" in full_text or "2+2" in full_text:
            output_text = "4"
        elif "capital of France" in full_text:
            output_text = "Paris"
        else:
            output_text = f"Mock response for input length {len(full_text)}"

        return GenerationResult(
            output_text=output_text,
            model_name=self._config.model_id,
            gen_config=config,
            token_count=len(output_text.split()),
            latency_ms=5.0,
        )

    def get_model_id(self) -> str:
        return self._config.model_id

    def count_tokens(self, text: str) -> int:
        return len(text.split())

