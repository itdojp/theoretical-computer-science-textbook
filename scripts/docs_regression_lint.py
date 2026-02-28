#!/usr/bin/env python3
"""Lint Markdown sources under docs/ to prevent recurring notation/format regressions.

This is a lightweight, stdlib-only checker intended for CI.

Checks (outside fenced code blocks and inline code):
- Broken list markers like "* 1." or "- 1." (bullet + ordered marker).
- LaTeX typo: "\\mathbb{R}{\\ge 0}" (should be "\\mathbb{R}_{\\ge 0}").
- Unicode sum symbol "∑" (use TeX "\\sum" inside math mode instead).
- Callout markers "〖...〗" (enforce consistent Markdown callout format).

Notes:
- docs/appendices/d.md is a symbol index that intentionally contains many Unicode
  symbols, so it is excluded by default.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path


FENCE_START_RE = re.compile(r"^\s*(```|~~~)")
INLINE_CODE_RE = re.compile(r"`[^`]*`")

BROKEN_BULLET_ORDERED_RE = re.compile(r"^\s*[*-]\s+\d+\.\s+")
MATHBB_R_GE0_TYPO_RE = re.compile(r"\\\\mathbb\{R\}\{\s*\\\\ge\s*0\s*\}")
UNICODE_SUM_RE = re.compile("∑")
CALLOUT_MARKER_RE = re.compile(r"[〖〗]")

DEFAULT_EXCLUDE = {
    "docs/appendices/d.md",  # symbol index: Unicode-heavy by design
}


def iter_markdown_files(docs_root: Path) -> list[Path]:
    return sorted(docs_root.rglob("*.md"), key=lambda p: p.as_posix())


def check_markdown(md: Path) -> list[str]:
    errors: list[str] = []
    in_fence = False

    for lineno, line in enumerate(md.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
        if FENCE_START_RE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue

        probe = INLINE_CODE_RE.sub("", line)

        if BROKEN_BULLET_ORDERED_RE.search(probe):
            errors.append(f"{md}:{lineno}: broken list marker (use ordered list, not bullet+number): {line.strip()}")

        if MATHBB_R_GE0_TYPO_RE.search(probe):
            errors.append(f"{md}:{lineno}: LaTeX typo: \\\\mathbb{{R}}{{\\\\ge 0}} (use \\\\mathbb{{R}}_{{\\\\ge 0}})")

        if UNICODE_SUM_RE.search(probe):
            errors.append(f"{md}:{lineno}: unicode sum '∑' found (use TeX \\\\sum inside math mode)")

        if CALLOUT_MARKER_RE.search(probe):
            errors.append(f"{md}:{lineno}: callout marker '〖〗' found (use consistent Markdown callout format)")

    return errors


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--docs-root", default="docs", help="Docs root directory (default: docs)")
    ap.add_argument(
        "--exclude",
        action="append",
        default=[],
        help="Exclude a repo-relative posix path (can be repeated)",
    )
    args = ap.parse_args()

    docs_root = Path(args.docs_root)
    if not docs_root.exists():
        print(f"missing: {docs_root}")
        return 2

    exclude = set(DEFAULT_EXCLUDE)
    exclude.update(args.exclude)

    errors: list[str] = []
    for md in iter_markdown_files(docs_root):
        rel = md.as_posix()
        if rel in exclude:
            continue
        errors.extend(check_markdown(md))

    if errors:
        print("docs regression lint failed:")
        for e in errors:
            print(e)
        return 1

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

