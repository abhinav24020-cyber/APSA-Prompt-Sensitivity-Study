"""Prompt formatter for code generation tasks."""

from apsa.data.base_dataset import DatasetItem
from .base_formatter import BaseFormatter, PromptRecord


class CodeFormatter(BaseFormatter):
    """Formats HumanEval / MBPP items into code-generation prompts."""

    def format(
        self,
        item: DatasetItem,
        system_prompt: str = BaseFormatter.DEFAULT_SYSTEM_PROMPT,
    ) -> PromptRecord:
        prompt = (
            "Complete the following Python function. "
            "Return only the implementation body — no explanations, no markdown.\n\n"
            f"{item.input_text}"
        )
        return PromptRecord(
            original_prompt=prompt,
            system_prompt=system_prompt,
            task_category=item.task_category.value,
            dataset_item_id=item.id,
        )
