import csv

import pytest

from experiments.pilot_experiment import redact_secrets, sample_dataset


def test_sample_dataset_respects_per_category_limit(tmp_path):
    data_path = tmp_path / "prompts.csv"
    rows = [
        {
            "prompt_id": f"{category}-{index}",
            "task_category": category,
            "original_prompt": f"Prompt {index}",
        }
        for category in ("alpha", "beta")
        for index in range(4)
    ]
    with data_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    sampled = sample_dataset(data_path, num_categories=2, prompts_per_category=2)

    assert len(sampled) == 4
    assert [row["prompt_id"] for row in sampled] == [
        "alpha-0",
        "alpha-1",
        "beta-0",
        "beta-1",
    ]


def test_sample_dataset_rejects_non_positive_category_limit(tmp_path):
    data_path = tmp_path / "prompts.csv"
    data_path.write_text("prompt_id,task_category,original_prompt\n", encoding="utf-8")

    with pytest.raises(ValueError, match="prompts_per_category"):
        sample_dataset(data_path, num_categories=2, prompts_per_category=0)


def test_redact_secrets_preserves_safe_model_configuration():
    assert redact_secrets({
        "provider": "groq",
        "max_tokens": 1024,
        "GROQ_API_KEY": "secret-value",
        "nested": {"client_secret": "other-secret"},
    }) == {
        "provider": "groq",
        "max_tokens": 1024,
        "GROQ_API_KEY": "[REDACTED]",
        "nested": {"client_secret": "[REDACTED]"},
    }
