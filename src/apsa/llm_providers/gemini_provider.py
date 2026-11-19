"""Google Gemini / Gemma provider.

Uses the current ``google-genai`` SDK when installed and falls back to the deprecated
``google-generativeai`` SDK otherwise. Rate-limit (HTTP 429) responses are raised as
``RateLimitError`` immediately, with the provider-suggested delay, so the caller decides
whether to wait; transient server errors (500/503) are retried with backoff.
"""

import logging
import os
import time
from typing import Any, Dict

from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential

from .base import BaseLLMProvider, GenerationResult
from .exceptions import (
    ConfigurationError,
    GenerationError,
    RateLimitError,
    classify_rate_limit_scope,
    parse_retry_after_text,
)

logger = logging.getLogger(__name__)


def _is_rate_limit(error: Exception) -> bool:
    code = getattr(error, "code", None) or getattr(error, "status_code", None)
    text = str(error)
    return code == 429 or "RESOURCE_EXHAUSTED" in text or text.startswith("429")


def _is_transient(error: Exception) -> bool:
    if _is_rate_limit(error):
        return False
    code = getattr(error, "code", None) or getattr(error, "status_code", None)
    text = str(error)
    return code in (500, 502, 503, 504) or "UNAVAILABLE" in text or "INTERNAL" in text


class GeminiProvider(BaseLLMProvider):
    def __init__(self, model_name: str):
        super().__init__(model_name)
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ConfigurationError(
                "GEMINI_API_KEY environment variable is not set. "
                "Cannot initialize GeminiProvider."
            )
        self._sdk = None
        try:
            from google import genai
            from google.genai import types

            self._client = genai.Client(
                api_key=api_key,
                http_options=types.HttpOptions(timeout=90_000),  # milliseconds
            )
            self._types = types
            self._sdk = "google-genai"
        except ImportError:
            try:
                import google.generativeai as legacy_genai
            except ImportError as e:
                raise ConfigurationError(
                    "Neither google-genai nor google-generativeai is installed. "
                    "Install it with: pip install google-genai"
                ) from e
            legacy_genai.configure(api_key=api_key)
            self.genai = legacy_genai
            self._sdk = "google-generativeai"

    @retry(
        wait=wait_exponential(multiplier=2, min=5, max=60),
        stop=stop_after_attempt(5),
        retry=retry_if_exception(_is_transient),
        reraise=True,
    )
    def _call(self, prompt: str, configuration: Dict[str, Any]):
        if self._sdk == "google-genai":
            config_kwargs: Dict[str, Any] = {
                "temperature": configuration.get("temperature", 0.0),
                "max_output_tokens": configuration.get("max_tokens", 1024),
            }
            if configuration.get("top_p") is not None:
                config_kwargs["top_p"] = configuration["top_p"]
            if configuration.get("seed") is not None:
                config_kwargs["seed"] = configuration["seed"]
            if configuration.get("system_prompt"):
                config_kwargs["system_instruction"] = configuration["system_prompt"]
            config_kwargs["automatic_function_calling"] = (
                self._types.AutomaticFunctionCallingConfig(disable=True)
            )
            return self._client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=self._types.GenerateContentConfig(**config_kwargs),
            )
        model = self.genai.GenerativeModel(
            self.model_name,
            system_instruction=configuration.get("system_prompt") or None,
        )
        gen_config = self.genai.GenerationConfig(
            temperature=configuration.get("temperature", 0.0),
            max_output_tokens=configuration.get("max_tokens", 1024),
            top_p=configuration.get("top_p"),
        )
        return model.generate_content(prompt, generation_config=gen_config)

    def generate(self, prompt: str, configuration: Dict[str, Any]) -> GenerationResult:
        start_time = time.time()
        try:
            response = self._call(prompt, configuration)
        except Exception as e:  # noqa: BLE001 - classify provider errors
            if _is_rate_limit(e):
                text = str(e)
                raise RateLimitError(
                    f"Gemini rate limit (429): {text[:500]}",
                    retry_after=parse_retry_after_text(text),
                    scope=classify_rate_limit_scope(text),
                ) from e
            logger.error(f"Generation failed for {self.model_name}: {str(e)[:300]}")
            raise GenerationError(f"Failed to generate output: {str(e)[:500]}") from e

        try:
            output = response.text or ""
        except Exception:  # noqa: BLE001 - blocked/empty candidates
            output = ""

        input_tokens = None
        output_tokens = None
        finish_reason = None
        usage = getattr(response, "usage_metadata", None)
        if usage:
            input_tokens = getattr(usage, "prompt_token_count", None)
            output_tokens = getattr(usage, "candidates_token_count", None)
        candidates = getattr(response, "candidates", None)
        if candidates:
            reason = getattr(candidates[0], "finish_reason", None)
            if reason is not None:
                finish_reason = getattr(reason, "name", None) or str(reason)

        return GenerationResult(
            model_name=self.model_name,
            prompt=prompt,
            output=output,
            latency=time.time() - start_time,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            finish_reason=finish_reason,
            generation_configuration=configuration,
        )
