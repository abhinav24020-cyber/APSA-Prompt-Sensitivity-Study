"""Conservative exact-answer checks for the lightweight baseline pilot."""

import re
import string
from fractions import Fraction

_SUPPORTED_CATEGORIES = {
    "mathematical_reasoning",
    "logical_reasoning",
    "question_answering",
    "classification",
    "closed_qa_extraction",
}
_NUMBER_PATTERN = re.compile(r"-?\d+(?:,\d{3})*(?:/\d+|\.\d+)?")
_PREFIX_PATTERN = re.compile(
    r"^(?:(?:the\s+)?(?:final\s+)?answer\s*(?:is|:)|"
    r"(?:the\s+)?(?:predicted\s+)?(?:class|category|label)\s*(?:is|:))\s*",
    re.IGNORECASE,
)
_NUMERIC_SUFFIX_WORDS = {"cm", "hour", "hours", "km", "m", "pi", "trips", "x", "y"}


def _normalize(text: str) -> str:
    text = text.strip().casefold()
    text = re.sub(r"^```[\w-]*\s*|\s*```$", "", text)
    text = text.strip("*`_ \t\r\n")
    text = _PREFIX_PATTERN.sub("", text)
    text = text.strip()
    return text.translate(str.maketrans("", "", string.punctuation)).strip()


def evaluate_pilot_answer(
    output: str | None,
    expected_answer: str | None,
    task_category: str,
) -> bool | None:
    """Return correctness where a conservative reference-answer check applies."""
    if not output or not expected_answer or task_category not in _SUPPORTED_CATEGORIES:
        return None

    gold = _normalize(expected_answer)
    response = _normalize(output.splitlines()[-1])
    if not gold or not response:
        return False
    acceptable_answers = [gold]
    if "->" in expected_answer and ";" in expected_answer:
        acceptable_answers = [
            _normalize(answer)
            for answer in expected_answer.split(";")
            if _normalize(answer)
        ]

    if task_category in {"mathematical_reasoning", "logical_reasoning"}:
        gold_numbers = _NUMBER_PATTERN.findall(expected_answer)
        remaining_words = re.findall(
            r"[a-z]+",
            _NUMBER_PATTERN.sub("", expected_answer).casefold(),
        )
        if gold_numbers and all(
            word in _NUMERIC_SUFFIX_WORDS for word in remaining_words
        ):
            response_numbers = _NUMBER_PATTERN.findall(output)
            if response_numbers:
                gold_values = [
                    Fraction(number.replace(",", "")) for number in gold_numbers
                ]
                response_values = [
                    Fraction(number.replace(",", ""))
                    for number in response_numbers[-len(gold_values):]
                ]
                if len(response_values) != len(gold_values):
                    return False
                return all(
                    abs(float(expected) - float(actual)) <= 1e-4
                    for expected, actual in zip(gold_values, response_values)
                )
        elif task_category == "mathematical_reasoning":
            return None

    if task_category == "classification":
        return response == gold

    if any(response == answer for answer in acceptable_answers):
        return True

    # Short reference answers commonly occur inside a complete answer sentence.
    return any(
        f" {answer} " in f" {response} "
        for answer in acceptable_answers
    )
