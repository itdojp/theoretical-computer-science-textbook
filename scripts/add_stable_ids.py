#!/usr/bin/env python3
"""Add kramdown stable IDs for numbered statements (definitions/theorems/examples).

This repository uses kramdown (GFM) via Jekyll. kramdown supports adding an
inline attribute list (IAL) after a block to assign an `id` that becomes a
stable anchor in the rendered HTML.

This script scans Markdown files and inserts a line like:
  {: #thm-9-3 }
right after a line like:
  **定理 9.3**（コンパクト性定理）

It is intended to be deterministic and safe to re-run (idempotent).
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path


KIND_TO_PREFIX = {
    "定義": "def",
    "定理": "thm",
    "補題": "lem",
    "命題": "prop",
    "系": "cor",
    "例": "ex",
}

LABEL_RE = re.compile(
    r"^(?P<indent>\s*)\*\*(?P<kind>定義|定理|補題|命題|系|例)\s+(?P<num>\d+(?:\.\d+)+)\*\*(?P<rest>.*)$"
)

IAL_RE = re.compile(r"^\s*\{:\s*#(?P<id>[A-Za-z0-9_-]+)\s*\}\s*$")


def compute_id(kind: str, num: str) -> str:
    prefix = KIND_TO_PREFIX[kind]
    return f"{prefix}-{num.replace('.', '-')}"


def process_file(path: Path) -> bool:
    original = path.read_text(encoding="utf-8").splitlines(keepends=True)
    out: list[str] = []
    changed = False

    i = 0
    while i < len(original):
        line = original[i]
        m = LABEL_RE.match(line.rstrip("\n"))
        out.append(line)

        if not m:
            i += 1
            continue

        stmt_id = compute_id(m.group("kind"), m.group("num"))
        indent = m.group("indent")

        next_line = original[i + 1] if i + 1 < len(original) else ""
        if IAL_RE.match(next_line.rstrip("\n")):
            # Already has an IAL. Keep as-is.
            i += 1
            continue

        out.append(f"{indent}{{: #{stmt_id} }}\n")
        changed = True
        i += 1

    if changed:
        path.write_text("".join(out), encoding="utf-8")
    return changed


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "roots",
        nargs="+",
        help="Root directories to scan (e.g. docs src). Only *.md files are processed.",
    )
    args = ap.parse_args()

    any_changed = False
    for root_str in args.roots:
        root = Path(root_str)
        if not root.exists():
            raise SystemExit(f"root does not exist: {root}")
        for md in sorted(root.rglob("*.md")):
            any_changed |= process_file(md)

    print("changed" if any_changed else "no changes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

