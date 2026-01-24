from __future__ import annotations

from typing import Iterable, Sequence, TypeVar

T = TypeVar("T")


class DPSolver:
    """Dynamic programming solvers (Chapter 6 exercise)."""

    def longest_common_subsequence(self, X: Sequence[T] | str, Y: Sequence[T] | str):
        """Return one longest common subsequence.

        - If X and Y are strings, returns a string.
        - Otherwise returns a list of elements.
        """

        x_list = list(X)
        y_list = list(Y)
        m, n = len(x_list), len(y_list)

        dp = [[0] * (n + 1) for _ in range(m + 1)]
        for i in range(m - 1, -1, -1):
            for j in range(n - 1, -1, -1):
                if x_list[i] == y_list[j]:
                    dp[i][j] = dp[i + 1][j + 1] + 1
                else:
                    dp[i][j] = dp[i + 1][j] if dp[i + 1][j] >= dp[i][j + 1] else dp[i][j + 1]

        i = 0
        j = 0
        out: list[T] = []
        while i < m and j < n:
            if x_list[i] == y_list[j]:
                out.append(x_list[i])
                i += 1
                j += 1
            elif dp[i + 1][j] >= dp[i][j + 1]:
                i += 1
            else:
                j += 1

        if isinstance(X, str) and isinstance(Y, str):
            return "".join(out)  # type: ignore[arg-type]
        return out

    def edit_distance(self, s1: str, s2: str) -> int:
        """Levenshtein edit distance (insert/delete/replace, cost=1)."""

        m, n = len(s1), len(s2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]

        for i in range(m + 1):
            dp[i][0] = i
        for j in range(n + 1):
            dp[0][j] = j

        for i in range(1, m + 1):
            for j in range(1, n + 1):
                cost = 0 if s1[i - 1] == s2[j - 1] else 1
                dp[i][j] = min(
                    dp[i - 1][j] + 1,  # delete
                    dp[i][j - 1] + 1,  # insert
                    dp[i - 1][j - 1] + cost,  # replace
                )

        return dp[m][n]

    def knapsack(self, weights: Sequence[int], values: Sequence[int], capacity: int) -> int:
        """0/1 knapsack: return the maximum achievable value."""

        if capacity < 0:
            raise ValueError("capacity must be non-negative")
        if len(weights) != len(values):
            raise ValueError("weights and values must have the same length")

        dp = [0] * (capacity + 1)
        for w, v in zip(weights, values):
            if w < 0 or v < 0:
                raise ValueError("weights/values must be non-negative")
            for c in range(capacity, w - 1, -1):
                cand = dp[c - w] + v
                if cand > dp[c]:
                    dp[c] = cand
        return dp[capacity]

    def matrix_chain_multiplication(self, dimensions: Sequence[int]) -> int:
        """Minimum number of scalar multiplications for matrix chain product.

        `dimensions` is a list of length n+1 for n matrices:
          A1: d0 x d1, A2: d1 x d2, ..., An: d(n-1) x dn
        """

        if len(dimensions) < 2:
            return 0
        if any(d <= 0 for d in dimensions):
            raise ValueError("all dimensions must be positive")

        n = len(dimensions) - 1
        m = [[0] * n for _ in range(n)]

        for chain_len in range(2, n + 1):
            for i in range(0, n - chain_len + 1):
                j = i + chain_len - 1
                best = None
                for k in range(i, j):
                    cost = (
                        m[i][k]
                        + m[k + 1][j]
                        + dimensions[i] * dimensions[k + 1] * dimensions[j + 1]
                    )
                    if best is None or cost < best:
                        best = cost
                m[i][j] = 0 if best is None else best

        return m[0][n - 1]

