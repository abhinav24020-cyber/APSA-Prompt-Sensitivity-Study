"""CLI entry point: generate all plots and the HTML report.

Usage:
    python scripts/run_visualization.py --experiment-id apsa_20260911_abc12def_42
"""

import json
import click
from pathlib import Path


@click.command()
@click.option("--experiment-id", required=True, help="Experiment ID to visualise.")
@click.option("--results-dir", default="results", show_default=True,
              type=click.Path(path_type=Path))
def main(experiment_id: str, results_dir: Path) -> None:
    """Generate all visualizations and the HTML/Markdown report."""
    exp_dir = Path(results_dir) / experiment_id
    if not exp_dir.exists():
        candidates = list(Path(results_dir).glob(f"*{experiment_id}*"))
        if candidates:
            exp_dir = candidates[0]
        else:
            raise click.ClickException(f"Directory not found for experiment '{experiment_id}' in {results_dir}")

    summary_file = exp_dir / "analysis_summary.json"
    if not summary_file.exists():
        # Check if results.jsonl exists, and run analysis first
        results_file = exp_dir / "results.jsonl"
        if not results_file.exists():
            raise click.ClickException(f"No results.jsonl or analysis_summary.json found in {exp_dir}")
        print("analysis_summary.json not found, running analysis first...")
        from apsa.analysis.sensitivity import SensitivityRecord, SensitivityAnalyzer
        from apsa.storage.reader import ResultReader
        reader = ResultReader(results_file)
        records = [
            SensitivityRecord(
                experiment_id=r.experiment_id,
                model=r.model_name,
                task_category=r.task_category,
                prompt_id=r.dataset_item_id,
                perturbation_type=r.perturbation_type,
                d_input=r.epsilon_budget_used.lexical_char_normalized,
                d_semantic_input=r.epsilon_budget_used.semantic_cosine,
                d_output=r.composite_output_divergence,
            )
            for r in reader.stream()
        ]
        analyzer = SensitivityAnalyzer(records)
        summary = {
            "experiment_id": experiment_id,
            "total_records": len(records),
            "mean_output_deviation": round(analyzer.compute_statistical_aggregations()["mean"], 4),
            "highest_sensitivity_per_task": analyzer.highest_sensitivity_per_group("task_category"),
            "highest_sensitivity_per_perturbation": analyzer.highest_sensitivity_per_group("perturbation_type"),
            "highest_sensitivity_per_model": analyzer.highest_sensitivity_per_group("model"),
        }
    else:
        with open(summary_file, "r", encoding="utf-8") as f:
            summary = json.load(f)

    # 1. Generate Markdown Report
    md_content = f"""# APSA Experiment Report: {experiment_id}

## Executive Summary
- **Total Paired Trials Analyzed**: {summary.get('total_records', 'N/A')}
- **Mean Output Deviation ($D_{{out}}$)**: {summary.get('mean_output_deviation', 'N/A')}
- **95% Confidence Interval**: {summary.get('ci_95_output_deviation', 'N/A')}
- **Max Deviation under $\\epsilon \\le 0.10$**: {summary.get('max_deviation_under_budget_0_10', 'N/A')}

---

## Sensitivity by Task Category
| Task Category | Highest Sensitivity Coefficient |
|---|---|
"""
    for task, val in summary.get("highest_sensitivity_per_task", {}).items():
        md_content += f"| {task} | {val:.4f} |\n"

    md_content += """
## Sensitivity by Perturbation Type
| Perturbation Type | Highest Sensitivity Coefficient |
|---|---|
"""
    for pert, val in summary.get("highest_sensitivity_per_perturbation", {}).items():
        md_content += f"| {pert} | {val:.4f} |\n"

    md_content += """
## Sensitivity by Model
| Model | Highest Sensitivity Coefficient |
|---|---|
"""
    for m, val in summary.get("highest_sensitivity_per_model", {}).items():
        md_content += f"| {m} | {val:.4f} |\n"

    report_md = exp_dir / "report.md"
    report_md.write_text(md_content, encoding="utf-8")
    print(f"[OK] Markdown report generated: {report_md.resolve()}")

    # 2. Generate HTML Report
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>APSA Report - {experiment_id}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 40px; color: #24292e; }}
        h1 {{ border-bottom: 2px solid #eaecef; padding-bottom: 10px; }}
        h2 {{ margin-top: 30px; color: #0366d6; }}
        table {{ border-collapse: collapse; width: 100%; margin: 15px 0; }}
        th, td {{ border: 1px solid #dfe2e5; padding: 10px 14px; text-align: left; }}
        th {{ background: #f6f8fa; }}
        tr:nth-child(even) {{ background: #fafbfc; }}
        .badge {{ background: #e1f5fe; color: #0277bd; padding: 4px 8px; border-radius: 4px; font-weight: bold; }}
    </style>
</head>
<body>
    <h1>Adversarial Prompt Sensitivity Analysis Report</h1>
    <p><strong>Experiment ID:</strong> <span class="badge">{experiment_id}</span></p>
    <p><strong>Total Trials:</strong> {summary.get('total_records', 'N/A')}</p>
    <p><strong>Mean Output Deviation:</strong> {summary.get('mean_output_deviation', 'N/A')}</p>
    
    <h2>Sensitivity by Task Category</h2>
    <table>
        <tr><th>Task Category</th><th>Highest Sensitivity</th></tr>
        {''.join(f'<tr><td>{k}</td><td>{v:.4f}</td></tr>' for k, v in summary.get('highest_sensitivity_per_task', {}).items())}
    </table>

    <h2>Sensitivity by Perturbation Operator</h2>
    <table>
        <tr><th>Operator</th><th>Highest Sensitivity</th></tr>
        {''.join(f'<tr><td>{k}</td><td>{v:.4f}</td></tr>' for k, v in summary.get('highest_sensitivity_per_perturbation', {}).items())}
    </table>
</body>
</html>
"""
    report_html = exp_dir / "report.html"
    report_html.write_text(html_content, encoding="utf-8")
    print(f"[OK] HTML report generated: {report_html.resolve()}")


if __name__ == "__main__":
    main()
