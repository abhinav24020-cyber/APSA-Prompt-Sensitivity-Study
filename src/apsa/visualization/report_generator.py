"""Assembles all figures and statistical tables into a self-contained HTML report."""

from pathlib import Path


class ReportGenerator:
    """Generate a jinja2-rendered HTML report from analysis results and figures."""

    def __init__(self, template_dir: Path | None = None) -> None:
        # TODO: configure jinja2 Environment
        pass

    def generate(self, results_dir: Path, output_path: Path) -> None:
        # TODO: load analysis JSON + figure paths; render HTML template
        raise NotImplementedError
