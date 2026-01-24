from __future__ import annotations

from itertools import combinations

from hypothesis import given, settings
from hypothesis import strategies as st

from tcs_exercises.dp import DPSolver


def _is_subsequence(sub: str, s: str) -> bool:
    it = iter(s)
    return all(ch in it for ch in sub)


def _brute_lcs_length(a: str, b: str) -> int:
    # Brute-force over subsequences of the shorter string.
    short, other = (a, b) if len(a) <= len(b) else (b, a)
    best = 0
    for r in range(len(short) + 1):
        for idxs in combinations(range(len(short)), r):
            cand = "".join(short[i] for i in idxs)
            if _is_subsequence(cand, other):
                best = max(best, len(cand))
    return best


def _brute_knapsack(weights: list[int], values: list[int], capacity: int) -> int:
    n = len(weights)
    best = 0
    for mask in range(1 << n):
        tw = 0
        tv = 0
        for i in range(n):
            if mask & (1 << i):
                tw += weights[i]
                tv += values[i]
        if tw <= capacity:
            best = max(best, tv)
    return best


def _brute_matrix_chain(dimensions: list[int]) -> int:
    if len(dimensions) < 2:
        return 0

    from functools import lru_cache

    n = len(dimensions) - 1

    @lru_cache(maxsize=None)
    def solve(i: int, j: int) -> int:
        if i == j:
            return 0
        best = None
        for k in range(i, j):
            cost = (
                solve(i, k)
                + solve(k + 1, j)
                + dimensions[i] * dimensions[k + 1] * dimensions[j + 1]
            )
            if best is None or cost < best:
                best = cost
        return 0 if best is None else best

    return solve(0, n - 1)


def test_lcs_known_example() -> None:
    solver = DPSolver()
    assert solver.longest_common_subsequence("ABCBDAB", "BDCABA") in {"BCBA", "BDAB", "BCAB"}


@given(a=st.text(alphabet="abc", max_size=8), b=st.text(alphabet="abc", max_size=8))
@settings(max_examples=100, deadline=None)
def test_lcs_matches_bruteforce_length(a: str, b: str) -> None:
    solver = DPSolver()
    lcs = solver.longest_common_subsequence(a, b)
    assert _is_subsequence(lcs, a)
    assert _is_subsequence(lcs, b)
    assert len(lcs) == _brute_lcs_length(a, b)


def test_edit_distance_known_examples() -> None:
    solver = DPSolver()
    assert solver.edit_distance("kitten", "sitting") == 3
    assert solver.edit_distance("", "") == 0
    assert solver.edit_distance("a", "") == 1


@given(a=st.text(alphabet="abc", max_size=10), b=st.text(alphabet="abc", max_size=10))
@settings(max_examples=100, deadline=None)
def test_edit_distance_basic_properties(a: str, b: str) -> None:
    solver = DPSolver()
    d_ab = solver.edit_distance(a, b)
    d_ba = solver.edit_distance(b, a)
    assert d_ab == d_ba
    assert solver.edit_distance(a, a) == 0
    assert solver.edit_distance(a, "") == len(a)
    assert solver.edit_distance("", b) == len(b)
    assert d_ab >= abs(len(a) - len(b))


@given(
    n=st.integers(min_value=0, max_value=10),
    weights=st.lists(st.integers(min_value=1, max_value=10), min_size=0, max_size=10),
    values=st.lists(st.integers(min_value=0, max_value=20), min_size=0, max_size=10),
    cap=st.integers(min_value=0, max_value=30),
)
@settings(max_examples=100, deadline=None)
def test_knapsack_matches_bruteforce(
    n: int, weights: list[int], values: list[int], cap: int
) -> None:
    # Keep arrays aligned and small.
    weights = weights[:n]
    values = values[:n]
    if len(values) < len(weights):
        values += [0] * (len(weights) - len(values))
    if len(weights) < len(values):
        weights += [1] * (len(values) - len(weights))

    solver = DPSolver()
    got = solver.knapsack(weights, values, cap)
    expected = _brute_knapsack(weights, values, cap)
    assert got == expected


@given(
    dims=st.lists(st.integers(min_value=1, max_value=10), min_size=2, max_size=7),
)
@settings(max_examples=80, deadline=None)
def test_matrix_chain_matches_bruteforce(dims: list[int]) -> None:
    solver = DPSolver()
    assert solver.matrix_chain_multiplication(dims) == _brute_matrix_chain(dims)

