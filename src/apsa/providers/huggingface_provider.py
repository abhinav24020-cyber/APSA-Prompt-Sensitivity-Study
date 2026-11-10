"""LLM provider backend for local HuggingFace / vLLM models."""

from apsa.config.schema import ModelConfig
from .base_provider import BaseLLMProvider, Message, GenerationConfig, GenerationResult


class HuggingFaceProvider(BaseLLMProvider):
    """Wraps local HuggingFace `transformers` (or optionally vLLM) inference.

    Reads ``HF_TOKEN`` from the environment variable declared in
    :attr:`ModelConfig.api_key_env_var`.  Never stores credentials.
    """

    def __init__(self, model_config: ModelConfig) -> None:
        self._config = model_config
        # TODO: load tokenizer and model (or vLLM engine) here

    def generate(self, messages: list[Message], config: GenerationConfig) -> GenerationResult:
        raise NotImplementedError

    def get_model_id(self) -> str:
        return self._config.model_id

    def count_tokens(self, text: str) -> int:
        raise NotImplementedError
