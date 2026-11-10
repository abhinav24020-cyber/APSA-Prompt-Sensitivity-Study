"""Prompt formatter for question-answering tasks."""

from apsa.data.base_dataset import DatasetItem
from .base_formatter import BaseFormatter, PromptRecord


class QAFormatter(BaseFormatter):
    """Formats SQuAD-v2 / HotpotQA items into QA prompts."""

    def format(
        self,
        item: DatasetItem,
        system_prompt: str = BaseFormatter.DEFAULT_SYSTEM_PROMPT,
    ) -> PromptRecord:
        context = item.metadata.get("context", "")
        if context:
            prompt = (
                f"Context: {context}\n\n"
                f"Question: {item.input_text}\n\n"
                "Answer concisely based only on the context."
            )
        else:
            prompt = f"Question: {item.input_text}\n\nAnswer concisely."
        return PromptRecord(
            original_prompt=prompt,
            system_prompt=system_prompt,
            task_category=item.task_category.value,
            dataset_item_id=item.id,
        )
