"""Core experiment orchestrator."""

import datetime
from pathlib import Path

from apsa.config.experiment_config import ExperimentConfig
from apsa.logging_.structured_logger import configure_logging, get_logger
from apsa.reproducibility.seed_manager import SeedManager
from apsa.storage.schema import ExperimentFailure
from apsa.storage.writer import ResultWriter

from .checkpoint import CheckpointManager
from .scheduler import Scheduler
from .trial import TrialRunner

logger = get_logger(__name__)


class ExperimentEngine:
    """Top-level orchestrator for an adversarial prompt sensitivity experiment."""

    def __init__(self, config: ExperimentConfig) -> None:
        self._config = config

    def run(self) -> None:
        """Execute the full experiment defined by the config."""
        date_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        experiment_id = f"{self._config.experiment.name}_{date_str}_{self._config.experiment.seed}"

        results_dir = Path(self._config.storage.results_dir)
        exp_dir = results_dir / experiment_id
        exp_dir.mkdir(parents=True, exist_ok=True)

        configure_logging(exp_dir, experiment_id, self._config.storage.log_level)
        logger.info(f"Experiment started: {experiment_id}")
        logger.info(f"Results directory: {exp_dir.resolve()}")

        SeedManager.set_global_seed(self._config.experiment.seed)

        checkpoint_path = exp_dir / "checkpoint.txt"
        checkpoint_mgr = CheckpointManager(checkpoint_path)
        completed = checkpoint_mgr.load_completed()
        if completed:
            logger.info(f"Resuming — {len(completed)} trials already completed.")

        output_path = exp_dir / "results.jsonl"
        writer = ResultWriter(output_path)

        model_index = {m.model_id: m for m in self._config.models}
        pert_index = {p.type: p for p in self._config.perturbations}

        scheduler = Scheduler(self._config)
        specs = list(scheduler.generate(completed))
        total = len(specs) + len(completed)
        logger.info(f"Trial queue: {len(specs)} to run, {len(completed)} already done (total={total})")

        trial_runner = TrialRunner(self._config)
        success_count = 0
        fail_count = 0

        for i, spec in enumerate(specs, 1):
            model_cfg = model_index.get(spec.model_config_path)
            pert_cfg = pert_index.get(spec.perturbation_type)

            if model_cfg is None:
                message = f"No model config found for id '{spec.model_config_path}'"
                writer.write_failure(
                    ExperimentFailure(
                        experiment_id=experiment_id,
                        run_id=spec.run_id,
                        timestamp=datetime.datetime.now(datetime.UTC),
                        model_name=spec.model_config_path,
                        task_category=spec.item.task_category.value,
                        perturbation_type=spec.perturbation_type,
                        dataset_item_id=spec.item.id,
                        error_type="ConfigurationError",
                        error_message=message,
                    )
                )
                logger.error(f"{message} — skipping {spec.run_id}")
                fail_count += 1
                continue
            if pert_cfg is None:
                message = f"No perturbation config found for type '{spec.perturbation_type}'"
                writer.write_failure(
                    ExperimentFailure(
                        experiment_id=experiment_id,
                        run_id=spec.run_id,
                        timestamp=datetime.datetime.now(datetime.UTC),
                        model_name=spec.model_config_path,
                        task_category=spec.item.task_category.value,
                        perturbation_type=spec.perturbation_type,
                        dataset_item_id=spec.item.id,
                        error_type="ConfigurationError",
                        error_message=message,
                    )
                )
                logger.error(f"{message} — skipping {spec.run_id}")
                fail_count += 1
                continue

            try:
                result = trial_runner.execute(
                    run_id=spec.run_id,
                    item=spec.item,
                    model_config=model_cfg,
                    perturbation_config=pert_cfg,
                )
                writer.write(result)
                checkpoint_mgr.mark_completed(spec.run_id)
                success_count += 1
                sensitivity = (
                    f"{result.sensitivity_coefficient:.4f}"
                    if result.sensitivity_coefficient is not None
                    else "NA"
                )
                logger.info(
                    f"[{i}/{len(specs)}] OK  S={sensitivity}  "
                    f"d_out={result.composite_output_divergence:.4f}  {spec.run_id}"
                )
            except Exception as exc:  # noqa: BLE001 - record each failed trial and continue the batch
                writer.write_failure(
                    ExperimentFailure(
                        experiment_id=experiment_id,
                        run_id=spec.run_id,
                        timestamp=datetime.datetime.now(datetime.UTC),
                        model_name=spec.model_config_path,
                        task_category=spec.item.task_category.value,
                        perturbation_type=spec.perturbation_type,
                        dataset_item_id=spec.item.id,
                        error_type=type(exc).__name__,
                        error_message=str(exc),
                    )
                )
                logger.error(
                    f"[{i}/{len(specs)}] FAILED: {spec.run_id} — {type(exc).__name__}: {exc}"
                )
                fail_count += 1

        logger.info(
            f"Experiment complete. Success={success_count}  Failed={fail_count}  "
            f"Results: {output_path.resolve()}"
        )
        print("\n============================================================")
        print("EXPERIMENT COMPLETE")
        print(f"Experiment ID: {experiment_id}")
        print(f"Total Trials:  {len(specs)}")
        print(f"Successful:    {success_count}")
        print(f"Failed:        {fail_count}")
        print(f"Results file:  {output_path.resolve()}")
        print("============================================================")
