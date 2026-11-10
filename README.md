# Adversarial Prompt Sensitivity Analysis (APSA)

> *How much can a Large Language Model's output change when its input prompt is modified by
> minimal, controlled perturbations?*

This repository implements an experimental framework for studying LLM output changes under prompt
perturbations. Implementation and mock-test results are not empirical findings. A current-code live
pilot was attempted but stopped at the provider's rate limit; see the work summary for its scope.

## Project Structure

See [`docs/software_architecture.md`](docs/software_architecture.md) for the full architecture.
See [`docs/research_methodology.md`](docs/research_methodology.md) for the research methodology.
See [`docs/pilot_study_workflow.md`](docs/pilot_study_workflow.md) for the pilot procedure, raw output format, analysis, and interpretation limits.
See [`docs/work_completed_summary.md`](docs/work_completed_summary.md) for completed work, verification, existing pilot evidence, and remaining Phase 1–10 requirements.
See [`docs/project_work_phases_1_to_10_run_guide.md`](docs/project_work_phases_1_to_10_run_guide.md) for a consolidated Phase 1–10 implementation walkthrough and professor-demo run instructions.
See [`data/dataset_card.md`](data/dataset_card.md) and [`data/baseline_dataset_audit.json`](data/baseline_dataset_audit.json) for dataset scope, sampling, structural audit, and reference-answer review limits.

## Setup

```bash
# 1. Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 2. Install core dependencies
pip install -e ".[huggingface,gemini,dev]"

# 3. Configure API keys
cp .env.example .env
# Edit .env and fill in your credentials

# 4. Verify environment
python scripts/verify_environment.py
```

## Running Experiments

```bash
# Demo run (offline mock; no API requests)
python experiments/pilot_experiment.py --mock --models openai/gpt-oss-20b \
  --prompts-per-category 1 --repetitions 1 --control-repetitions 1 \
  --output-dir results/demo

# Modular experiment runner (different schema and analysis path)
python scripts/run_experiment.py --config config/experiments/pilot_small.yaml

```

On Windows, use `.\.venv\Scripts\python.exe` in place of `python`. The lightweight pilot writes
each run to `results/demo/mock/<experiment-id>/`; use
`experiments/evaluate_experiment.py` to generate Phase 9/10 analysis for its `raw_results.jsonl`.
See [`docs/pilot_study_workflow.md`](docs/pilot_study_workflow.md) for copy/paste PowerShell
commands and interpretation guidance. Do not treat mock output as live-model evidence.

## Analysis & Visualization

```bash
# Run statistical analysis
python scripts/run_analysis.py --experiment-id apsa_20260911_abc12def_42

# Generate all figures and HTML report
python scripts/run_visualization.py --experiment-id apsa_20260911_abc12def_42
```

## Testing

```bash
pytest tests/ -v --cov=src/apsa
```

## Security Note

API keys are NEVER stored in config files. Always use environment variables as defined in `.env.example`.
