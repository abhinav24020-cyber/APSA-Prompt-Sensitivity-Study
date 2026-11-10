"""Lexical input distance metrics.

Mathematical definitions
------------------------
Let P  = original prompt string of length |P|  characters / |P_w|  word-tokens.
Let P' = perturbed prompt string of length |P'| characters / |P'_w| word-tokens.

(1) Character-level Levenshtein distance
    d_char(P, P') = edit(P, P')
    Minimum number of single-character insertions, deletions, or substitutions
    required to transform P into P'.  Uses the Wagner-Fischer DP algorithm.
    Complexity: O(|P| * |P'|) time, O(min(|P|, |P'|)) space.

(2) Normalized character distance
    d_char_norm(P, P') = edit(P, P') / max(|P|, |P'|)
    Scales (1) to [0, 1] by dividing by the longer string's character length.
    Equals 0 iff P == P'; equals 1 iff one string is empty and the other is not.

(3) Word-level edit distance
    d_word(P, P') = word_edit(P_w, P'_w)
    Same Levenshtein recurrence but over sequences of word-tokens rather than
    characters.  Tokenisation: lowercase, keep alphanumeric + apostrophe
    sequences and punctuation marks as their own tokens (re pattern below).

(4) Changed-word count
    n_words_changed(P, P') = d_word(P, P')
    Interpreting each edit (insertion / deletion / substitution at word level)
    as one changed word.

(5) Changed-character count
    n_chars_changed(P, P') = d_char(P, P')
    Raw character-level edit distance (same value as metric 1, exposed under
    a semantically descriptive name for use in downstream reporting).

(6) Percentage of prompt changed
    pct_changed(P, P') = d_char_norm(P, P') * 100
    Human-readable representation of the normalized character distance,
    expressed in percent.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


# ---------------------------------------------------------------------------
# Public result type
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class LexicalDistanceResult:
    """All lexical distance sub-metrics for a single (P, P') pair.

    Attributes
    ----------
    char_levenshtein : int
        Raw character-level Levenshtein edit distance  [metric 1].
    char_levenshtein_normalized : float
        Normalized ∈ [0, 1] by max(|P|, |P'|)  [metric 2].
    word_levenshtein : int
        Raw word-level edit distance  [metric 3 / 4].
    num_words_changed : int
        Equals word_levenshtein (one edit == one changed word)  [metric 4].
    num_chars_changed : int
        Equals char_levenshtein (descriptive alias)  [metric 5].
    pct_prompt_changed : float
        100 × char_levenshtein_normalized  [metric 6].
    """

    char_levenshtein: int
    char_levenshtein_normalized: float
    word_levenshtein: int
    num_words_changed: int
    num_chars_changed: int
    pct_prompt_changed: float


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _word_tokens(text: str) -> list[str]:
    """Lowercase word-tokenization that keeps punctuation as separate tokens.

    Pattern captures:
      - Alphanumeric runs and contractions  (e.g. ``don't``, ``42``)
      - Individual non-whitespace punctuation characters
    """
    return re.findall(r"[a-zA-Z0-9']+|[^\s\w]", text.lower())


def _char_edit_distance(a: str, b: str) -> int:
    """Wagner-Fischer character-level Levenshtein distance (O(m·n), O(min(m,n)) space)."""
    if a == b:
        return 0
    if len(a) < len(b):
        a, b = b, a  # ensure a is the longer string to minimize inner-list length
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


def _word_edit_distance(wa: list[str], wb: list[str]) -> int:
    """Same DP recurrence but over word-token lists."""
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


# ---------------------------------------------------------------------------
# Public calculator
# ---------------------------------------------------------------------------

class LexicalDistanceCalculator:
    """Compute all six lexical distance metrics between two prompt strings.

    Usage
    -----
    >>> calc = LexicalDistanceCalculator()
    >>> result = calc.compute("Hello world", "Hello Word")
    >>> result.char_levenshtein
    2
    """

    def compute(self, original: str, perturbed: str) -> LexicalDistanceResult:
        """Compute and return all lexical distance metrics.

        Parameters
        ----------
        original:
            The unmodified baseline prompt P.
        perturbed:
            The perturbed prompt P'.

        Returns
        -------
        LexicalDistanceResult
            Frozen dataclass containing all six metric values.
        """
        # --- Metric 1 & 5: raw character Levenshtein ---
        char_lev = _char_edit_distance(original, perturbed)

        # --- Metric 2 & 6: normalized / percentage ---
        max_len = max(len(original), len(perturbed), 1)  # guard against empty strings
        char_norm = char_lev / max_len
        pct = char_norm * 100.0

        # --- Metric 3 & 4: word-level edit distance ---
        orig_tokens = _word_tokens(original)
        pert_tokens = _word_tokens(perturbed)
        word_lev = _word_edit_distance(orig_tokens, pert_tokens)

        return LexicalDistanceResult(
            char_levenshtein=char_lev,
            char_levenshtein_normalized=round(char_norm, 6),
            word_levenshtein=word_lev,
            num_words_changed=word_lev,
            num_chars_changed=char_lev,
            pct_prompt_changed=round(pct, 4),
        )
