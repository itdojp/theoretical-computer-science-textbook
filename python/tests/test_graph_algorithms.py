from __future__ import annotations

import math
from collections import deque
from itertools import combinations

from hypothesis import given, settings
from hypothesis import strategies as st

from tcs_exercises.graph_algorithms import GraphAlgorithms


def _bellman_ford(graph: dict[int, dict[int, int]], source: int) -> dict[int, float]:
    nodes = set(graph.keys())
    for u, nbrs in graph.items():
        nodes.add(u)
        nodes.update(nbrs.keys())
    nodes.add(source)

    dist = {v: math.inf for v in nodes}
    dist[source] = 0.0

    edges: list[tuple[int, int, int]] = []
    for u, nbrs in graph.items():
        for v, w in nbrs.items():
            edges.append((u, v, w))

    for _ in range(len(nodes) - 1):
        changed = False
        for u, v, w in edges:
            if dist[u] is math.inf:
                continue
            nd = dist[u] + float(w)
            if nd < dist[v]:
                dist[v] = nd
                changed = True
        if not changed:
            break

    return dist


def _connected_components(n: int, undirected_edges: list[tuple[int, int]]) -> list[set[int]]:
    adj = [[] for _ in range(n)]
    for a, b in undirected_edges:
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
        comp = {i}
        while q:
            u = q.popleft()
            for v in adj[u]:
                if not seen[v]:
                    seen[v] = True
                    comp.add(v)
                    q.append(v)
        out.append(comp)
    return out


def _is_connected(n: int, edges: list[tuple[int, int]]) -> bool:
    return len(_connected_components(n, edges)) == 1


def _brute_mst_weight(n: int, edges: list[tuple[int, int, int]]) -> float:
    # Enumerate all subsets of edges of size n-1; feasible only for small n.
    best = math.inf
    for subset in combinations(edges, n - 1):
        undirected = [(a, b) for a, b, _ in subset]
        if not _is_connected(n, undirected):
            continue
        # A connected undirected graph with n-1 edges is a tree.
        w = sum(float(w) for _, _, w in subset)
        if w < best:
            best = w
    return best


def _min_cut_capacity(
    n: int, caps: dict[int, dict[int, int]], source: int, sink: int
) -> float:
    nodes = list(range(n))
    best = math.inf
    for mask in range(1 << n):
        if not (mask & (1 << source)):
            continue
        if mask & (1 << sink):
            continue
        s_set = {i for i in nodes if mask & (1 << i)}
        cut = 0.0
        for u in s_set:
            for v, cap in caps.get(u, {}).items():
                if v not in s_set:
                    cut += float(cap)
        best = min(best, cut)
    return best


@given(
    n=st.integers(min_value=2, max_value=7),
    data=st.data(),
)
@settings(max_examples=80, deadline=None)
def test_dijkstra_matches_bellman_ford(n: int, data: st.DataObject) -> None:
    graph: dict[int, dict[int, int]] = {i: {} for i in range(n)}
    for u in range(n):
        for v in range(n):
            if u == v:
                continue
            if data.draw(st.booleans()):
                graph[u][v] = data.draw(st.integers(min_value=0, max_value=10))

    algo = GraphAlgorithms()
    got = algo.dijkstra(graph, 0)
    exp = _bellman_ford(graph, 0)
    assert got == exp


@given(n=st.integers(min_value=2, max_value=7), data=st.data())
@settings(max_examples=60, deadline=None)
def test_mst_kruskal_equals_prim_and_is_minimal(n: int, data: st.DataObject) -> None:
    # Build a connected undirected graph: start from a random tree, then add extra edges.
    edges: list[tuple[int, int, int]] = []
    for v in range(1, n):
        u = data.draw(st.integers(min_value=0, max_value=v - 1))
        w = data.draw(st.integers(min_value=1, max_value=10))
        edges.append((u, v, w))

    extra = data.draw(st.lists(st.tuples(st.integers(0, n - 1), st.integers(0, n - 1)), max_size=10))
    for a, b in extra:
        if a == b:
            continue
        if a > b:
            a, b = b, a
        w = data.draw(st.integers(min_value=1, max_value=10))
        edges.append((a, b, w))

    graph: dict[int, dict[int, int]] = {i: {} for i in range(n)}
    for a, b, w in edges:
        # Keep the minimum weight if multiple edges exist.
        graph[a][b] = min(graph[a].get(b, w), w)
        graph[b][a] = min(graph[b].get(a, w), w)

    algo = GraphAlgorithms()
    w_kr, e_kr = algo.minimum_spanning_tree(graph, algorithm="kruskal")
    w_pr, e_pr = algo.minimum_spanning_tree(graph, algorithm="prim")

    assert w_kr == w_pr
    assert len(e_kr) == n - 1
    assert len(e_pr) == n - 1

    # Minimality check via brute force (n<=7).
    unique_edges = []
    seen = set()
    for a, b, w in edges:
        key = (min(a, b), max(a, b))
        if key in seen:
            continue
        seen.add(key)
        unique_edges.append((key[0], key[1], graph[key[0]][key[1]]))
    assert w_kr == _brute_mst_weight(n, unique_edges)


@given(n=st.integers(min_value=2, max_value=7), data=st.data())
@settings(max_examples=80, deadline=None)
def test_scc_matches_reachability_partition(n: int, data: st.DataObject) -> None:
    graph: dict[int, dict[int, int]] = {i: {} for i in range(n)}
    for u in range(n):
        for v in range(n):
            if u == v:
                continue
            if data.draw(st.booleans()):
                graph[u][v] = 1

    def reachable(u: int) -> set[int]:
        q: deque[int] = deque([u])
        seen = {u}
        while q:
            x = q.popleft()
            for y in graph.get(x, {}).keys():
                if y not in seen:
                    seen.add(y)
                    q.append(y)
        return seen

    reach = {u: reachable(u) for u in range(n)}
    # Build SCCs by equivalence relation: u~v iff mutually reachable.
    unused = set(range(n))
    scc_ref: list[set[int]] = []
    while unused:
        u = next(iter(unused))
        comp = {v for v in unused if (v in reach[u] and u in reach[v])}
        scc_ref.append(comp)
        unused -= comp

    algo = GraphAlgorithms()
    scc = algo.strongly_connected_components(graph)

    assert {frozenset(c) for c in scc} == {frozenset(c) for c in scc_ref}


@given(n=st.integers(min_value=2, max_value=7), data=st.data())
@settings(max_examples=60, deadline=None)
def test_max_flow_equals_min_cut_on_small_graphs(n: int, data: st.DataObject) -> None:
    source = 0
    sink = n - 1
    caps: dict[int, dict[int, int]] = {i: {} for i in range(n)}
    for u in range(n):
        for v in range(n):
            if u == v:
                continue
            if data.draw(st.booleans()):
                caps[u][v] = data.draw(st.integers(min_value=0, max_value=10))

    algo = GraphAlgorithms()
    got = algo.max_flow(caps, source, sink)
    expected = _min_cut_capacity(n, caps, source, sink)
    assert got == expected

