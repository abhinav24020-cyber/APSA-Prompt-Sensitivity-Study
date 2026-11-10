"""Prompt formatter for mathematical and logical reasoning tasks."""

from apsa.data.base_dataset import DatasetItem
from .base_formatter import BaseFormatter, PromptRecord


class ReasoningFormatter(BaseFormatter):
    """Formats GSM8K / MATH items into chain-of-thought prompts."""

    def format(
        self,
        item: DatasetItem,
        system_prompt: str = BaseFormatter.DEFAULT_SYSTEM_PROMPT,
    ) -> PromptRecord:
        prompt = (
            "Solve the following math problem step by step.\n\n"
            f"Problem: {item.input_text}\n\n"
            "Show your reasoning clearly, then state the final answer on its own line "
            "in the format: #### <answer>"
        )
        return PromptRecord(
            original_prompt=prompt,
            system_prompt=system_prompt,
            task_category=item.task_category.value,
            dataset_item_id=item.id,
        )
