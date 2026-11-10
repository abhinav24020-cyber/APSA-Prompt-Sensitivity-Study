import csv
from fractions import Fraction
from itertools import permutations
from pathlib import Path

DATASET = Path(__file__).resolve().parents[2] / "data" / "baseline_prompts.csv"


def _rows_by_id():
    with DATASET.open(encoding="utf-8-sig", newline="") as stream:
        return {row["prompt_id"]: row for row in csv.DictReader(stream)}


def test_corrected_math_reference_answers_are_consistent():
    rows = _rows_by_id()
    x, y = Fraction(34, 13), Fraction(53, 13)
    assert 3 * x + 2 * y == 16
    assert 5 * x - y == 9
    assert rows["MATH-002"]["expected_answer"] == "(34/13, 53/13)"

    matrix = [[2, 0, 1], [3, 4, -2], [1, 5, 0]]
    determinant = (
        matrix[0][0] * (matrix[1][1] * matrix[2][2] - matrix[1][2] * matrix[2][1])
        - matrix[0][1] * (matrix[1][0] * matrix[2][2] - matrix[1][2] * matrix[2][0])
        + matrix[0][2] * (matrix[1][0] * matrix[2][1] - matrix[1][1] * matrix[2][0])
    )
    assert determinant == 31
    assert rows["MATH-010"]["expected_answer"] == "31"


def test_logic_references_capture_all_solutions_and_sufficient_clues():
    rows = _rows_by_id()
    valid_orders = [
        order for order in permutations("ABCD")
        if order.index("A") < order.index("B")
        and order.index("B") < order.index("C")
        and order.index("A") < order.index("D") < order.index("C")
    ]
    assert set(valid_orders) == {tuple("ABDC"), tuple("ADBC")}
    assert set(rows["LOGIC-006"]["expected_answer"].split("; ")) == {
        "A -> B -> D -> C",
        "A -> D -> B -> C",
    }

    prompt = rows["LOGIC-008"]["original_prompt"]
    assert "Clara does not own the dog" in prompt
