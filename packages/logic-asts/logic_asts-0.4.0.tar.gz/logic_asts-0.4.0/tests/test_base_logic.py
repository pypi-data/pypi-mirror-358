import operator
from functools import reduce

import pytest

import logic_asts
from logic_asts.base import Equiv, Expr, Literal, Variable


@pytest.mark.parametrize(
    ["expr", "expected"],
    [
        ("0", Literal(False)),
        ("1", Literal(True)),
        ("False", Literal(False)),
        ("True", Literal(True)),
        ("FALSE", Literal(False)),
        ("TRUE", Literal(True)),
    ],
)
def test_atoms(expr: str, expected: Expr) -> None:
    parsed = logic_asts.parse_expr(expr, syntax="base")
    assert parsed == expected, (parsed, expected)


def test_base_logic() -> None:
    expr = "(x1 <-> x2) | x3"
    expected = Equiv(Variable("x1"), Variable("x2")) | Variable("x3")
    parsed = logic_asts.parse_expr(expr, syntax="base")
    assert parsed == expected, (parsed, expected)
    assert parsed.horizon() == expected.horizon() == 0


@pytest.mark.parametrize(
    "n",
    [3, 5, 10, 20, 30, 40, 80, 100],
)
def test_parse_large_expr(n: int) -> None:
    expr = " & ".join((f"(x{i} <-> y{i})" for i in range(n)))
    expected: Expr = reduce(operator.__and__, (Equiv(Variable(f"x{i}"), Variable(f"y{i}")) for i in range(n)))
    parsed = logic_asts.parse_expr(expr, syntax="base")
    assert parsed == expected
    assert parsed.horizon() == expected.horizon() == 0


if __name__ == "__main__":
    test_atoms("0", Literal(False))
