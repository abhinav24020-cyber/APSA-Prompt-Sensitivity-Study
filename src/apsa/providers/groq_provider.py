"""LLM provider backend for Groq Cloud API."""

import os
import time
import logging
import requests
from apsa.config.schema import ModelConfig
from .base_provider import BaseLLMProvider, Message, GenerationConfig, GenerationResult

logger = logging.getLogger(__name__)


class GroqProvider(BaseLLMProvider):
    API_URL = "https://api.groq.com/openai/v1/chat/completions"

    def __init__(self, model_config: ModelConfig) -> None:
        self._config = model_config
        self._load_dotenv()
        api_key = os.environ.get(model_config.api_key_env_var) or os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise EnvironmentError(f"GROQ_API_KEY is not set.")
        self.api_key = api_key

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
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self._config.model_id,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "temperature": config.temperature,
            "max_tokens": config.max_tokens,
            "top_p": config.top_p,
        }

        start = time.time()
        resp = requests.post(self.API_URL, headers=headers, json=payload, timeout=60)
        latency_ms = (time.time() - start) * 1000.0

        if resp.status_code != 200:
            raise RuntimeError(f"Groq API error ({resp.status_code}): {resp.text}")

        data = resp.json()
        output_text = data["choices"][0]["message"]["content"] or ""
        token_count = data.get("usage", {}).get("completion_tokens", len(output_text.split()))

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
        return len(text.split())

