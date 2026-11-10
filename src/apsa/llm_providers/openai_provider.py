import os
import time
import logging
from typing import Dict, Any
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type

try:
    import openai
    _OPENAI_RETRY_EXCEPTIONS = (openai.APIConnectionError, openai.RateLimitError, openai.InternalServerError)
    HAS_OPENAI = True
except ImportError:
    openai = None
    _OPENAI_RETRY_EXCEPTIONS = (Exception,)
    HAS_OPENAI = False

from .base import BaseLLMProvider, GenerationResult
from .exceptions import ConfigurationError, GenerationError

logger = logging.getLogger(__name__)

class OpenAIProvider(BaseLLMProvider):
    def __init__(self, model_name: str):
        super().__init__(model_name)
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ConfigurationError(
                "OPENAI_API_KEY environment variable is not set. "
                "Cannot initialize OpenAIProvider."
            )
        
        if not HAS_OPENAI:
            raise ConfigurationError(
                "openai is not installed. "
                "Install it with: pip install 'apsa[openai]'"
            )

        self.client = openai.OpenAI(api_key=api_key)

    @retry(
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type(_OPENAI_RETRY_EXCEPTIONS),
        reraise=True
    )
    def _generate_with_retry(self, prompt: str, configuration: Dict[str, Any]):
        # Map generic configuration to OpenAI's completion parameters
        kwargs = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": configuration.get("temperature", 0.0),
        }
        
        if "max_tokens" in configuration:
            kwargs["max_tokens"] = configuration["max_tokens"]
            
        if "top_p" in configuration:
            kwargs["top_p"] = configuration["top_p"]
            
        if "seed" in configuration:
            # support deterministic settings if provided
            kwargs["seed"] = configuration["seed"]

        return self.client.chat.completions.create(**kwargs)

    def generate(self, prompt: str, configuration: Dict[str, Any]) -> GenerationResult:
        start_time = time.time()
        
        try:
            response = self._generate_with_retry(prompt, configuration)
            output = response.choices[0].message.content or ""
            
            input_tokens = None
            output_tokens = None
            if response.usage:
                input_tokens = response.usage.prompt_tokens
                output_tokens = response.usage.completion_tokens
                
        except Exception as e:
            logger.error(f"Generation failed for {self.model_name}: {str(e)}")
            raise GenerationError(f"Failed to generate output: {str(e)}") from e
            
        latency = time.time() - start_time
        
        return GenerationResult(
            model_name=self.model_name,
            prompt=prompt,
            output=output,
            latency=latency,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            generation_configuration=configuration
        )
