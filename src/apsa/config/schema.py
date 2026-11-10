"""Pydantic schemas for all configuration objects."""

from __future__ import annotations

from enum import Enum
from typing import Any
from pydantic import BaseModel, Field


class TaskCategory(str, Enum):
    MATHEMATICAL_REASONING = "mathematical_reasoning"
    LOGICAL_REASONING = "logical_reasoning"
    QUESTION_ANSWERING = "question_answering"
    CLASSIFICATION = "classification"
    CODE_GENERATION = "code_generation"
    CLOSED_QA_EXTRACTION = "closed_qa_extraction"
    SUMMARIZATION = "summarization"


class GenerationConfig(BaseModel):
    temperature_deterministic: float = 0.0
    temperature_stochastic: float = 0.7
    top_p: float = 0.95
    max_tokens: int = 1024
    n_stochastic_repeats: int = 5
    seed: int = 42


class EpsilonBudget(BaseModel):
    lexical_char_normalized: float = 0.10
    lexical_word_normalized: float = 0.15
    semantic_cosine: float = 0.05
    syntactic_ted_normalized: float = 0.20


class MetricWeights(BaseModel):
    w1_textual: float = 0.33
    w2_semantic: float = 0.34
    w3_functional: float = 0.33
    eta: float = 1e-4


class CompositeInputWeights(BaseModel):
    alpha_lexical: float = 0.5
    beta_semantic: float = 0.5
    gamma_syntactic: float = 0.0


class ModelConfig(BaseModel):
    model_id: str
    display_name: str
    provider: str                        # "huggingface" | "gemini" | "openai"
    api_key_env_var: str
    context_window: int
    parameter_scale: str
    type: str
    tokenizer_id: str | None = None
    device: str = "auto"
    dtype: str = "bfloat16"
    vllm: bool = False


class DatasetConfig(BaseModel):
    name: str
    split: str = "test"
    sample_size: int | None = None


class PerturbationConfig(BaseModel):
    type: str
    params: dict[str, Any] = Field(default_factory=dict)


class StorageConfig(BaseModel):
    results_dir: str = "results"
    log_level: str = "INFO"


class JudgeModelConfig(BaseModel):
    provider: str
    model_id: str
