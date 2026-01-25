#!/usr/bin/env python3
"""Lightweight notation linter for Markdown.

Goal: prevent re-introducing a few high-signal notation inconsistencies.
This is intentionally narrow (regex-based, stdlib only) to keep CI stable.
"""

from __future__ import annotations

import argparse
from pathlib import Path


BAD_SUBSTRINGS = [
    # Power set notation: keep it consistent with the guide (Appendix A).
    ("𝒫(", "Use P(A) for power set notation (avoid Unicode 𝒫)."),
    ("𝒫（", "Use P(A) for power set notation (avoid Unicode 𝒫)."),
    ("𝒫{", "Use P(A) for power set notation (avoid Unicode 𝒫)."),
    # Minus sign in prose math: prefer U+2212 with surrounding spaces.
    ("|V| -", "Use U+2212 minus with spaces: |V| − ... (not |V| - ...)."),
    ("|E| -", "Use U+2212 minus with spaces: |E| − ... (not |E| - ...)."),
    ("|F| -", "Use U+2212 minus with spaces: |F| − ... (not |F| - ...)."),
    ("|V|−", "Add spaces around minus: |V| − ... (not |V|−...)."),
    ("|E|−", "Add spaces around minus: |E| − ... (not |E|−...)."),
    ("|F|−", "Add spaces around minus: |F| − ... (not |F|−...)."),
]


def iter_markdown_files(roots: list[Path]) -> list[Path]:
    out: list[Path] = []
    for root in roots:
        for p in root.rglob("*.md"):
            # Ignore Jekyll internal directories (e.g. docs/_includes) even if *.md appears.
            if any(part.startswith("_") for part in p.relative_to(root).parts):
                continue
            out.append(p)
    return sorted(out, key=lambda p: p.as_posix())


def check_file(path: Path) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8")

    in_fence = False
    for lineno, raw in enumerate(text.splitlines(), start=1):
        line = raw.rstrip("\n")

        # Skip fenced code blocks.
        stripped = line.lstrip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue

        for bad, msg in BAD_SUBSTRINGS:
            if bad in line:
                errors.append(f"{path}:{lineno}: {msg} (found: {bad})")

    return errors


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "roots",
        nargs="*",
        default=["docs", "src"],
        help="Root directories to scan (default: docs src)",
    )
    args = ap.parse_args()

    roots = [Path(r) for r in args.roots]
    missing = [r.as_posix() for r in roots if not r.exists()]
    if missing:
        print("missing roots:")
        for m in missing:
            print(f"- {m}")
        return 2

    all_errors: list[str] = []
    for md in iter_markdown_files(roots):
        all_errors.extend(check_file(md))

    if all_errors:
        print("notation lint failed:")
        for e in all_errors:
            print(e)
        return 1

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

