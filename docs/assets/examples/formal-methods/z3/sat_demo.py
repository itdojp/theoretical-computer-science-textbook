"""Minimal SAT/SMT example using Z3 (Chapter 9).

Usage (example):
  python3 -m venv .venv
  . .venv/bin/activate
  pip install z3-solver
  python sat_demo.py
"""

from __future__ import annotations

from z3 import And, Bool, Not, Or, Solver, sat


def main() -> None:
    # Example 1: UNSAT (p ∧ ¬p)
    p = Bool("p")
    s1 = Solver()
    s1.add(And(p, Not(p)))
    print("[example 1] p AND (NOT p)")
    print("  result:", s1.check())

    # Example 2: small 3-SAT-style CNF from Chapter 9 exercises (SAT/UNSAT depends on constraints).
    p = Bool("p")
    q = Bool("q")
    r = Bool("r")

    cnf = And(
        Or(p, q, r),
        Or(Not(p), Not(q)),
        Or(Not(q), Not(r)),
        Or(Not(r), Not(p)),
    )

    s2 = Solver()
    s2.add(cnf)
    print("[example 2] (p ∨ q ∨ r) ∧ (¬p ∨ ¬q) ∧ (¬q ∨ ¬r) ∧ (¬r ∨ ¬p)")
    res = s2.check()
    print("  result:", res)
    if res == sat:
        print("  model:", s2.model())


if __name__ == "__main__":
    main()

