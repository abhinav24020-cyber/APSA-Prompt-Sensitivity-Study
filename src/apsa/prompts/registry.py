"""Prompt formatter registry."""

from apsa.config.schema import TaskCategory
from .base_formatter import BaseFormatter
from .reasoning_formatter import ReasoningFormatter
from .code_formatter import CodeFormatter
from .qa_formatter import QAFormatter
from .summarization_formatter import SummarizationFormatter

_REGISTRY: dict[TaskCategory, type[BaseFormatter]] = {
    TaskCategory.MATHEMATICAL_REASONING: ReasoningFormatter,
    TaskCategory.LOGICAL_REASONING:        ReasoningFormatter,
    TaskCategory.CODE_GENERATION:        CodeFormatter,
    TaskCategory.QUESTION_ANSWERING:     QAFormatter,
    TaskCategory.CLOSED_QA_EXTRACTION:   QAFormatter,
    TaskCategory.SUMMARIZATION:          SummarizationFormatter,
    TaskCategory.CLASSIFICATION:         QAFormatter,
}


def get_formatter(task_category: TaskCategory) -> BaseFormatter:
    """Return an instantiated formatter for the given task category."""
    if task_category not in _REGISTRY:
        # Default fallback to QAFormatter
        return QAFormatter()
    return _REGISTRY[task_category]()
