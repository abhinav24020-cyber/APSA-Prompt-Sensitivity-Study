"""Execution-based correctness for code-generation outputs.

Extracts Python code from a model response and runs it with item-specific unit tests in
a separate, isolated Python subprocess with a timeout. This is test-based functional
correctness (pass/fail on the listed cases), not a proof of correctness, and the
subprocess is a convenience boundary rather than a security sandbox: only run it on
outputs from the study's benign coding prompts.
"""

from __future__ import annotations

import ast
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

# Item-specific tests: (expected entry-point name, test source using the name `f`).
CODE_TESTS: dict[str, tuple[str, str]] = {
    "CODE-001": ("reverse_string", """
assert f("abc") == "cba"
assert f("") == ""
assert f("a") == "a"
assert f("hello world") == "dlrow olleh"
"""),
    "CODE-002": ("is_prime", """
for n, want in [(0, False), (1, False), (2, True), (3, True), (4, False), (17, True),
                (25, False), (97, True), (-7, False), (7919, True), (1000000, False)]:
    assert f(n) == want, (n, want)
"""),
    "CODE-003": ("flatten_list", """
assert f([1, [2, [3, [4]], 5]]) == [1, 2, 3, 4, 5]
assert f([]) == []
assert f([[[]]]) == []
assert f([1, 2]) == [1, 2]
"""),
    "CODE-004": ("fibonacci", """
assert list(f(1)) == [0]
assert list(f(2)) == [0, 1]
assert list(f(7)) == [0, 1, 1, 2, 3, 5, 8]
assert list(f(0)) == []
"""),
    "CODE-005": ("word_frequencies", """
assert f("Hello, hello! World.") == {"hello": 2, "world": 1}
assert f("") == {}
assert f("A a a; b") == {"a": 3, "b": 1}
"""),
    "CODE-006": ("merge_sorted", """
assert f([1, 3, 5], [2, 4, 6]) == [1, 2, 3, 4, 5, 6]
assert f([], [1]) == [1]
assert f([1, 1], [1]) == [1, 1, 1]
assert f([], []) == []
"""),
    "CODE-007": ("is_anagram", """
assert f("Listen", "Silent") is True or f("Listen", "Silent") == True
assert f("Dormitory", "Dirty room") == True
assert f("abc", "abd") == False
assert f("a", "aa") == False
"""),
    "CODE-008": ("Singleton", """
a = f()
b = f()
assert a is b
"""),
    "CODE-009": ("binary_search", """
assert f([1, 3, 5, 7, 9], 7) == 3
assert f([1, 3, 5], 4) == -1
assert f([], 1) == -1
assert f([2], 2) == 0
"""),
    "CODE-010": ("max_subarray_sum", """
assert f([-2, 1, -3, 4, -1, 2, 1, -5, 4]) == 6
assert f([1]) == 1
assert f([-3, -1, -2]) == -1
assert f([5, 4, -1, 7, 8]) == 23
"""),
}

_FENCE = re.compile(r"```(?:python|py|Python)?[ \t]*\n(.*?)```", re.DOTALL)


def extract_code(output: str) -> str | None:
    """Return the longest fenced code block that parses, or the whole output if it parses."""
    blocks = [b for b in _FENCE.findall(output or "")]
    blocks.sort(key=len, reverse=True)
    for block in blocks + [output or ""]:
        try:
            ast.parse(block)
            if block.strip():
                return block
        except SyntaxError:
            continue
    return None


def _top_level_names(code: str) -> list[str]:
    tree = ast.parse(code)
    return [n.name for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef))]


@dataclass
class CodeRunResult:
    applicable: bool
    passed: bool | None
    error: str | None = None
    name_fallback: bool = False


def run_code_tests(prompt_id: str, output: str | None, timeout_seconds: int = 10) -> CodeRunResult:
    if prompt_id not in CODE_TESTS:
        return CodeRunResult(applicable=False, passed=None)
    name, tests = CODE_TESTS[prompt_id]
    code = extract_code(output or "")
    if code is None:
        return CodeRunResult(applicable=True, passed=False, error="no_parseable_code")
    names = _top_level_names(code)
    fallback = False
    if name not in names:
        if len(names) == 1:
            name, fallback = names[0], True
        else:
            return CodeRunResult(applicable=True, passed=False, error="entry_point_missing")
    # Drop top-level demo calls such as print(...) or input() that would block/alter output.
    program = (
        "import builtins\nbuiltins.input = lambda *a, **k: ''\n"
        + code
        + f"\n\nf = {name}\n"
        + tests
        + "\nprint('APSA_TESTS_PASSED')\n"
    )
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "candidate.py"
        path.write_text(program, encoding="utf-8")
        try:
            proc = subprocess.run(
                [sys.executable, "-I", str(path)], cwd=tmp, capture_output=True,
                text=True, timeout=timeout_seconds,
            )
        except subprocess.TimeoutExpired:
            return CodeRunResult(True, False, "timeout", fallback)
    passed = proc.returncode == 0 and "APSA_TESTS_PASSED" in proc.stdout
    err = None if passed else (proc.stderr.strip().splitlines() or ["failed"])[-1][:300]
    return CodeRunResult(True, passed, err, fallback)


@dataclass
class CodeExecutionResult:
    applicable: bool
    original_pass: bool
    perturbed_pass: bool
    functional_failure: bool
    original_error: str | None = None
    perturbed_error: str | None = None


class CodeExecutionEvaluator:
    """Execute and test Python code extracted from paired LLM outputs."""

    def __init__(self, timeout_seconds: int = 10) -> None:
        self._timeout = timeout_seconds

    def evaluate(self, original_output: str, perturbed_output: str, prompt_id: str) -> CodeExecutionResult:
        a = run_code_tests(prompt_id, original_output, self._timeout)
        b = run_code_tests(prompt_id, perturbed_output, self._timeout)
        if not a.applicable:
            return CodeExecutionResult(False, False, False, False)
        return CodeExecutionResult(
            applicable=True,
            original_pass=bool(a.passed),
            perturbed_pass=bool(b.passed),
            functional_failure=bool(a.passed) and not bool(b.passed),
            original_error=a.error,
            perturbed_error=b.error,
        )
