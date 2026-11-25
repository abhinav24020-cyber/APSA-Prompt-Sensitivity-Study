# Run APSA prompt analysis

Open PowerShell in the repository root and use the project’s `.venv`. [Environment setup](../README.md#setup-verified-on-windows-10-python-312)

## Analyze a stored prompt

```powershell
.\.venv\Scripts\python.exe experiments\category_operators.py prompt --prompt-id LOGIC-010
```

This uses the five-model panel and a `0.10` input edit budget. To find a different prompt, use `--search "truth value"` in place of `--prompt-id LOGIC-010`. Add `--model gpt-oss-120b` for a single-model result, or `--target 0.20 --budget 0.10` to find the smallest eligible edit that reaches the target.

Open the Markdown report printed by the command in VS Code Preview. Stored `main_v1` reports go to `results/category_operator_prompts/main_v1/`. For `LOGIC-010`, expect **punctuation** to lead with **0.2891** mean excess output change. The report shows the exact edit, all ten operator rows, and whether the answer changed.

## Prepare a new prompt

```powershell
.\.venv\Scripts\python.exe experiments\category_operators.py prompt --text "Who wrote Pride and Prejudice?" --reference "Jane Austen"
```

APSA suggests a category and saves an unmeasured report and a review CSV in `results/category_operator_prompts/<prompt-id>/`. Use `--category question_answering` to confirm or override the category. For a measured result, complete the review CSV and follow **Measure after review** in the generated `report.md`. That section gives the commands for a separate live run.
