#!/usr/bin/env python3
"""Lightweight notation linter for Markdown.

Goal: prevent re-introducing a few high-signal notation inconsistencies.
This is intentionally narrow (regex-based, stdlib only) to keep CI stable.
"""

from __future__ import annotations

import argparse
import re
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

INLINE_CODE_RE = re.compile(r"`[^`]+`")

# Markdown table separator line, e.g.:
# |---|---:|:---|
TABLE_SEPARATOR_RE = re.compile(r"^\s*\|?(?:\s*:?-{3,}:?\s*\|)+\s*:?-{3,}:?\s*\|?\s*$")

BAD_REGEXES: list[tuple[re.Pattern[str], str]] = [
    # Avoid combining overline/macron characters like "L̄" or "L̅".
    (
        re.compile(r"[A-Za-z]\u0304|[A-Za-z]\u0305"),
        "Avoid combining overline/macron characters (use TeX like \\overline{L}).",
    ),
    # Avoid raw |...| for cardinality/length/absolute value, because it easily collides with Markdown tables.
    (
        re.compile(r"\|[^\s|]+\|"),
        "Avoid raw |...| (use TeX like \\lvert A\\rvert).",
    ),
]

def contains_raw_bar_inside_braces(line: str) -> bool:
    """Detect a literal '|' that appears inside a {...} segment.

    We intentionally ignore Liquid templates like {{ ... }} and {% ... %}.
    This catches set-builder-style notation like {x | P(x)} even when the braces
    contain nested set literals (e.g. {w ∈ {0,1}* | ...}).
    """

    i = 0
    depth = 0
    n = len(line)
    while i < n:
        if line.startswith("{{", i):
            end = line.find("}}", i + 2)
            if end == -1:
                return False
            i = end + 2
            continue
        if line.startswith("{%", i):
            end = line.find("%}", i + 2)
            if end == -1:
                return False
            i = end + 2
            continue

        ch = line[i]
        # Skip escaped braces used in TeX like \{ and \}.
        if ch == "\\" and i + 1 < n and line[i + 1] in "{}":
            i += 2
            continue

        if ch == "{":
            depth += 1
        elif ch == "}":
            if depth > 0:
                depth -= 1
        elif ch == "|" and depth > 0:
            return True
        i += 1
    return False


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

        # Remove inline code spans for linting.
        line_no_code = INLINE_CODE_RE.sub(" ", line)

        # Skip Markdown table separator lines.
        if TABLE_SEPARATOR_RE.match(line_no_code):
            continue

        # Regex examples should be written in inline code to avoid Markdown emphasis eating '*'.
        # We scope this narrowly to lines that mention regular expressions.
        if "正規表現" in line_no_code and re.search(r"[0-9A-Za-z)\]]\*(?!\*)", line_no_code):
            errors.append(
                f"{path}:{lineno}: Put regex examples in inline code to preserve '*' "
                f"(e.g. `b*(ab)*`)."
            )

        if contains_raw_bar_inside_braces(line_no_code):
            errors.append(
                f"{path}:{lineno}: Avoid raw '|' inside braces like {{x | ...}} "
                f"(use TeX like \\mid)."
            )

        for bad, msg in BAD_SUBSTRINGS:
            if bad in line_no_code:
                errors.append(f"{path}:{lineno}: {msg} (found: {bad})")

        for rx, msg in BAD_REGEXES:
            m = rx.search(line_no_code)
            if m:
                errors.append(f"{path}:{lineno}: {msg} (found: {m.group(0)})")

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
