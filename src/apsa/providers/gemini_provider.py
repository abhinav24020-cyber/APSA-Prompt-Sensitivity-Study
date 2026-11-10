"""LLM provider backend for the Google Gemini API."""

import os
import time
import logging
from typing import Any

from apsa.config.schema import ModelConfig
from .base_provider import BaseLLMProvider, Message, GenerationConfig, GenerationResult

logger = logging.getLogger(__name__)


class GeminiProvider(BaseLLMProvider):
    """Wraps the google-generativeai SDK for the Gemini model family."""

    def __init__(self, model_config: ModelConfig) -> None:
        self._config = model_config
        self._load_dotenv()
        api_key = os.environ.get(model_config.api_key_env_var) or os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise EnvironmentError(
                f"Environment variable '{model_config.api_key_env_var}' is not set. "
                "Add it to your .env file."
            )
        try:
            import google.generativeai as genai
            self._genai = genai
        except ImportError as e:
            raise ImportError(
                "google-generativeai not installed. Run: pip install 'apsa[gemini]'"
            ) from e

        self._genai.configure(api_key=api_key)
        self._model = self._genai.GenerativeModel(model_config.model_id)

    @staticmethod
    def _load_dotenv() -> None:
        from pathlib import Path
        for candidate in [
            Path.cwd() / ".env",
            Path(__file__).resolve().parent.parent.parent.parent / ".env",
        ]:
            if candidate.is_file():
                with open(candidate, encoding="utf-8-sig") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            k, _, v = line.partition("=")
                            k, v = k.strip(), v.strip().strip("'\"")
                            if k and k not in os.environ:
                                os.environ[k] = v
                break

    def generate(self, messages: list[Message], config: GenerationConfig) -> GenerationResult:
        parts = []
        for msg in messages:
            if msg.role == "system":
                parts.append(f"System: {msg.content}")
            else:
                parts.append(msg.content)
        full_prompt = "\n\n".join(parts)

        gen_cfg = self._genai.GenerationConfig(
            temperature=config.temperature,
            max_output_tokens=config.max_tokens,
            top_p=config.top_p,
        )

        start_time = time.time()
        try:
            response = self._model.generate_content(full_prompt, generation_config=gen_cfg)
            output_text = response.text if hasattr(response, "text") and response.text else ""
        except Exception as e:
            logger.error(f"Gemini generate_content failed for {self._config.model_id}: {e}")
            raise
        latency_ms = (time.time() - start_time) * 1000.0

        token_count = len(output_text.split())
        if hasattr(response, "usage_metadata") and response.usage_metadata:
            token_count = response.usage_metadata.candidates_token_count or token_count

        return GenerationResult(
            output_text=output_text,
            model_name=self._config.model_id,
            gen_config=config,
            token_count=token_count,
            latency_ms=round(latency_ms, 2),
        )

    def get_model_id(self) -> str:
        return self._config.model_id

    def count_tokens(self, text: str) -> int:
        try:
            result = self._model.count_tokens(text)
            return result.total_tokens
        except Exception:
            return len(text.split())
