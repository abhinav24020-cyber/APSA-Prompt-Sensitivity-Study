from typing import Dict, Any

from .base import BaseLLMProvider
from .exceptions import ConfigurationError
from .gemini_provider import GeminiProvider
from .openai_provider import OpenAIProvider
from .groq_provider import GroqProvider
from .mock_provider import MockProvider

class LLMProviderFactory:
    """Factory to create LLM providers based on the configuration."""
    
    _PROVIDERS = {
        "gemini": GeminiProvider,
        "openai": OpenAIProvider,
        "groq": GroqProvider,
        "mock": MockProvider,
    }

    @classmethod
    def create(cls, provider_name: str, model_name: str) -> BaseLLMProvider:
        """
        Create and return an instance of the requested LLM provider.
        
        Args:
            provider_name (str): The name of the provider (e.g., 'gemini', 'openai').
            model_name (str): The model identifier for the provider.
            
        Returns:
            BaseLLMProvider: The instantiated provider.
            
        Raises:
            ConfigurationError: If the provider is unknown or missing credentials.
        """
        provider_name = provider_name.lower()
        if provider_name not in cls._PROVIDERS:
            raise ConfigurationError(
                f"Unknown provider '{provider_name}'. "
                f"Supported providers are: {list(cls._PROVIDERS.keys())}"
            )
            
        provider_class = cls._PROVIDERS[provider_name]
        return provider_class(model_name)
