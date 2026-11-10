"""Pydantic model for the ExperimentRun JSONL record schema.

Matches the JSON schema specified in research_methodology.md §14,
extended with additional runtime fields defined in software_architecture.md §6.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class GenerationConfigSnapshot(BaseModel):
    temperature: float
    top_p: float
    max_tokens: int
    seed: int


class InputDistanceMetrics(BaseModel):
    lexical_char_levenshtein: float
    lexical_word_levenshtein: float
    lexical_char_normalized: float | None = None
    lexical_word_normalized: float | None = None
    lexical_jaccard_bigram: float | None = None
    syntactic_tree_edit_distance: float | None = None
    semantic_cosine_distance: float


class OutputDistanceMetrics(BaseModel):
    textual_levenshtein: float
    rouge_1_f1: float
    rouge_2_f1: float
    rouge_l_f1: float
    bleu_score: float
    token_jaccard: float
    semantic_bertscore_f1_disparity: float | None = None
    semantic_embedding_cosine: float
    llm_judge_score_delta: float | None = None


class FunctionalMetrics(BaseModel):
    applicable: bool
    original_pass: bool
    perturbed_pass: bool
    functional_failure: bool


class EpsilonBudgetUsed(BaseModel):
    lexical_char_normalized: float
    semantic_cosine: float
    lexical_word_normalized: float | None = None


class ExperimentRun(BaseModel):
    """Immutable record for a single paired-comparison inference run."""

    # Identity
    experiment_id: str
    run_id: str
    timestamp: datetime
    condition: str   # "baseline" | "random_control" | "treatment"

    # Provenance
    model_name: str
    task_category: str
    perturbation_type: str
    dataset_item_id: str

    # Generation config snapshot
    generation_config: GenerationConfigSnapshot

    # Prompts
    original_prompt: str
    perturbed_prompt: str

    # Raw outputs
    original_output: str
    perturbed_output: str
    original_token_count: int
    perturbed_token_count: int

    # Distance metrics
    input_distance: InputDistanceMetrics
    output_distance: OutputDistanceMetrics
    functional_metrics: FunctionalMetrics

    # Composite scores
    composite_output_divergence: float
    sensitivity_coefficient: float | None

    # Runtime metadata
    original_latency_ms: float
    perturbed_latency_ms: float
    epsilon_budget_used: EpsilonBudgetUsed
    perturbation_id: str | None = None
    perturbation_metadata: dict[str, Any] = Field(default_factory=dict)
    semantic_risk_level: str | None = None
    semantic_risk_reasons: list[str] = Field(default_factory=list)
    sensitivity_unavailable_reason: str | None = None


class ExperimentFailure(BaseModel):
    """Traceable record for a trial that did not produce a complete result."""

    experiment_id: str
    run_id: str
    timestamp: datetime
    model_name: str
    task_category: str
    perturbation_type: str
    dataset_item_id: str
    error_type: str
    error_message: str
