#!/usr/bin/env python3
"""Heuristic checks on generated HTML to prevent notation regressions.

This runs *after* the Jekyll build and checks that:
- MathJax is present (TeX rendering is enabled).
- Combining overline/macron characters (e.g. "L̄") do not leak into HTML.
- Raw |...| (cardinality/length style) does not appear in rendered prose.

Notes:
- We strip <pre>/<code> blocks before scanning so literal examples don't fail.
- This is intentionally lightweight (stdlib only) to keep CI stable.
"""

from __future__ import annotations

import argparse
import html
import re
from pathlib import Path


SCRUB_RE = re.compile(
    r"(?is)<pre\b.*?>.*?</pre>|<code\b.*?>.*?</code>|<script\b.*?>.*?</script>|<style\b.*?>.*?</style>"
)
TAG_RE = re.compile(r"(?is)<[^>]+>")
WS_RE = re.compile(r"\s+")

RAW_BARS_RE = re.compile(r"\|[^\s|]+\|")
RAW_SET_BUILDER_RE = re.compile(r"\{[^{}]*\|[^{}]*\}")
RAW_DOUBLE_PIPE_RE = re.compile(r"\|\|")
COMBINING_OVERLINE_RE = re.compile(r"[A-Za-z]\u0304|[A-Za-z]\u0305")
MATHJAX_RE = re.compile(r"mathjax@3|tex-chtml\.js")

VAR_RE = r"[A-Za-z][A-Za-z0-9]*"
VAR_ASSIGN_RE = rf"{VAR_RE}(?:=[^)\s]+)?"
I_FIRST_RE = rf"{VAR_RE};{VAR_RE}(?:,{VAR_RE})*"

MISSING_CONDITIONAL_H_RE = re.compile(rf"\bH\(\s*{VAR_RE}\s+{VAR_ASSIGN_RE}\)")
MISSING_CONDITIONAL_I_RE = re.compile(rf"\bI\(\s*{I_FIRST_RE}\s+{VAR_ASSIGN_RE}\)")
MISSING_KL_RE = re.compile(rf"\bD\(\s*{VAR_RE}\s+{VAR_RE}\)")
MISSING_DIVISIBILITY_RE = re.compile(r"\bq\s*\(p\s*-\s*1\)")

TEX_COMMAND_SMART_QUOTE_RE = re.compile(r"\\[A-Za-z]+’")
TRAILING_PRIME_SMART_QUOTE_RE = re.compile(r"[A-Za-z]’(?![A-Za-z])")


def iter_html_files(root: Path) -> list[Path]:
    return sorted(root.rglob("*.html"), key=lambda p: p.as_posix())

def visible_text(text: str) -> str:
    # Best-effort conversion of HTML to text for heuristic matching.
    # Replace tags with spaces so text that was split across nodes doesn't concatenate.
    out = TAG_RE.sub(" ", text)
    out = html.unescape(out)
    out = WS_RE.sub(" ", out).strip()
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--site-root", default="_site", help="Built site root (default: _site)")
    args = ap.parse_args()

    root = Path(args.site_root)
    if not root.exists():
        print(f"missing: {root}")
        return 2

    found_mathjax = False
    errors: list[str] = []

    for html in iter_html_files(root):
        text = html.read_text(encoding="utf-8", errors="replace")

        if MATHJAX_RE.search(text):
            found_mathjax = True

        scrubbed = SCRUB_RE.sub(" ", text)
        visible = visible_text(scrubbed)

        m = COMBINING_OVERLINE_RE.search(visible)
        if m:
            errors.append(f"{html}: combining overline/macron found: {m.group(0)}")

        m = RAW_BARS_RE.search(visible)
        if m:
            errors.append(f"{html}: raw |...| found: {m.group(0)}")

        m = RAW_SET_BUILDER_RE.search(visible)
        if m:
            errors.append(f"{html}: raw set-builder '{{...|...}}' found: {m.group(0)}")

        m = RAW_DOUBLE_PIPE_RE.search(visible)
        if m:
            errors.append(f"{html}: raw '||' found (use TeX): {m.group(0)}")

        m = MISSING_CONDITIONAL_H_RE.search(visible)
        if m:
            errors.append(f"{html}: possible missing conditional/concat symbol near: {m.group(0)}")

        m = MISSING_CONDITIONAL_I_RE.search(visible)
        if m:
            errors.append(f"{html}: possible missing conditional symbol near: {m.group(0)}")

        m = MISSING_KL_RE.search(visible)
        if m:
            errors.append(f"{html}: possible missing KL double-bar symbol near: {m.group(0)}")

        m = MISSING_DIVISIBILITY_RE.search(visible)
        if m:
            errors.append(f"{html}: possible missing divisibility symbol near: {m.group(0)}")

        # Issue #272: smart-quote conversion can leak U+2019 (’) into TeX, e.g. \delta’ or M’.
        # This can break MathJax/TeX parsing, so we detect it in built HTML (post-scrub).
        m = TEX_COMMAND_SMART_QUOTE_RE.search(visible)
        if m:
            ctx = visible[max(0, m.start() - 30) : min(len(visible), m.end() + 30)]
            errors.append(f"{html}: U+2019 (’) found after TeX command (smart quotes?): {m.group(0)} (ctx: {ctx})")

        m = TRAILING_PRIME_SMART_QUOTE_RE.search(visible)
        if m:
            ctx = visible[max(0, m.start() - 30) : min(len(visible), m.end() + 30)]
            errors.append(f"{html}: U+2019 (’) looks like a prime inside TeX/prose: {m.group(0)} (ctx: {ctx})")

    if not found_mathjax:
        errors.append("MathJax not found in built HTML (expected mathjax@3 / tex-chtml.js).")

    if errors:
        print("html notation check failed:")
        for e in errors:
            print(e)
        return 1

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
