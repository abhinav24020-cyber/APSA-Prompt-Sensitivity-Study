class LLMProviderError(Exception):
    """Base class for all LLM provider exceptions."""

class ConfigurationError(LLMProviderError):
    """Raised when there is an issue with the provider configuration (e.g., missing API keys)."""

class GenerationError(LLMProviderError):
    """Raised when model generation fails after retries."""


class RateLimitError(GenerationError):
    """Raised when a provider rejects a request because of rate limits."""

    def __init__(self, message: str, retry_after: float | None = None) -> None:
        super().__init__(message)
        self.retry_after = retry_after
