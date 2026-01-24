from __future__ import annotations

from collections import deque

from hypothesis import given, settings
from hypothesis import strategies as st

from tcs_exercises.union_find import UnionFind


def _normalize_components(comps: list[set[int]]) -> set[frozenset[int]]:
    return {frozenset(c) for c in comps}


def _bfs_components(n: int, edges: list[tuple[int, int]]) -> list[set[int]]:
    adj: list[list[int]] = [[] for _ in range(n)]
    for a, b in edges:
        if a == b:
            continue
        adj[a].append(b)
        adj[b].append(a)

    seen = [False] * n
    out: list[set[int]] = []
    for i in range(n):
        if seen[i]:
            continue
        q: deque[int] = deque([i])
        seen[i] = True
        comp: set[int] = {i}
        while q:
            u = q.popleft()
            for v in adj[u]:
                if not seen[v]:
                    seen[v] = True
                    comp.add(v)
                    q.append(v)
        out.append(comp)
    return out


def _uf_components(uf: UnionFind) -> list[set[int]]:
    n = len(uf.parent)
    groups: dict[int, set[int]] = {}
    for i in range(n):
        r = uf.find_with_path_compression(i)
        groups.setdefault(r, set()).add(i)
    return list(groups.values())


@given(
    n=st.integers(min_value=1, max_value=30),
    pairs=st.lists(
        st.tuples(st.integers(min_value=0, max_value=200), st.integers(min_value=0, max_value=200)),
        max_size=200,
    ),
)
@settings(max_examples=100)
def test_union_find_matches_bfs_components(n: int, pairs: list[tuple[int, int]]) -> None:
    uf = UnionFind(n)
    edges: list[tuple[int, int]] = []
    for a, b in pairs:
        a %= n
        b %= n
        uf.union_by_rank(a, b)
        edges.append((a, b))

    assert _normalize_components(_uf_components(uf)) == _normalize_components(_bfs_components(n, edges))


@given(
    n=st.integers(min_value=1, max_value=30),
    pairs=st.lists(
        st.tuples(st.integers(min_value=0, max_value=200), st.integers(min_value=0, max_value=200)),
        max_size=200,
    ),
)
@settings(max_examples=50)
def test_path_compression_does_not_change_partition(n: int, pairs: list[tuple[int, int]]) -> None:
    uf = UnionFind(n)
    edges: list[tuple[int, int]] = []
    for a, b in pairs:
        a %= n
        b %= n
        uf.union_by_rank(a, b)
        edges.append((a, b))

    before = _normalize_components(_uf_components(uf))
    for i in range(n):
        _ = uf.find_with_path_compression(i)
    after = _normalize_components(_uf_components(uf))
    assert before == after

