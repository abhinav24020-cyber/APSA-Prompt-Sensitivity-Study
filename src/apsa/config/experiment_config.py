"""Top-level ExperimentConfig aggregating all sub-configurations."""

from pydantic import BaseModel
from .schema import (
    GenerationConfig,
    EpsilonBudget,
    MetricWeights,
    CompositeInputWeights,
    ModelConfig,
    DatasetConfig,
    PerturbationConfig,
    StorageConfig,
    JudgeModelConfig,
)


class ExperimentMetadata(BaseModel):
    name: str = "adversarial_prompt_sensitivity"
    description: str = ""
    seed: int = 42
    max_workers: int = 4


class ExperimentConfig(BaseModel):
    """Complete, fully-resolved experiment configuration.

    Loaded and validated by :func:`apsa.config.loader.load_config`.
    """
    experiment: ExperimentMetadata
    generation: GenerationConfig
    epsilon_budget: EpsilonBudget
    metric_weights: MetricWeights
    composite_input_weights: CompositeInputWeights
    datasets: list[DatasetConfig]
    models: list[ModelConfig]
    perturbations: list[PerturbationConfig]
    system_prompt: str
    storage: StorageConfig
    judge_model: JudgeModelConfig
