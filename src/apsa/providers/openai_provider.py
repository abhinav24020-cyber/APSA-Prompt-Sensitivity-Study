"""LLM provider backend for OpenAI-compatible API endpoints (future extension)."""

import os
from apsa.config.schema import ModelConfig
from .base_provider import BaseLLMProvider, Message, GenerationConfig, GenerationResult


class OpenAIProvider(BaseLLMProvider):
    """Wraps the OpenAI Python SDK for OpenAI-compatible endpoints.

    The API key is read from the environment variable declared in
    :attr:`ModelConfig.api_key_env_var` (typically ``OPENAI_API_KEY``).
    """

    def __init__(self, model_config: ModelConfig) -> None:
        self._config = model_config
        # TODO: initialise openai client from env var

    def generate(self, messages: list[Message], config: GenerationConfig) -> GenerationResult:
        raise NotImplementedError

    def get_model_id(self) -> str:
        return self._config.model_id

    def count_tokens(self, text: str) -> int:
        raise NotImplementedError
