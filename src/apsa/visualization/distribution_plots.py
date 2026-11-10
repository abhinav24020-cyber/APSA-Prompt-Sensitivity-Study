"""Violin / box plots of sensitivity coefficient distributions."""

from pathlib import Path


class DistributionPlotter:
    """Generate violin plots of S per model and per task category."""

    def plot(self, data, output_path: Path) -> None:
        # TODO: implement using seaborn.violinplot
        raise NotImplementedError
