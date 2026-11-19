"""Item-level answer key for the APSA main study (rule-based correctness).

Each scorable baseline item has an explicit, auditable rule: a list of regular
expressions that must all match (``require``) and a list that must not match
(``forbid``) inside a defined answer region of the model output.

Answer region (``scope``):
  * ``final`` - text after the last ``Final answer:`` marker (the study's system prompt
    asks for one); when the marker is absent, the whole output.
  * ``full``  - the whole output (used for multi-part answers whose components may be
    stated in the body).

All text is normalised first: lower-case, LaTeX ``\\frac{a}{b}`` -> ``a/b``, ``π`` ->
``pi``, unicode minus/arrows/dashes unified, markdown emphasis and ``$``/``\\`` removed,
thousands separators removed. These rules are heuristics written from the reference
answers before scoring; they are not human adjudication.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

_NUM = r"(?<![\d./])"
_END = r"(?![\d]|\.\d)"


@dataclass(frozen=True)
class AnswerRule:
    require: list[str]
    forbid: list[str] = field(default_factory=list)
    scope: str = "final"


def _label_rule(gold: str, others: list[str]) -> AnswerRule:
    return AnswerRule(
        require=[rf"\b{gold}\b"],
        forbid=[rf"\b{o}\b" for o in others],
    )


ANSWER_KEY: dict[str, AnswerRule] = {
    # --- classification (single label in the final answer) ---
    "CLASS-001": _label_rule("negative", ["positive", "neutral"]),
    "CLASS-002": _label_rule("business", ["sports", "technology", "politics"]),
    "CLASS-003": _label_rule(r"billing[_ ]issue",
                             [r"account[_ ]cancellation", r"product[_ ]inquiry",
                              r"general[_ ]feedback"]),
    "CLASS-004": AnswerRule(require=[r"\bspam\b"], forbid=[r"\bham\b", r"not spam"]),
    "CLASS-005": _label_rule("anger", ["joy", "fear", "sadness", "surprise"]),
    "CLASS-006": _label_rule("spanish", ["portuguese", "italian", "english", "french"]),
    "CLASS-007": _label_rule("entailment", ["contradiction", "neutral"]),
    "CLASS-008": _label_rule("critical", ["high", "medium", "low"]),
    "CLASS-009": _label_rule("science fiction", ["fantasy", "historical fiction", "mystery"]),
    "CLASS-010": _label_rule("bullish", ["bearish", "neutral"]),
    # --- logical reasoning ---
    "LOGIC-001": AnswerRule(require=[r"\bvalid\b"], forbid=[r"\binvalid\b", r"not valid"]),
    "LOGIC-002": AnswerRule(
        require=[r"\ba\b\s*(is|:|=|-|->|,)\s*(a\s+)?knight", r"\bb\b\s*(is|:|=|-|->|,)\s*(a\s+)?knave"],
        forbid=[r"\ba\b\s*(is|:|=|-|->|,)\s*(a\s+)?knave", r"\bb\b\s*(is|:|=|-|->|,)\s*(a\s+)?knight"]),
    "LOGIC-003": AnswerRule(require=[r"\bdave\b"], forbid=[r"\b(alice|bob|carol)\b"]),
    "LOGIC-004": AnswerRule(require=[r"(not|n't)\s+raining", r"(not|n't)\s+(be\s+)?cold",
                                     r"\bor\b"]),
    "LOGIC-005": AnswerRule(require=[r"\byes\b"], forbid=[r"\bno\b"]),
    "LOGIC-006": AnswerRule(require=[r"\ba\W+b\W+d\W+c\b", r"\ba\W+d\W+b\W+c\b"], scope="full"),
    "LOGIC-007": AnswerRule(require=[r"\bno\b|\bcannot\b|can't|can not|not valid|invalid"],
                            forbid=[r"\byes\b"]),
    "LOGIC-008": AnswerRule(require=[r"anna[^.;\n]{0,30}\bfish", r"brian[^.;\n]{0,30}\bdog",
                                     r"clara[^.;\n]{0,30}\bcat"]),
    "LOGIC-009": AnswerRule(require=[r"slippery[\s-]+slope"]),
    "LOGIC-010": AnswerRule(require=[r"\btrue\b"], forbid=[r"\bfalse\b"]),
    # --- mathematical reasoning (numeric answers in the final answer) ---
    "MATH-001": AnswerRule(require=[rf"{_NUM}7\.20?{_END}"]),
    "MATH-002": AnswerRule(require=[r"34\s*/\s*13|2\.615|2\.62\b", r"53\s*/\s*13|4\.077|4\.08\b"]),
    "MATH-003": AnswerRule(require=[r"160\s*\*?\s*pi"]),
    "MATH-004": AnswerRule(require=[r"10\s*/\s*21"]),
    "MATH-005": AnswerRule(require=[rf"{_NUM}1125\.51{_END}"]),
    "MATH-006": AnswerRule(require=[rf"{_NUM}1{_END}"]),
    "MATH-007": AnswerRule(require=[rf"{_NUM}12{_END}"]),
    "MATH-008": AnswerRule(require=[rf"{_NUM}95{_END}"]),
    "MATH-009": AnswerRule(require=[rf"{_NUM}2{_END}"]),
    "MATH-010": AnswerRule(require=[rf"{_NUM}31{_END}"]),
    # --- question answering ---
    "QA-001": AnswerRule(require=[r"einstein"]),
    "QA-002": AnswerRule(require=[r"december\s+25,?\s+2021|25\s+december,?\s+2021|2021-12-25",
                                  r"\bl2\b|lagrange point 2|second lagrange"], scope="full"),
    "QA-003": AnswerRule(require=[r"\b1789\b"]),
    "QA-004": AnswerRule(require=[r"amazon", r"atlantic"], scope="full"),
    "QA-007": AnswerRule(require=[r"\bvenus\b", r"greenhouse|carbon dioxide|co2|atmospher"],
                         scope="full"),
    "QA-008": AnswerRule(require=[r"4\.2\s*(billion|bn|b)\b", rf"{_NUM}8\s*%",
                                  r"2\.9\s*(billion|bn|b)\b"], scope="full"),
    "QA-010": AnswerRule(require=[r"\bau\b", r"\b79\b"], scope="full"),
    "QA-013": AnswerRule(require=[r"marbury"]),
    "QA-015": AnswerRule(require=[r"sophia martinez", r"liam chen", r"zurich", r"tokyo"],
                         scope="full"),
    "QA-016": AnswerRule(require=[r"\bsyn\b", r"syn[\s/-]*ack", r"\back\b"], scope="full"),
}


def normalize(text: str) -> str:
    text = text.casefold()
    text = re.sub(r"\\[dt]?frac\{([^{}]*)\}\{([^{}]*)\}", r"(\1)/(\2)", text)
    text = re.sub(r"\(([\d.]+)\)/\(([\d.]+)\)", r"\1/\2", text)
    replacements = {
        "π": "pi", "\\pi": "pi", "−": "-", "–": "-", "—": "-", "→": "->", "⇒": "->",
        "\\cdot": "*", "×": "*", "\\times": "*", "\\boxed": "", "’": "'",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    text = re.sub(r"(?<=\d),(?=\d{3}\b)", "", text)
    text = re.sub(r"[*_`$\\{}]", " ", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text


def answer_region(output: str, scope: str) -> str:
    norm = normalize(output or "")
    if scope == "full":
        return norm
    idx = norm.rfind("final answer")
    if idx >= 0:
        region = norm[idx + len("final answer"):]
        return region.lstrip(" :.-\n")
    # No marker (format instruction not followed): score the whole output. This is
    # conservative because forbidden alternatives mentioned anywhere count against it.
    # (A 300-character tail was used first, but the evaluator audit found it could cut an
    # answer word such as "Yes" in half.)
    return norm


def has_final_answer_marker(output: str) -> bool:
    return "final answer" in normalize(output or "")


def score_answer(prompt_id: str, output: str | None) -> bool | None:
    """Return True/False for items in the answer key, None for unscorable items."""
    rule = ANSWER_KEY.get(prompt_id)
    if rule is None:
        return None
    if not output or not output.strip():
        return False
    region = answer_region(output, rule.scope)
    if not all(re.search(p, region) for p in rule.require):
        return False
    return not any(re.search(p, region) for p in rule.forbid)
