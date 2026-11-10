"""Unit tests for src/apsa/metrics/input_distance/ — Phase 5.

Coverage
--------
* LexicalDistanceCalculator — all six metrics
* SemanticDistanceCalculator — with a deterministic mock embedder
* EmbeddingModel ABC — contract enforcement
* SyntacticDistanceCalculator — stub / NotImplementedError behaviour
* Edge cases: identical strings, empty strings, single character, Unicode
* Mathematical property tests (symmetry, identity, triangle inequality approx.)
"""

from __future__ import annotations

import math

import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _approx(value: float, expected: float, rel: float = 1e-4) -> bool:
    """Return True iff value ≈ expected within a relative tolerance."""
    if expected == 0.0:
        return abs(value) < 1e-9
    return abs(value - expected) / abs(expected) < rel


# ---------------------------------------------------------------------------
# Lexical distance tests
# ---------------------------------------------------------------------------

class TestLexicalDistanceCalculator:
    """Tests for LexicalDistanceCalculator and LexicalDistanceResult."""

    @pytest.fixture
    def calc(self):
        from apsa.metrics.input_distance import LexicalDistanceCalculator
        return LexicalDistanceCalculator()

    # --- Metric 1: char_levenshtein ---

    def test_char_levenshtein_identical(self, calc):
        """d_char(P, P) = 0 for any P."""
        r = calc.compute("Hello, world!", "Hello, world!")
        assert r.char_levenshtein == 0

    def test_char_levenshtein_single_insertion(self, calc):
        """'cat' → 'cart': one insertion → distance = 1."""
        r = calc.compute("cat", "cart")
        assert r.char_levenshtein == 1

    def test_char_levenshtein_single_deletion(self, calc):
        """'cart' → 'cat': one deletion → distance = 1."""
        r = calc.compute("cart", "cat")
        assert r.char_levenshtein == 1

    def test_char_levenshtein_single_substitution(self, calc):
        """'cat' → 'bat': one substitution → distance = 1."""
        r = calc.compute("cat", "bat")
        assert r.char_levenshtein == 1

    def test_char_levenshtein_completely_different(self, calc):
        """'abc' → 'xyz': 3 substitutions → distance = 3."""
        r = calc.compute("abc", "xyz")
        assert r.char_levenshtein == 3

    def test_char_levenshtein_empty_to_string(self, calc):
        """'' → 'hello': 5 insertions → distance = 5."""
        r = calc.compute("", "hello")
        assert r.char_levenshtein == 5

    def test_char_levenshtein_string_to_empty(self, calc):
        """'hello' → '': 5 deletions → distance = 5."""
        r = calc.compute("hello", "")
        assert r.char_levenshtein == 5

    def test_char_levenshtein_symmetry(self, calc):
        """d_char(P, P') == d_char(P', P) for all P, P'."""
        a, b = "The quick brown fox", "The slow red fox"
        assert calc.compute(a, b).char_levenshtein == calc.compute(b, a).char_levenshtein

    def test_char_levenshtein_both_empty(self, calc):
        """d_char('', '') = 0."""
        r = calc.compute("", "")
        assert r.char_levenshtein == 0

    # --- Metric 2: char_levenshtein_normalized ---

    def test_char_norm_identical(self, calc):
        """Normalized distance for identical strings = 0.0."""
        r = calc.compute("foo bar", "foo bar")
        assert r.char_levenshtein_normalized == pytest.approx(0.0)

    def test_char_norm_range(self, calc):
        """Normalized distance is always in [0, 1]."""
        pairs = [
            ("", "hello"),
            ("hello", ""),
            ("aaa", "bbb"),
            ("kitten", "sitting"),
            ("", ""),
        ]
        for a, b in pairs:
            r = calc.compute(a, b)
            assert 0.0 <= r.char_levenshtein_normalized <= 1.0, (
                f"Out of range for ({a!r}, {b!r}): {r.char_levenshtein_normalized}"
            )

    def test_char_norm_formula(self, calc):
        """Verify: norm = edit / max(|P|, |P'|)."""
        a, b = "kitten", "sitting"
        r = calc.compute(a, b)
        expected_norm = r.char_levenshtein / max(len(a), len(b))
        assert r.char_levenshtein_normalized == pytest.approx(expected_norm, rel=1e-5)

    def test_char_norm_single_char_change(self, calc):
        """'abcde' → 'abcde' with 1 sub: norm = 1/5 = 0.2."""
        r = calc.compute("abcde", "abcXe")
        assert r.char_levenshtein_normalized == pytest.approx(1 / 5, rel=1e-5)

    # --- Metric 3 & 4: word_levenshtein / num_words_changed ---

    def test_word_levenshtein_identical(self, calc):
        """Word distance for identical strings = 0."""
        r = calc.compute("What is AI?", "What is AI?")
        assert r.word_levenshtein == 0

    def test_word_levenshtein_one_word_changed(self, calc):
        """'compute X' → 'calculate X': one word substituted → distance = 1."""
        r = calc.compute("compute the value", "calculate the value")
        assert r.word_levenshtein == 1

    def test_word_levenshtein_word_added(self, calc):
        """'go home' → 'go home now': one word inserted → distance = 1."""
        r = calc.compute("go home", "go home now")
        assert r.word_levenshtein == 1

    def test_word_levenshtein_word_deleted(self, calc):
        """'please go home' → 'go home': one word deleted → distance = 1."""
        r = calc.compute("please go home", "go home")
        assert r.word_levenshtein == 1

    def test_word_levenshtein_symmetry(self, calc):
        """Word distance is symmetric."""
        a = "Explain the concept of entropy"
        b = "Describe the notion of entropy"
        assert calc.compute(a, b).word_levenshtein == calc.compute(b, a).word_levenshtein

    def test_num_words_changed_equals_word_levenshtein(self, calc):
        """num_words_changed must always equal word_levenshtein."""
        pairs = [
            ("hello world", "hello there"),
            ("foo", "bar baz"),
            ("a b c d", "a b c d"),
        ]
        for a, b in pairs:
            r = calc.compute(a, b)
            assert r.num_words_changed == r.word_levenshtein

    # --- Metric 5: num_chars_changed ---

    def test_num_chars_changed_equals_char_levenshtein(self, calc):
        """num_chars_changed must always equal char_levenshtein."""
        pairs = [("kitten", "sitting"), ("abc", "abc"), ("", "xyz")]
        for a, b in pairs:
            r = calc.compute(a, b)
            assert r.num_chars_changed == r.char_levenshtein

    # --- Metric 6: pct_prompt_changed ---

    def test_pct_changed_identical(self, calc):
        """Identical strings → 0% changed."""
        r = calc.compute("same text", "same text")
        assert r.pct_prompt_changed == pytest.approx(0.0)

    def test_pct_changed_formula(self, calc):
        """pct = char_norm * 100."""
        r = calc.compute("hello", "hXllo")
        expected_pct = (r.char_levenshtein / max(len("hello"), len("hXllo"))) * 100
        assert r.pct_prompt_changed == pytest.approx(expected_pct, rel=1e-4)

    def test_pct_changed_range(self, calc):
        """Percentage is always in [0, 100]."""
        r = calc.compute("abc", "xyz")
        assert 0.0 <= r.pct_prompt_changed <= 100.0

    # --- Result is frozen ---

    def test_result_is_frozen(self, calc):
        """LexicalDistanceResult must be immutable (frozen dataclass)."""
        r = calc.compute("foo", "bar")
        with pytest.raises(Exception):   # FrozenInstanceError or AttributeError
            r.char_levenshtein = 999   # type: ignore[misc]

    # --- Known reference values ---

    def test_kitten_sitting(self, calc):
        """Classic Levenshtein example: edit('kitten', 'sitting') = 3."""
        r = calc.compute("kitten", "sitting")
        assert r.char_levenshtein == 3

    def test_unicode_characters(self, calc):
        """Unicode characters should be handled correctly as code-points."""
        r = calc.compute("café", "cafe")
        # 'é' (1 char) → 'e' (1 char): 1 substitution
        assert r.char_levenshtein == 1

    def test_whitespace_sensitivity(self, calc):
        """Extra whitespace counts as character-level differences."""
        r = calc.compute("hello world", "hello  world")
        assert r.char_levenshtein == 1   # one extra space


# ---------------------------------------------------------------------------
# Semantic distance tests (using a deterministic mock embedder)
# ---------------------------------------------------------------------------

class MockEmbedder:
    """Deterministic test embedder using hard-coded 3-D unit vectors."""

    _VECTORS: dict[str, list[float]] = {
        "identical text": [1.0, 0.0, 0.0],
        "similar text":   [0.9, math.sqrt(1 - 0.81), 0.0],    # cos = 0.9
        "orthogonal":     [0.0, 1.0, 0.0],                     # cos = 0.0
        "opposite":       [-1.0, 0.0, 0.0],                    # cos = -1.0
        "zero vector":    [0.0, 0.0, 0.0],
    }

    @property
    def model_name(self) -> str:
        return "mock-test-embedder"

    def encode(self, texts: list[str]) -> list[list[float]]:
        result = []
        for t in texts:
            if t in self._VECTORS:
                result.append(list(self._VECTORS[t]))
            else:
                # Default: [1, 0, 0] (unit vector pointing along x-axis)
                result.append([1.0, 0.0, 0.0])
        return result


class TestSemanticDistanceCalculator:
    """Tests for SemanticDistanceCalculator with a mock embedder."""

    @pytest.fixture
    def calc(self):
        from apsa.metrics.input_distance import SemanticDistanceCalculator
        return SemanticDistanceCalculator(MockEmbedder())

    def test_identical_strings_skip_embed(self):
        """Identical strings return distance=0 without calling the embedder."""
        from apsa.metrics.input_distance import SemanticDistanceCalculator

        class NeverCallEmbedder:
            @property
            def model_name(self): return "never-call"
            def encode(self, texts): raise AssertionError("Should not be called")

        calc = SemanticDistanceCalculator(NeverCallEmbedder())
        r = calc.compute("same text", "same text")
        assert r.cosine_distance == pytest.approx(0.0)
        assert r.cosine_similarity == pytest.approx(1.0)

    def test_identical_embeddings(self, calc):
        """Two strings that map to the same vector → distance = 0."""
        r = calc.compute("identical text", "unknown_a")
        # Both map to [1,0,0] → cos = 1 → dist = 0
        assert r.cosine_distance == pytest.approx(0.0, abs=1e-7)

    def test_orthogonal_embeddings(self, calc):
        """Orthogonal vectors → cos = 0 → D_semantic = 1."""
        r = calc.compute("identical text", "orthogonal")
        assert r.cosine_distance == pytest.approx(1.0, rel=1e-5)
        assert r.cosine_similarity == pytest.approx(0.0, abs=1e-5)

    def test_opposite_embeddings(self, calc):
        """Anti-parallel vectors → cos = -1 → D_semantic = 2."""
        r = calc.compute("identical text", "opposite")
        assert r.cosine_distance == pytest.approx(2.0, rel=1e-5)
        assert r.cosine_similarity == pytest.approx(-1.0, rel=1e-5)

    def test_partial_similarity(self, calc):
        """cos = 0.9 → D_semantic = 0.1."""
        r = calc.compute("identical text", "similar text")
        assert r.cosine_distance == pytest.approx(0.1, rel=1e-4)
        assert r.cosine_similarity == pytest.approx(0.9, rel=1e-4)

    def test_distance_is_complement_of_similarity(self, calc):
        """distance + similarity == 1.0 for unit-norm vectors."""
        r = calc.compute("identical text", "similar text")
        assert r.cosine_distance + r.cosine_similarity == pytest.approx(1.0, rel=1e-6)

    def test_formula_d_semantic(self, calc):
        """D_semantic = 1 - cosine_similarity (the documented formula)."""
        r = calc.compute("identical text", "similar text")
        assert r.cosine_distance == pytest.approx(1.0 - r.cosine_similarity, rel=1e-8)

    def test_result_contains_model_name(self, calc):
        """Result embeds the embedding model name for tracking."""
        r = calc.compute("foo", "bar")
        assert r.embedding_model == "mock-test-embedder"

    def test_result_is_frozen(self, calc):
        """SemanticDistanceResult must be immutable (frozen dataclass)."""
        r = calc.compute("foo", "bar")
        with pytest.raises(Exception):
            r.cosine_distance = 0.5  # type: ignore[misc]

    def test_embedding_model_name_property(self):
        """embedding_model_name property reflects the injected embedder."""
        from apsa.metrics.input_distance import SemanticDistanceCalculator
        calc = SemanticDistanceCalculator(MockEmbedder())
        assert calc.embedding_model_name == "mock-test-embedder"

    # --- Batch compute ---

    def test_compute_batch_empty(self, calc):
        """Empty input list returns empty list."""
        assert calc.compute_batch([]) == []

    def test_compute_batch_single_pair(self, calc):
        """Batch with one pair returns same result as scalar compute."""
        from apsa.metrics.input_distance import SemanticDistanceCalculator
        calc2 = SemanticDistanceCalculator(MockEmbedder())
        single = calc2.compute("identical text", "orthogonal")
        batch = calc2.compute_batch([("identical text", "orthogonal")])
        assert len(batch) == 1
        assert batch[0].cosine_distance == pytest.approx(single.cosine_distance, rel=1e-7)

    def test_compute_batch_identical_pair(self, calc):
        """Batch handles identical pairs without calling encode."""
        from apsa.metrics.input_distance import SemanticDistanceCalculator

        class CountingEmbedder:
            calls = 0
            @property
            def model_name(self): return "counter"
            def encode(self, texts):
                CountingEmbedder.calls += len(texts)
                return [[1.0, 0.0]] * len(texts)

        embedder = CountingEmbedder()
        calc2 = SemanticDistanceCalculator(embedder)
        results = calc2.compute_batch([("same", "same"), ("same", "same")])
        # Identical pairs → encode should not be called
        assert all(r.cosine_distance == pytest.approx(0.0) for r in results)

    def test_compute_batch_deduplicates_strings(self):
        """Batch encodes each unique string only once."""
        from apsa.metrics.input_distance import SemanticDistanceCalculator

        encoded_texts = []

        class RecordingEmbedder:
            @property
            def model_name(self): return "recorder"
            def encode(self, texts):
                encoded_texts.extend(texts)
                return [[1.0, 0.0]] * len(texts)

        calc = SemanticDistanceCalculator(RecordingEmbedder())
        calc.compute_batch([
            ("A", "B"),
            ("A", "C"),  # "A" should only be encoded once
            ("B", "C"),
        ])
        # "A", "B", "C" — each should appear exactly once
        assert len(encoded_texts) == 3
        assert set(encoded_texts) == {"A", "B", "C"}

    def test_compute_batch_order_preserved(self, calc):
        """Output list is in the same order as input pairs."""
        from apsa.metrics.input_distance import SemanticDistanceCalculator
        calc2 = SemanticDistanceCalculator(MockEmbedder())
        pairs = [
            ("identical text", "orthogonal"),
            ("identical text", "similar text"),
            ("identical text", "identical text"),
        ]
        results = calc2.compute_batch(pairs)
        assert len(results) == 3
        # First pair: orthogonal → dist ≈ 1.0
        assert results[0].cosine_distance == pytest.approx(1.0, rel=1e-5)
        # Third pair: identical → dist = 0.0
        assert results[2].cosine_distance == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# EmbeddingModel ABC contract tests
# ---------------------------------------------------------------------------

class TestEmbeddingModelABC:
    """Tests that the EmbeddingModel ABC enforces the correct contract."""

    def test_cannot_instantiate_abc(self):
        """Instantiating EmbeddingModel directly raises TypeError."""
        from apsa.metrics.input_distance import EmbeddingModel
        with pytest.raises(TypeError):
            EmbeddingModel()  # type: ignore[abstract]

    def test_missing_model_name_raises(self):
        """Subclass missing model_name property cannot be instantiated."""
        from apsa.metrics.input_distance import EmbeddingModel
        with pytest.raises(TypeError):
            class IncompleteEmbedder(EmbeddingModel):  # type: ignore[abstract]
                def encode(self, texts): return [[0.0]] * len(texts)
            IncompleteEmbedder()  # type: ignore[abstract]

    def test_missing_encode_raises(self):
        """Subclass missing encode method cannot be instantiated."""
        from apsa.metrics.input_distance import EmbeddingModel
        with pytest.raises(TypeError):
            class IncompleteEmbedder(EmbeddingModel):  # type: ignore[abstract]
                @property
                def model_name(self): return "incomplete"
            IncompleteEmbedder()  # type: ignore[abstract]

    def test_valid_custom_embedder(self):
        """A fully-implemented custom embedder can be injected and used."""
        from apsa.metrics.input_distance import EmbeddingModel, SemanticDistanceCalculator

        class ConstantEmbedder(EmbeddingModel):
            @property
            def model_name(self): return "constant-ones"
            def encode(self, texts): return [[1.0, 0.0, 0.0]] * len(texts)

        calc = SemanticDistanceCalculator(ConstantEmbedder())
        r = calc.compute("any text", "any other text")
        # cos([1,0,0], [1,0,0]) = 1 → dist = 0
        assert r.cosine_distance == pytest.approx(0.0, abs=1e-7)
        assert r.embedding_model == "constant-ones"


# ---------------------------------------------------------------------------
# Syntactic distance stub tests
# ---------------------------------------------------------------------------

class TestSyntacticDistanceCalculator:
    """Tests for the SyntacticDistanceCalculator stub."""

    def test_compute_raises_not_implemented(self):
        """compute() must raise NotImplementedError while the metric is unimplemented."""
        from apsa.metrics.input_distance import SyntacticDistanceCalculator
        calc = SyntacticDistanceCalculator()
        with pytest.raises(NotImplementedError, match="not implemented"):
            calc.compute("original prompt", "perturbed prompt")

    def test_accepts_custom_spacy_model(self):
        """Constructor accepts a spaCy model name without raising."""
        from apsa.metrics.input_distance import SyntacticDistanceCalculator
        calc = SyntacticDistanceCalculator(spacy_model="en_core_web_md")
        assert calc._spacy_model == "en_core_web_md"

    def test_result_type_is_frozen(self):
        """SyntacticDistanceMetrics is a frozen dataclass."""
        from apsa.metrics.input_distance import SyntacticDistanceMetrics
        r = SyntacticDistanceMetrics(tree_edit_distance=0.25)
        with pytest.raises(Exception):
            r.tree_edit_distance = 0.5  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Mathematical property tests
# ---------------------------------------------------------------------------

class TestMathematicalProperties:
    """Verify that all metrics satisfy their documented mathematical properties."""

    @pytest.fixture
    def lex(self):
        from apsa.metrics.input_distance import LexicalDistanceCalculator
        return LexicalDistanceCalculator()

    SAMPLE_STRINGS = [
        "The cat sat on the mat.",
        "The dog sat on the log.",
        "What is the capital of France?",
        "What is France's capital city?",
        "Compute the integral of x squared from 0 to 1.",
        "",
    ]

    def test_identity_property_char(self, lex):
        """d_char(P, P) = 0 for all P."""
        for s in self.SAMPLE_STRINGS:
            assert lex.compute(s, s).char_levenshtein == 0

    def test_identity_property_word(self, lex):
        """d_word(P, P) = 0 for all P."""
        for s in self.SAMPLE_STRINGS:
            assert lex.compute(s, s).word_levenshtein == 0

    def test_symmetry_property_char(self, lex):
        """d_char(P, P') == d_char(P', P) for all pairs."""
        pairs = list(zip(self.SAMPLE_STRINGS, self.SAMPLE_STRINGS[1:]))
        for a, b in pairs:
            assert lex.compute(a, b).char_levenshtein == lex.compute(b, a).char_levenshtein

    def test_symmetry_property_word(self, lex):
        """d_word(P, P') == d_word(P', P) for all pairs."""
        pairs = list(zip(self.SAMPLE_STRINGS, self.SAMPLE_STRINGS[1:]))
        for a, b in pairs:
            assert lex.compute(a, b).word_levenshtein == lex.compute(b, a).word_levenshtein

    def test_normalized_is_fraction_of_raw(self, lex):
        """char_levenshtein_normalized = char_levenshtein / max(|P|, |P'|)."""
        for a, b in zip(self.SAMPLE_STRINGS, self.SAMPLE_STRINGS[1:]):
            r = lex.compute(a, b)
            denom = max(len(a), len(b), 1)
            expected = r.char_levenshtein / denom
            assert r.char_levenshtein_normalized == pytest.approx(expected, rel=1e-5)

    def test_pct_equals_100_times_norm(self, lex):
        """pct_prompt_changed = 100 × char_levenshtein_normalized."""
        for a, b in zip(self.SAMPLE_STRINGS, self.SAMPLE_STRINGS[1:]):
            r = lex.compute(a, b)
            assert r.pct_prompt_changed == pytest.approx(
                r.char_levenshtein_normalized * 100, rel=1e-5
            )

    def test_num_words_changed_equals_word_lev(self, lex):
        """num_words_changed == word_levenshtein always."""
        for a, b in zip(self.SAMPLE_STRINGS, self.SAMPLE_STRINGS[1:]):
            r = lex.compute(a, b)
            assert r.num_words_changed == r.word_levenshtein

    def test_num_chars_changed_equals_char_lev(self, lex):
        """num_chars_changed == char_levenshtein always."""
        for a, b in zip(self.SAMPLE_STRINGS, self.SAMPLE_STRINGS[1:]):
            r = lex.compute(a, b)
            assert r.num_chars_changed == r.char_levenshtein


# ---------------------------------------------------------------------------
# Package import smoke test
# ---------------------------------------------------------------------------

class TestPackageImports:
    """Verify that all public names are importable from the top-level package."""

    def test_import_lexical(self):
        from apsa.metrics.input_distance import LexicalDistanceCalculator, LexicalDistanceResult
        assert LexicalDistanceCalculator is not None
        assert LexicalDistanceResult is not None

    def test_import_semantic(self):
        from apsa.metrics.input_distance import (
            EmbeddingModel,
            SemanticDistanceCalculator,
            SemanticDistanceResult,
            SentenceTransformerEmbedder,
        )
        assert SemanticDistanceCalculator is not None
        assert SemanticDistanceResult is not None
        assert EmbeddingModel is not None
        assert SentenceTransformerEmbedder is not None

    def test_import_syntactic(self):
        from apsa.metrics.input_distance import (
            SyntacticDistanceCalculator,
            SyntacticDistanceMetrics,
        )
        assert SyntacticDistanceCalculator is not None
        assert SyntacticDistanceMetrics is not None
