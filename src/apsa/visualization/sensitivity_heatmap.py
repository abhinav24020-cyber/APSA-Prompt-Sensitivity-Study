"""Model x Perturbation-type heatmap of mean Sensitivity Coefficient S."""

from pathlib import Path


class SensitivityHeatmap:
    """Generate a heatmap of mean S values: rows=models, cols=perturbation types."""

    def plot(self, data, output_path: Path) -> None:
        # TODO: implement using seaborn.heatmap
        raise NotImplementedError
