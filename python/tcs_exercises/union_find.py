from __future__ import annotations

from time import perf_counter
from typing import Iterable, Literal


Operation = tuple[Literal["find"], int] | tuple[Literal["union"], int, int]


class UnionFind:
    """Union-Find with path compression + union by rank (Chapter 7 exercise)."""

    def __init__(self, n: int):
        if n < 0:
            raise ValueError("n must be non-negative")
        self.parent = list(range(n))
        self.rank = [0] * n

    def find_with_path_compression(self, x: int) -> int:
        if self.parent[x] != x:
            self.parent[x] = self.find_with_path_compression(self.parent[x])
        return self.parent[x]

    def union_by_rank(self, x: int, y: int) -> int:
        rx = self.find_with_path_compression(x)
        ry = self.find_with_path_compression(y)
        if rx == ry:
            return rx

        if self.rank[rx] < self.rank[ry]:
            self.parent[rx] = ry
            return ry
        if self.rank[rx] > self.rank[ry]:
            self.parent[ry] = rx
            return rx

        self.parent[ry] = rx
        self.rank[rx] += 1
        return rx

    def analyze_amortized_complexity(self, operations: Iterable[Operation]) -> dict[str, float]:
        """A small helper for the exercise: run operations and measure wall time.

        This is not a formal amortized analysis. It is meant for "experimental verification"
        in the context of the textbook exercise.
        """

        start = perf_counter()
        count = 0
        for op in operations:
            if not op:
                continue
            if op[0] == "find":
                _, x = op
                _ = self.find_with_path_compression(x)
                count += 1
            elif op[0] == "union":
                _, x, y = op
                _ = self.union_by_rank(x, y)
                count += 1
            else:
                raise ValueError(f"unknown op: {op!r}")
        elapsed = perf_counter() - start
        return {"operations": float(count), "elapsed_seconds": float(elapsed)}
