"""Provider registry: maps provider type strings to backend classes."""

from apsa.config.schema import ModelConfig
from .base_provider import BaseLLMProvider
from .huggingface_provider import HuggingFaceProvider
from .gemini_provider import GeminiProvider
from .openai_provider import OpenAIProvider
from .groq_provider import GroqProvider
from .mock_provider import MockProvider

_REGISTRY: dict[str, type[BaseLLMProvider]] = {
    "huggingface": HuggingFaceProvider,
    "gemini":      GeminiProvider,
    "openai":      OpenAIProvider,
    "groq":        GroqProvider,
    "mock":        MockProvider,
}


def get_provider(model_config: ModelConfig) -> BaseLLMProvider:
    """Instantiate and return the appropriate backend for the given model config."""
    provider_type = model_config.provider.lower()
    if provider_type not in _REGISTRY:
        raise KeyError(f"Unknown provider '{provider_type}'. Available: {list(_REGISTRY)}")
    return _REGISTRY[provider_type](model_config)
