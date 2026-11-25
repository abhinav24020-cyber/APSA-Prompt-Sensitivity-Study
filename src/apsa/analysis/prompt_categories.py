"""Explainable, offline category suggestions for new APSA prompts."""

import re


# Match the requested task, leaving quoted examples and fenced code out of the cues.
_EXAMPLES = re.compile(r"```[\s\S]*?```|\"[^\"\n]*\"|(?<!\w)'[^'\n]+'(?!\w)|`[^`\n]+`")
_CUES = {
    "classification": re.compile(
        r"\b(?:classify|categorize|categorise|label|assign\s+(?:a\s+)?(?:label|category)|"
        r"(?:choose|select|identify)\s+(?:the|a|one)\s+(?:label|category|sentiment|topic)|"
        r"positive,?\s+(?:negative|neutral)(?:\s+or\s+neutral)?|positive\s+or\s+negative)\b", re.I),
    "code_generation": re.compile(
        r"\b(?:implement|debug|refactor)\b|\b(?:write|generate|create|provide|return|fix|complete)\b"
        r"[^.!?;\n]{0,65}\b(?:function|script|class|program|code|query|regex|implementation)\b", re.I),
    "logical_reasoning": re.compile(
        r"\b(?:truth value|premises?|logically|deduce|infer|conclude|by elimination|"
        r"valid (?:inference|execution orders?)|what (?:logically )?follows|if and only if|implies|who (?:owns|sits))\b"
        r"|\bif\s+(?:all|every|no|some)\b", re.I),
    "mathematical_reasoning": re.compile(
        r"\b(?:calculate|compute|solve|simplify|evaluate)\b[^.!?;\n]{0,70}"
        r"(?:\d|\b(?:equation|determinant|matrix|integral|derivative|probability|sum|price|area|perimeter)\b)"
        r"|\bsolve for\s+\w+|\bwhat is\s+-?\d+(?:\.\d+)?\s*[-+*/×÷^]\s*\d"
        r"|\b(?:how (?:many|much|long|far)|what is)\b[^?;\n]{0,65}"
        r"\b(?:total|percent|average|sum|product|probability|remainder|perimeter|area|determinant)\b", re.I),
}
_FACTUAL = re.compile(r"\b(?:who|what|when|where|which|why|how|define|explain|name|identify|extract)\b", re.I)
_OPEN_ENDED = re.compile(r"\b(?:summari[sz]e|translate|brainstorm|write (?:a |an )?(?:poem|story|essay))\b", re.I)


def suggest_category(prompt: str) -> dict:
    """Return a suggestion and the matched wording, or a reason to ask for a label."""
    request = _EXAMPLES.sub(" ", prompt)
    matches = {category: cue.group(0).strip() for category, pattern in _CUES.items()
               if (cue := pattern.search(request))}
    if len(matches) == 1 and not _OPEN_ENDED.search(request):
        category, cue = next(iter(matches.items()))
        return {"proposed_category": category, "reason": f"The request contains {cue!r}, a cue for this task type."}
    if matches:
        detail = ", ".join(f"{category} ({cue!r})" for category, cue in matches.items())
        return {"proposed_category": None, "reason": f"The request has overlapping or additional tasks: {detail}."}
    factual = _FACTUAL.search(request)
    if factual and not _OPEN_ENDED.search(request):
        return {"proposed_category": "question_answering",
                "reason": f"The request uses {factual[0]!r} to ask for an answer or explanation."}
    return {"proposed_category": None, "reason": "No clear request fits one of the five supported categories."}
