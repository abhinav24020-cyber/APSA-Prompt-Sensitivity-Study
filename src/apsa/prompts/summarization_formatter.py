"""Prompt formatter for summarization tasks."""

from apsa.data.base_dataset import DatasetItem
from .base_formatter import BaseFormatter, PromptRecord


class SummarizationFormatter(BaseFormatter):
    """Formats CNN/DailyMail / XSum items into summarization prompts."""

    def format(
        self,
        item: DatasetItem,
        system_prompt: str = BaseFormatter.DEFAULT_SYSTEM_PROMPT,
    ) -> PromptRecord:
        prompt = (
            "Summarize the following article concisely in 2-3 sentences.\n\n"
            f"Article:\n{item.input_text}\n\n"
            "Summary:"
        )
        return PromptRecord(
            original_prompt=prompt,
            system_prompt=system_prompt,
            task_category=item.task_category.value,
            dataset_item_id=item.id,
        )
