"""Trial scheduling: enumerate the Cartesian product of experiment conditions."""

from collections.abc import Iterator
from dataclasses import dataclass

from apsa.config.experiment_config import ExperimentConfig
from apsa.data.base_dataset import DatasetItem
from apsa.logging_.structured_logger import get_logger

logger = get_logger(__name__)


@dataclass
class TrialSpec:
    """Minimal specification of a single trial."""
    run_id: str
    item: DatasetItem
    model_config_path: str
    perturbation_type: str


class Scheduler:
    """Generates the ordered trial queue from the experiment config matrix."""

    def __init__(self, config: ExperimentConfig) -> None:
        self._config = config

    def generate(self, completed_run_ids: set[str]) -> Iterator[TrialSpec]:
        """Yield TrialSpec objects, skipping completed ones."""
        from apsa.data.registry import get_dataset

        seed = self._config.experiment.seed
        exp_name = self._config.experiment.name

        for ds_config in self._config.datasets:
            logger.info(
                f"Loading dataset: {ds_config.name} (split={ds_config.split}, n={ds_config.sample_size})"
            )
            try:
                dataset = get_dataset(ds_config.name)
                items = dataset.load(
                    split=ds_config.split,
                    sample_size=ds_config.sample_size,
                    seed=seed,
                )
            except Exception as e:
                logger.error(f"Failed to load dataset '{ds_config.name}': {e}")
                continue

            for model_cfg in self._config.models:
                for pert_cfg in self._config.perturbations:
                    for item in items:
                        run_id = (
                            f"{exp_name}"
                            f"__{model_cfg.model_id}"
                            f"__{pert_cfg.type}"
                            f"__{item.id}"
                        )
                        if run_id in completed_run_ids:
                            logger.debug(f"Skipping completed trial: {run_id}")
                            continue
                        yield TrialSpec(
                            run_id=run_id,
                            item=item,
                            model_config_path=model_cfg.model_id,
                            perturbation_type=pert_cfg.type,
                        )
