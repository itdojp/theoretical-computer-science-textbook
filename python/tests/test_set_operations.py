from __future__ import annotations

from itertools import product

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from tcs_exercises.set_operations import SetOperations


@given(
    a=st.sets(st.integers(min_value=-50, max_value=50), max_size=30),
    b=st.sets(st.integers(min_value=-50, max_value=50), max_size=30),
)
@settings(max_examples=200)
def test_union_intersection_difference_match_builtin(a: set[int], b: set[int]) -> None:
    so = SetOperations(a)
    assert so.union(b) == a | b
    assert so.intersection(b) == a & b
    assert so.difference(b) == a - b


@given(a=st.sets(st.integers(min_value=-10, max_value=10), max_size=10))
@settings(max_examples=100)
def test_power_set_basic_properties(a: set[int]) -> None:
    ps = SetOperations(a).power_set()

    # Cardinality of the powerset: 2^n
    assert len(ps) == 2 ** len(a)

    # Contains empty set and the set itself
    assert frozenset() in ps
    assert frozenset(a) in ps

    # Every subset is a subset of the original
    for subset in ps:
        assert set(subset).issubset(a)


@given(
    a=st.sets(st.integers(min_value=-20, max_value=20), max_size=12),
    b=st.sets(st.integers(min_value=-20, max_value=20), max_size=12),
)
@settings(max_examples=100)
def test_cartesian_product_matches_builtin(a: set[int], b: set[int]) -> None:
    so = SetOperations(a)
    got = so.cartesian_product(b)
    expected = set(product(a, b))
    assert got == expected


def test_accepts_set_operations_as_argument() -> None:
    a = SetOperations([1, 2])
    b = SetOperations([2, 3])
    assert a.union(b) == {1, 2, 3}

