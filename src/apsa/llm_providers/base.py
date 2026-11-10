import time
import uuid
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

class GenerationResult(BaseModel):
    """Result of a generation from an LLM provider."""
    model_name: str
    prompt: str
    output: str
    latency: float
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    finish_reason: Optional[str] = None
    timestamp: float = Field(default_factory=time.time)
    run_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    generation_configuration: Dict[str, Any]

def load_env_file(env_path: Optional[str] = None) -> None:
    """Lightweight .env loader that populates os.environ without requiring external dependencies."""
    import os
    from pathlib import Path
    
    if env_path:
        candidates = [Path(env_path)]
    else:
        candidates = [
            Path.cwd() / ".env",
            Path(__file__).resolve().parent.parent.parent.parent / ".env",
        ]
        
    for p in candidates:
        if p.is_file():
            try:
                with open(p, "r", encoding="utf-8-sig") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            k, v = line.split("=", 1)
                            k, v = k.strip(), v.strip().strip("'\"")
                            if k and k not in os.environ:
                                os.environ[k] = v
                break
            except Exception:
                pass


class BaseLLMProvider(ABC):
    """Abstract base class for all LLM providers."""
    
    def __init__(self, model_name: str):
        self.model_name = model_name
        load_env_file()

    @abstractmethod
    def generate(self, prompt: str, configuration: Dict[str, Any]) -> GenerationResult:
        """
        Generate output from the model.
        
        Args:
            prompt (str): The input text to the model.
            configuration (Dict[str, Any]): Generation parameters (temperature, max_tokens, etc.)
            
        Returns:
            GenerationResult: The generated output along with metadata.
        """
        pass
