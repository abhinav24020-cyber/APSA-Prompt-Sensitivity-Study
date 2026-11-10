"""Pure-stdlib distance and token utilities for perturbation measurement.

All functions operate in O(m*n) time (Levenshtein) or O(n) (word ops).
No external dependencies required.
"""

from __future__ import annotations

import re


def char_edit_distance(a: str, b: str) -> int:
    """Compute the raw character-level Levenshtein edit distance between *a* and *b*.

    Uses the Wagner-Fischer dynamic programming algorithm in O(m*n) time and
    O(min(m,n)) space.
    """
    if a == b:
        return 0
    if len(a) < len(b):
        a, b = b, a  # ensure a is the longer string
    # Only keep two rows to save memory
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        curr = [i] + [0] * len(b)
        for j, cb in enumerate(b, 1):
            if ca == cb:
                curr[j] = prev[j - 1]
            else:
                curr[j] = 1 + min(prev[j], curr[j - 1], prev[j - 1])
        prev = curr
    return prev[len(b)]


def word_edit_distance(a: str, b: str) -> int:
    """Compute the word-level Levenshtein edit distance (tokens as atoms)."""
    wa = _word_tokens(a)
    wb = _word_tokens(b)
    # Same DP, but over word lists
    if wa == wb:
        return 0
    m, n = len(wa), len(wb)
    prev = list(range(n + 1))
    for i in range(1, m + 1):
        curr = [i] + [0] * n
        for j in range(1, n + 1):
            if wa[i - 1] == wb[j - 1]:
                curr[j] = prev[j - 1]
            else:
                curr[j] = 1 + min(prev[j], curr[j - 1], prev[j - 1])
        prev = curr
    return prev[n]


def _word_tokens(text: str) -> list[str]:
    """Split text into lowercase word tokens (preserving punctuation as own token)."""
    return re.findall(r"[a-zA-Z0-9']+|[^\s\w]", text.lower())


def changed_tokens(original: str, perturbed: str) -> list[str]:
    """Return the list of word-tokens that differ between *original* and *perturbed*.

    Uses a simple symmetric-difference approach on token multisets, which is
    sufficient for the single-edit perturbations used in Phase 4.
    """
    orig_words = _word_tokens(original)
    pert_words = _word_tokens(perturbed)

    # Find tokens added and removed via multiset diff
    from collections import Counter
    orig_count = Counter(orig_words)
    pert_count = Counter(_word_tokens(perturbed))

    diff: list[str] = []
    for tok, cnt in orig_count.items():
        if pert_count[tok] < cnt:
            diff.extend([tok] * (cnt - pert_count[tok]))
    for tok, cnt in pert_count.items():
        if orig_count[tok] < cnt:
            diff.extend([tok] * (cnt - orig_count[tok]))
    return diff


def is_lexically_minimal(original: str, perturbed: str, threshold: float = 0.15) -> bool:
    """Return True iff the normalised word edit distance does not exceed *threshold*.

    Normalised by ``max(len(original_words), len(perturbed_words))``.
    """
    wa = _word_tokens(original)
    wb = _word_tokens(perturbed)
    denom = max(len(wa), len(wb), 1)
    return word_edit_distance(original, perturbed) / denom <= threshold
