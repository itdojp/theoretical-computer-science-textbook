from __future__ import annotations

from itertools import combinations
from typing import FrozenSet, Hashable, Iterable, TypeVar

T = TypeVar("T", bound=Hashable)
U = TypeVar("U", bound=Hashable)


class SetOperations:
    """Basic set operations (Chapter 1 implementation exercise).

    The methods return Python built-in types to keep the API simple:
    - union / intersection / difference: `set`
    - power_set: `set[frozenset]` (hashable representation of subsets)
    - cartesian_product: `set[tuple]`
    """

    def __init__(self, elements: Iterable[T]):
        self.elements: set[T] = set(elements)

    @staticmethod
    def _coerce(other_set: "SetOperations[T] | Iterable[T]") -> set[T]:
        if isinstance(other_set, SetOperations):
            return set(other_set.elements)
        return set(other_set)

    def union(self, other_set: "SetOperations[T] | Iterable[T]") -> set[T]:
        return self.elements | self._coerce(other_set)

    def intersection(self, other_set: "SetOperations[T] | Iterable[T]") -> set[T]:
        return self.elements & self._coerce(other_set)

    def difference(self, other_set: "SetOperations[T] | Iterable[T]") -> set[T]:
        return self.elements - self._coerce(other_set)

    def power_set(self) -> set[FrozenSet[T]]:
        elems = list(self.elements)
        result: set[FrozenSet[T]] = set()
        for r in range(len(elems) + 1):
            for comb in combinations(elems, r):
                result.add(frozenset(comb))
        return result

    def cartesian_product(self, other_set: "SetOperations[U] | Iterable[U]") -> set[tuple[T, U]]:
        other = other_set.elements if isinstance(other_set, SetOperations) else set(other_set)
        return {(a, b) for a in self.elements for b in other}

