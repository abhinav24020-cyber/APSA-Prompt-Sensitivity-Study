"""CLI entry point: run a complete adversarial prompt sensitivity experiment.

Usage:
    python scripts/run_experiment.py --config config/experiments/pilot_small.yaml
    python scripts/run_experiment.py --config config/experiments/full_experiment.yaml --resume
"""

import click
from pathlib import Path

from apsa.config.loader import load_config
from apsa.execution.engine import ExperimentEngine


@click.command()
@click.option("--config", required=True, type=click.Path(exists=True, path_type=Path),
              help="Path to the experiment YAML configuration file.")
@click.option("--resume", is_flag=True, default=False,
              help="Resume from an existing checkpoint instead of starting fresh.")
def main(config: Path, resume: bool) -> None:
    """Run the adversarial prompt sensitivity experiment."""
    experiment_config = load_config(config)
    engine = ExperimentEngine(experiment_config)
    engine.run()


if __name__ == "__main__":
    main()
