#!/usr/bin/env python3
"""Lightweight notation linter for Markdown.

Goal: prevent re-introducing a few high-signal notation inconsistencies.
This is intentionally narrow (regex-based, stdlib only) to keep CI stable.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path


UNICODE_SUPERSCRIPT_CODEPOINTS = [
    # Superscripts and Subscripts block + a few modifier-letter superscripts
    # used as exponents in prose (e.g. 0^n, n^k, σ^2, Σ_0^P).
    0x2070,  # SUPERSCRIPT ZERO
    0x00B9,  # SUPERSCRIPT ONE
    0x00B2,  # SUPERSCRIPT TWO
    0x00B3,  # SUPERSCRIPT THREE
    0x2074,  # SUPERSCRIPT FOUR
    0x2075,  # SUPERSCRIPT FIVE
    0x2076,  # SUPERSCRIPT SIX
    0x2077,  # SUPERSCRIPT SEVEN
    0x2078,  # SUPERSCRIPT EIGHT
    0x2079,  # SUPERSCRIPT NINE
    0x207A,  # SUPERSCRIPT PLUS SIGN
    0x207B,  # SUPERSCRIPT MINUS
    0x207F,  # SUPERSCRIPT LATIN SMALL LETTER N
    0x2071,  # SUPERSCRIPT LATIN SMALL LETTER I
    0x1D43,  # MODIFIER LETTER SMALL A
    0x1D47,  # MODIFIER LETTER SMALL B
    0x1D9C,  # MODIFIER LETTER SMALL C
    0x1D48,  # MODIFIER LETTER SMALL D
    0x1D49,  # MODIFIER LETTER SMALL E
    0x1DA0,  # MODIFIER LETTER SMALL F
    0x1D4D,  # MODIFIER LETTER SMALL G
    0x02B0,  # MODIFIER LETTER SMALL H
    0x1DA6,  # MODIFIER LETTER SMALL CAPITAL I
    0x02B2,  # MODIFIER LETTER SMALL J
    0x1D4F,  # MODIFIER LETTER SMALL K
    0x02E1,  # MODIFIER LETTER SMALL L
    0x1D50,  # MODIFIER LETTER SMALL M
    0x1D52,  # MODIFIER LETTER SMALL O
    0x1D56,  # MODIFIER LETTER SMALL P
    0x1D3E,  # MODIFIER LETTER CAPITAL P
    0x1D3F,  # MODIFIER LETTER CAPITAL R
    0x02B3,  # MODIFIER LETTER SMALL R
    0x02E2,  # MODIFIER LETTER SMALL S
    0x1D57,  # MODIFIER LETTER SMALL T
    0x1D58,  # MODIFIER LETTER SMALL U
    0x1D5B,  # MODIFIER LETTER SMALL V
    0x02B7,  # MODIFIER LETTER SMALL W
    0x02E3,  # MODIFIER LETTER SMALL X
    0x02B8,  # MODIFIER LETTER SMALL Y
    0x1DBB,  # MODIFIER LETTER SMALL Z
    0x1D05,  # LATIN LETTER SMALL CAPITAL D
    0x1D4B,  # MODIFIER LETTER SMALL OPEN E
]

UNICODE_SUPERSCRIPT_CHARS = "".join(chr(cp) for cp in UNICODE_SUPERSCRIPT_CODEPOINTS)
UNICODE_SUPERSCRIPT_RE = re.compile("[" + re.escape(UNICODE_SUPERSCRIPT_CHARS) + "]")

INLINE_MATH_MID_TOKEN_RE = re.compile(
    # Mixed set-builder notation tends to appear as { ... \( \mid \) ... }.
    # The repository mostly uses double backslashes in Markdown (\\( ... \\)),
    # but we accept both to prevent regressions.
    r"(?:\\\(\s*\\mid\s*\\\)|\\\\\(\s*\\\\mid\s*\\\\\))"
)

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

BAD_INLINE_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    # Avoid raw conditional/divisibility bars inside common math-like expressions.
    (
        re.compile(r"\bH\([^)\n]*\|[^)\n]*\)"),
        "Avoid raw '|' in conditional entropy notation (use TeX like \\mid).",
    ),
    (
        re.compile(r"\bI\([^)\n]*\|[^)\n]*\)"),
        "Avoid raw '|' in conditional mutual information notation (use TeX like \\mid).",
    ),
    (
        re.compile(r"\bp\([^)\n]*\|[^)\n]*\)"),
        "Avoid raw '|' in conditional probability notation (use TeX like \\mid).",
    ),
    (
        re.compile(r"\bq\s*\|\s*\(?p\s*-\s*1\)?"),
        "Avoid raw divisibility '|' (use TeX like \\mid, e.g. \\(q \\mid (p-1)\\)).",
    ),
]

def contains_inline_math_mid_inside_braces(line: str) -> bool:
    """Detect an inline-math-only \\mid token inside a {...} segment.

    This catches the mixed notation "{ ... \\(\\mid\\) ... }" which is
    discouraged in Issue #261 (set-builder notation should be all in math mode).
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

        if depth > 0:
            m = INLINE_MATH_MID_TOKEN_RE.match(line, i)
            if m:
                return True

        ch = line[i]
        if ch == "{":
            depth += 1
        elif ch == "}":
            if depth > 0:
                depth -= 1
        i += 1

    return False


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


def check_chapter_end_sections(path: Path, text: str) -> list[str]:
    errors: list[str] = []

    in_fence = False
    h2: list[tuple[int, str]] = []
    for lineno, raw in enumerate(text.splitlines(), start=1):
        line = raw.rstrip("\n")
        stripped = line.lstrip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue

        m = re.match(r"^##\s+(.+?)\s*$", line)
        if not m:
            continue
        title = m.group(1)
        h2.append((lineno, title))

    summary = [(ln, t) for (ln, t) in h2 if t == "まとめ"]
    problems = [(ln, t) for (ln, t) in h2 if t == "章末問題"]

    if len(summary) > 1:
        for ln, _ in summary[1:]:
            errors.append(f"{path}:{ln}: '## まとめ' must appear at most once per chapter.")
    if len(problems) > 1:
        for ln, _ in problems[1:]:
            errors.append(f"{path}:{ln}: '## 章末問題' must appear at most once per chapter.")

    summary_ln = summary[0][0] if summary else None
    problems_ln = problems[0][0] if problems else None

    if summary_ln is not None and problems_ln is not None and summary_ln > problems_ln:
        errors.append(f"{path}:{summary_ln}: '## まとめ' must come before '## 章末問題'.")

    if problems_ln is not None and h2:
        last_ln, last_title = h2[-1]
        if last_title != "章末問題":
            errors.append(
                f"{path}:{problems_ln}: '## 章末問題' must be the last level-2 section in the chapter "
                f"(last is '{last_title}' at line {last_ln})."
            )

    if summary_ln is not None:
        allowed_after_summary = {"章末問題"}
        after = [(ln, t) for (ln, t) in h2 if ln > summary_ln]
        bad_after = [(ln, t) for (ln, t) in after if t not in allowed_after_summary]
        if bad_after:
            ln, t = bad_after[0]
            errors.append(
                f"{path}:{summary_ln}: '## まとめ' must be a chapter-end section "
                f"(found another level-2 section '{t}' at line {ln} after it)."
            )

    return errors


def check_unicode_superscripts_in_text(path: Path, text: str) -> list[str]:
    errors: list[str] = []
    for lineno, raw in enumerate(text.splitlines(), start=1):
        m = UNICODE_SUPERSCRIPT_RE.search(raw)
        if m:
            errors.append(
                f"{path}:{lineno}: Avoid Unicode superscripts (use TeX like ^{{...}} / ASCII like ^...): "
                f"{m.group(0)}"
            )
            # Avoid overwhelming output for large generated files.
            if len(errors) >= 5:
                errors.append(f"{path}: too many Unicode superscripts; showing first 5 only.")
                break
    return errors


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

        m = UNICODE_SUPERSCRIPT_RE.search(line_no_code)
        if m:
            errors.append(
                f"{path}:{lineno}: Avoid Unicode superscripts (use TeX like ^{{...}} / ASCII like ^...): "
                f"{m.group(0)}"
            )

        # Avoid raw concatenation / double-bar notation, which is easy to lose in Markdown/HTML.
        if "||" in line_no_code:
            errors.append(
                f"{path}:{lineno}: Avoid raw '||' (use TeX like \\\\parallel for concatenation "
                f"or \\\\Vert for KL-style double bars)."
            )

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

        if contains_inline_math_mid_inside_braces(line_no_code):
            errors.append(
                f"{path}:{lineno}: Avoid mixed set-builder notation like {{... \\(\\mid\\) ...}}; "
                f"put the whole expression in math mode (e.g. \\(\\\\{{... \\\\mid ...\\\\}}\\))."
            )

        for rx, msg in BAD_INLINE_PATTERNS:
            m = rx.search(line_no_code)
            if m:
                errors.append(f"{path}:{lineno}: {msg} (found: {m.group(0)})")

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
        if md.name == "index.md" and md.parent.name.startswith("chapter-"):
            all_errors.extend(check_chapter_end_sections(md, md.read_text(encoding="utf-8")))

    # Also enforce the Unicode superscript ban on a few non-Markdown sources that commonly leak into HTML.
    extra_paths: list[Path] = []
    if Path("cspell-words.txt").exists():
        extra_paths.append(Path("cspell-words.txt"))
    if Path("docs/index.json").exists():
        extra_paths.append(Path("docs/index.json"))
    diagrams_dir = Path("docs/assets/images/diagrams")
    if diagrams_dir.exists():
        extra_paths.extend(sorted(diagrams_dir.glob("*.svg"), key=lambda p: p.as_posix()))

    for p in extra_paths:
        all_errors.extend(check_unicode_superscripts_in_text(p, p.read_text(encoding="utf-8")))

    if all_errors:
        print("notation lint failed:")
        for e in all_errors:
            print(e)
        return 1

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
