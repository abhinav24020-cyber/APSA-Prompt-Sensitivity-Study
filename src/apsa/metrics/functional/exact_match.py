"""Exact Match failure indicator for math and QA tasks."""

import re
from dataclasses import dataclass


@dataclass
class ExactMatchResult:
    applicable: bool
    original_pass: bool
    perturbed_pass: bool
    functional_failure: bool


class ExactMatchEvaluator:
    """Extract and compare short-form answers from Y and Y'."""

    _APPLICABLE_CATEGORIES = {
        "mathematical_reasoning",
        "logical_reasoning",
        "question_answering",
        "closed_qa_extraction",
    }

    def evaluate(
        self,
        original_output: str,
        perturbed_output: str,
        gold_answer: str | None,
        task_category: str,
    ) -> ExactMatchResult:
        if gold_answer is None or task_category not in self._APPLICABLE_CATEGORIES:
            return ExactMatchResult(
                applicable=False,
                original_pass=False,
                perturbed_pass=False,
                functional_failure=False,
            )

        gold = self._normalize(self._extract_answer(gold_answer) or gold_answer)
        orig_ans = self._extract_answer(original_output)
        pert_ans = self._extract_answer(perturbed_output)

        orig_pass = self._normalize(orig_ans) == gold if orig_ans else False
        pert_pass = self._normalize(pert_ans) == gold if pert_ans else False

        return ExactMatchResult(
            applicable=True,
            original_pass=orig_pass,
            perturbed_pass=pert_pass,
            functional_failure=orig_pass and not pert_pass,
        )

    def _extract_answer(self, text: str) -> str | None:
        # GSM8K style: #### <answer>
        m = re.search(r'####\s*(.+)', text)
        if m:
            return m.group(1).strip()
        # "The answer is X" / "answer: X"
        m = re.search(r'(?:the answer is|answer\s*:)\s*([^\.\n]+)', text, re.IGNORECASE)
        if m:
            return m.group(1).strip()
        # Last number in text
        nums = re.findall(r'-?\d+(?:,\d{3})*(?:\.\d+)?', text)
        if nums:
            return nums[-1].replace(",", "")
        return None

    def _normalize(self, s: str) -> str:
        """Strip non-numeric characters for numeric comparison."""
        return re.sub(r'[^\d\.\-]', '', s).strip() if s else ""
