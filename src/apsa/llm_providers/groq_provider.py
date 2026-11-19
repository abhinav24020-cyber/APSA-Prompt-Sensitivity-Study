import logging
import os
import time
from typing import Any

import requests
from tenacity import (
    retry,
    retry_if_exception_type,
    retry_if_not_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from .base import BaseLLMProvider, GenerationResult
from .exceptions import (
    ConfigurationError,
    GenerationError,
    RateLimitError,
    classify_rate_limit_scope,
    parse_retry_after_text,
)

logger = logging.getLogger(__name__)

class GroqProvider(BaseLLMProvider):
    """Groq Cloud LLM Provider.
    
    Provides high-speed inference for open models (Llama 3.1/3.3, Gemma 2, etc.)
    with a completely free tier (no credit card required).
    Get free API keys at: https://console.groq.com/keys
    """
    
    API_URL = "https://api.groq.com/openai/v1/chat/completions"

    def __init__(self, model_name: str):
        super().__init__(model_name)
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ConfigurationError(
                "GROQ_API_KEY environment variable is not set. "
                "Get a free API key at https://console.groq.com/keys "
                "and set it in your .env file."
            )
        self.api_key = api_key

    @retry(
        wait=wait_exponential(multiplier=2, min=5, max=30),
        stop=stop_after_attempt(5),
        retry=(
            retry_if_exception_type(GenerationError)
            & retry_if_not_exception_type(RateLimitError)
        ),
        reraise=True
    )
    def _generate_with_retry(self, prompt: str, configuration: dict[str, Any]) -> dict[str, Any]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        max_tokens = configuration.get("max_tokens", 256)
        messages = []
        if configuration.get("system_prompt"):
            messages.append({"role": "system", "content": configuration["system_prompt"]})
        messages.append({"role": "user", "content": prompt})
        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": configuration.get("temperature", 0.0),
            "max_tokens": max_tokens,
        }
        if "top_p" in configuration:
            payload["top_p"] = configuration["top_p"]
        if "seed" in configuration:
            payload["seed"] = configuration["seed"]
        if configuration.get("reasoning_effort"):
            payload["reasoning_effort"] = configuration["reasoning_effort"]

        response = requests.post(self.API_URL, headers=headers, json=payload, timeout=60)
        if response.status_code == 429:
            retry_after = None
            try:
                retry_after = float(response.headers["retry-after"])
            except (KeyError, TypeError, ValueError):
                retry_after = parse_retry_after_text(response.text)
            scope = classify_rate_limit_scope(response.text)
            wait_message = (
                f" Retry after {retry_after:g} seconds."
                if retry_after is not None
                else ""
            )
            logger.warning(
                "Groq rate limit (429); raising RateLimitError without provider-level "
                "retry (the caller decides whether to wait).%s",
                wait_message,
            )
            raise RateLimitError(
                f"Groq rate limit (429): {response.text}{wait_message}",
                retry_after=retry_after,
                scope=scope,
            )

        if response.status_code != 200:
            raise GenerationError(f"Groq API error (status {response.status_code}): {response.text}")
        return response.json()

    def generate(self, prompt: str, configuration: dict[str, Any]) -> GenerationResult:
        start_time = time.time()
        try:
            data = self._generate_with_retry(prompt, configuration)
            output = data["choices"][0]["message"]["content"] or ""
            finish_reason = data["choices"][0].get("finish_reason")
            latency = time.time() - start_time
            
            usage = data.get("usage", {})
            input_tokens = usage.get("prompt_tokens", len(prompt.split()))
            output_tokens = usage.get("completion_tokens", len(output.split()))

            return GenerationResult(
                model_name=self.model_name,
                prompt=prompt,
                output=output,
                latency=latency,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                finish_reason=finish_reason,
                generation_configuration=configuration
            )
        except RateLimitError:
            raise
        except Exception as e:
            logger.error(f"Failed to generate text from Groq ({self.model_name}): {e}")
            raise GenerationError(f"Generation failed: {e}") from e
