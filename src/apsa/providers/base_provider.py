"""Abstract base class for all LLM provider backends."""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class Message:
    """A single message in a chat conversation."""
    role: str        # "system" | "user" | "assistant"
    content: str


@dataclass
class GenerationConfig:
    """Frozen generation parameters for a single inference call."""
    temperature: float
    top_p: float
    max_tokens: int
    seed: int


@dataclass
class GenerationResult:
    """The result of a single generation call."""
    output_text: str
    model_name: str
    gen_config: GenerationConfig
    token_count: int
    latency_ms: float


class BaseLLMProvider(ABC):
    """Uniform interface over all LLM backends.

    All provider-specific logic (authentication, retries, device
    placement) lives exclusively within concrete subclasses.
    API keys are NEVER read from config files; always from environment
    variables whose names are declared in the model config YAML.
    """

    @abstractmethod
    def generate(
        self,
        messages: list[Message],
        config: GenerationConfig,
    ) -> GenerationResult:
        """Run inference and return a :class:`GenerationResult`."""
        ...

    @abstractmethod
    def get_model_id(self) -> str:
        """Return the canonical model identifier string."""
        ...

    @abstractmethod
    def count_tokens(self, text: str) -> int:
        """Return the token count for the given text string."""
        ...
