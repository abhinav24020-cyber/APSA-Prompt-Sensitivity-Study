import os
import time
import logging
from typing import Dict, Any
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type

from .base import BaseLLMProvider, GenerationResult
from .exceptions import ConfigurationError, GenerationError

logger = logging.getLogger(__name__)

class GeminiProvider(BaseLLMProvider):
    def __init__(self, model_name: str):
        super().__init__(model_name)
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ConfigurationError(
                "GEMINI_API_KEY environment variable is not set. "
                "Cannot initialize GeminiProvider."
            )
        
        try:
            import google.generativeai as genai
            self.genai = genai
        except ImportError as e:
            raise ConfigurationError(
                "google-generativeai is not installed. "
                "Install it with: pip install 'apsa[gemini]'"
            ) from e

        self.genai.configure(api_key=api_key)
        self.model = self.genai.GenerativeModel(self.model_name)

    @retry(
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type(Exception),
        reraise=True
    )
    def _generate_with_retry(self, prompt: str, generation_config: Any):
        return self.model.generate_content(
            prompt,
            generation_config=generation_config
        )

    def generate(self, prompt: str, configuration: Dict[str, Any]) -> GenerationResult:
        start_time = time.time()
        
        # Map generic configuration to Gemini's GenerationConfig
        gen_config = self.genai.GenerationConfig(
            temperature=configuration.get("temperature", 0.0),
            max_output_tokens=configuration.get("max_tokens", 1024),
            top_p=configuration.get("top_p"),
            top_k=configuration.get("top_k"),
        )
        
        try:
            response = self._generate_with_retry(prompt, gen_config)
            output = response.text
            
            input_tokens = None
            output_tokens = None
            finish_reason = None
            if hasattr(response, 'usage_metadata') and response.usage_metadata:
                input_tokens = response.usage_metadata.prompt_token_count
                output_tokens = response.usage_metadata.candidates_token_count
            candidates = getattr(response, "candidates", None)
            if candidates:
                reason = getattr(candidates[0], "finish_reason", None)
                finish_reason = str(reason) if reason is not None else None
                
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
            finish_reason=finish_reason,
            generation_configuration=configuration
        )
