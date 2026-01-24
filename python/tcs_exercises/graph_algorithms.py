from __future__ import annotations

import heapq
import math
from collections import deque
from typing import Hashable, Iterable, Mapping, MutableMapping


Node = Hashable
WeightedGraph = Mapping[Node, Mapping[Node, float]]


class GraphAlgorithms:
    """Graph algorithms (Chapter 8 exercise).

    Graph representation:
      graph[u][v] = weight (for shortest path / MST) or capacity (for max flow)
    """

    @staticmethod
    def _nodes(graph: Mapping[Node, Mapping[Node, float]]) -> set[Node]:
        nodes: set[Node] = set(graph.keys())
        for u, nbrs in graph.items():
            nodes.update(nbrs.keys())
        return nodes

    def dijkstra(self, graph: WeightedGraph, source: Node) -> dict[Node, float]:
        """Dijkstra shortest paths from `source` (non-negative weights)."""

        nodes = self._nodes(graph)
        nodes.add(source)

        dist: dict[Node, float] = {v: math.inf for v in nodes}
        dist[source] = 0.0

        pq: list[tuple[float, Node]] = [(0.0, source)]
        while pq:
            d, u = heapq.heappop(pq)
            if d != dist[u]:
                continue
            for v, w in graph.get(u, {}).items():
                if w < 0:
                    raise ValueError("Dijkstra requires non-negative weights")
                nd = d + float(w)
                if nd < dist.get(v, math.inf):
                    dist[v] = nd
                    heapq.heappush(pq, (nd, v))

        return dist

    def max_flow(self, graph: WeightedGraph, source: Node, sink: Node) -> float:
        """Maximum s-t flow (Edmonds-Karp) for non-negative capacities."""

        if source == sink:
            return 0.0

        nodes = self._nodes(graph)
        nodes.add(source)
        nodes.add(sink)

        residual: dict[Node, dict[Node, float]] = {u: {} for u in nodes}
        for u, nbrs in graph.items():
            for v, cap in nbrs.items():
                if cap < 0:
                    raise ValueError("capacity must be non-negative")
                residual[u][v] = residual[u].get(v, 0.0) + float(cap)
                residual.setdefault(v, {}).setdefault(u, 0.0)

        max_flow_value = 0.0

        while True:
            parent: dict[Node, Node | None] = {source: None}
            q: deque[Node] = deque([source])

            while q and sink not in parent:
                u = q.popleft()
                for v, cap in residual.get(u, {}).items():
                    if v in parent:
                        continue
                    if cap <= 0:
                        continue
                    parent[v] = u
                    q.append(v)

            if sink not in parent:
                break

            # Find bottleneck
            bottleneck = math.inf
            v = sink
            while parent[v] is not None:
                u = parent[v]
                bottleneck = min(bottleneck, residual[u][v])
                v = u

            # Augment
            v = sink
            while parent[v] is not None:
                u = parent[v]
                residual[u][v] -= bottleneck
                residual[v][u] = residual.get(v, {}).get(u, 0.0) + bottleneck
                v = u

            max_flow_value += bottleneck

        return max_flow_value

    def minimum_spanning_tree(
        self, graph: WeightedGraph, algorithm: str = "kruskal"
    ) -> tuple[float, list[tuple[Node, Node, float]]]:
        """Minimum spanning tree for an undirected connected graph.

        Returns (total_weight, edges).
        """

        nodes = sorted(self._nodes(graph), key=repr)
        if not nodes:
            return 0.0, []

        algo = algorithm.lower()
        if algo not in {"kruskal", "prim"}:
            raise ValueError("algorithm must be 'kruskal' or 'prim'")

        if algo == "kruskal":
            return self._mst_kruskal(graph, nodes)
        return self._mst_prim(graph, nodes)

    def _mst_kruskal(
        self, graph: WeightedGraph, nodes: list[Node]
    ) -> tuple[float, list[tuple[Node, Node, float]]]:
        idx = {v: i for i, v in enumerate(nodes)}
        parent = list(range(len(nodes)))
        rank = [0] * len(nodes)

        def find(i: int) -> int:
            while parent[i] != i:
                parent[i] = parent[parent[i]]
                i = parent[i]
            return i

        def union(i: int, j: int) -> bool:
            ri = find(i)
            rj = find(j)
            if ri == rj:
                return False
            if rank[ri] < rank[rj]:
                parent[ri] = rj
            elif rank[ri] > rank[rj]:
                parent[rj] = ri
            else:
                parent[rj] = ri
                rank[ri] += 1
            return True

        edges_seen: dict[frozenset[Node], tuple[Node, Node, float]] = {}
        for u, nbrs in graph.items():
            for v, w in nbrs.items():
                if u == v:
                    continue
                key = frozenset({u, v})
                cur = edges_seen.get(key)
                if cur is None or w < cur[2]:
                    edges_seen[key] = (u, v, float(w))

        edges = sorted(edges_seen.values(), key=lambda e: e[2])
        out: list[tuple[Node, Node, float]] = []
        total = 0.0
        for u, v, w in edges:
            if union(idx[u], idx[v]):
                out.append((u, v, w))
                total += w
                if len(out) == len(nodes) - 1:
                    break

        if len(out) != len(nodes) - 1:
            raise ValueError("graph must be connected (undirected) for MST")
        return total, out

    def _mst_prim(
        self, graph: WeightedGraph, nodes: list[Node]
    ) -> tuple[float, list[tuple[Node, Node, float]]]:
        start = nodes[0]
        visited: set[Node] = {start}
        pq: list[tuple[float, Node, Node]] = []

        for v, w in graph.get(start, {}).items():
            if v != start:
                heapq.heappush(pq, (float(w), start, v))

        out: list[tuple[Node, Node, float]] = []
        total = 0.0

        while pq and len(visited) < len(nodes):
            w, u, v = heapq.heappop(pq)
            if v in visited:
                continue
            visited.add(v)
            out.append((u, v, w))
            total += w
            for nxt, ww in graph.get(v, {}).items():
                if nxt not in visited and nxt != v:
                    heapq.heappush(pq, (float(ww), v, nxt))

        if len(visited) != len(nodes) or len(out) != len(nodes) - 1:
            raise ValueError("graph must be connected (undirected) for MST")
        return total, out

    def strongly_connected_components(self, graph: Mapping[Node, object]) -> list[set[Node]]:
        """Strongly connected components (Tarjan).

        The adjacency may be:
          - dict[node, dict[neighbor, weight]]
          - dict[node, list/tuple/set of neighbors]
        """

        def neighbors(u: Node) -> Iterable[Node]:
            nbrs = graph.get(u, {})
            if isinstance(nbrs, Mapping):
                return nbrs.keys()
            return nbrs  # type: ignore[return-value]

        nodes: set[Node] = set(graph.keys())
        for u in list(nodes):
            for v in neighbors(u):
                nodes.add(v)

        index = 0
        stack: list[Node] = []
        on_stack: set[Node] = set()
        indices: dict[Node, int] = {}
        lowlink: dict[Node, int] = {}
        sccs: list[set[Node]] = []

        def strongconnect(v: Node) -> None:
            nonlocal index
            indices[v] = index
            lowlink[v] = index
            index += 1
            stack.append(v)
            on_stack.add(v)

            for w in neighbors(v):
                if w not in indices:
                    strongconnect(w)
                    lowlink[v] = min(lowlink[v], lowlink[w])
                elif w in on_stack:
                    lowlink[v] = min(lowlink[v], indices[w])

            if lowlink[v] == indices[v]:
                comp: set[Node] = set()
                while True:
                    w = stack.pop()
                    on_stack.remove(w)
                    comp.add(w)
                    if w == v:
                        break
                sccs.append(comp)

        for v in nodes:
            if v not in indices:
                strongconnect(v)

        return sccs
