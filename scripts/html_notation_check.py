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
import re
from pathlib import Path


CODE_RE = re.compile(r"(?is)<pre\\b.*?>.*?</pre>|<code\\b.*?>.*?</code>")
RAW_BARS_RE = re.compile(r"\\|[^\\s|]+\\|")
RAW_SET_BUILDER_RE = re.compile(r"\\{[^{}]*\\|[^{}]*\\}")
COMBINING_OVERLINE_RE = re.compile(r"[A-Za-z]\\u0304|[A-Za-z]\\u0305")
MATHJAX_RE = re.compile(r"mathjax@3|tex-chtml\\.js")


def iter_html_files(root: Path) -> list[Path]:
    return sorted(root.rglob("*.html"), key=lambda p: p.as_posix())


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

        scrubbed = CODE_RE.sub(" ", text)

        m = COMBINING_OVERLINE_RE.search(scrubbed)
        if m:
            errors.append(f"{html}: combining overline/macron found: {m.group(0)}")

        m = RAW_BARS_RE.search(scrubbed)
        if m:
            errors.append(f"{html}: raw |...| found: {m.group(0)}")

        m = RAW_SET_BUILDER_RE.search(scrubbed)
        if m:
            errors.append(f"{html}: raw set-builder '{{...|...}}' found: {m.group(0)}")

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
