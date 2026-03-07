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

DISPLAY_MATH_OPEN = r"\\["
DISPLAY_MATH_CLOSE = r"\\]"
INLINE_MATH_OPEN = r"\\("
INLINE_MATH_CLOSE = r"\\)"
DOLLAR_MATH_DELIM = "$$"

DISPLAY_MATH_OPEN_TOKENS = [r"\[", DISPLAY_MATH_OPEN]
DISPLAY_MATH_CLOSE_TOKENS = [r"\]", DISPLAY_MATH_CLOSE]
INLINE_MATH_OPEN_TOKENS = [r"\(", INLINE_MATH_OPEN]
INLINE_MATH_CLOSE_TOKENS = [r"\)", INLINE_MATH_CLOSE]

# Unicode subscripts are discouraged in prose/math (prefer TeX `_`).
UNICODE_SUBSCRIPT_RE = re.compile(r"[\u2080-\u209F\u1D62-\u1D6A\u2C7C]")

# In Markdown sources, `*` is parsed as emphasis, and this can corrupt math like
# `^*` / `^{*}` (e.g. rendering `^{<em>}` in the built HTML). Prefer TeX `\ast`.
UNSAFE_CARET_STAR_RE = re.compile(r"\^\*|\^\{\*\}")

# Also catch the clearly broken pattern where the exponent is missing entirely.
MISSING_KLEENE_STAR_RE = re.compile(r"\\\\\{0,1\\\\\}\^\s*(?:\\\\\)|\\\\\]|\\\\\}|$)")

# In prose, a bare `C*` / `X*` / `D*` etc is fragile because `*` can be eaten by
# Markdown emphasis parsing when another `*` appears later in the same line.
ALNUM_STAR_RE = re.compile(r"[0-9A-Za-z]\*(?!\*)")

# Keep Chapter 10/11 math notation strict (Issue #263 scope).
STRICT_CHAPTER_PATHS = {
    "docs/chapter-10/index.md",
    "docs/chapter-11/index.md",
    "src/chapter-10/index.md",
    "src/chapter-11/index.md",
}

# Keep Chapter 2 and Appendix A notation aligned with the guide (Issue #264 scope).
KLEENE_STAR_STRICT_PATHS = {
    "docs/chapter-2/index.md",
    "docs/appendices/a.md",
    "src/chapter-2/index.md",
    "src/appendices/a.md",
}

TM_NOTATION_STRICT_PATHS = {
    "docs/chapter-2/index.md",
    "docs/appendices/a.md",
    "src/chapter-2/index.md",
    "src/appendices/a.md",
}

# Keep Chapter 3 / Appendix C CFG notation TeX-only (Issue #273 scope).
CFG_NOTATION_STRICT_PATHS = {
    "docs/chapter-3/index.md",
    "docs/appendices/c.md",
    "src/chapter-3/index.md",
    "src/appendices/c.md",
}

CFG_NOTATION_STRICT_BAD_SUBSTRINGS = [
    ("≥", "Use TeX like `\\\\ge` (avoid Unicode ≥)."),
    ("≤", "Use TeX like `\\\\le` (avoid Unicode ≤)."),
    ("→", "Use TeX like `\\\\to` or rewrite prose (avoid Unicode →)."),
    ("⇒", "Use TeX like `\\\\Rightarrow` or rewrite prose (avoid Unicode ⇒)."),
]

CALLOUT_FREE_PATHS = {
    "docs/chapter-4/index.md",
    "docs/chapter-7/index.md",
    "docs/appendices/c.md",
    "src/chapter-4/index.md",
    "src/chapter-7/index.md",
    "src/appendices/c.md",
}

MATHBB_R_GE0_TYPO_PATHS = {
    "docs/appendices/c.md",
    "src/appendices/c.md",
}

CUSTOM_CALLOUT_RE = re.compile(r"[【】〖〗]")
MATHBB_R_GE0_TYPO_RE = re.compile(r"\\\\mathbb\{R\}\{\s*\\\\ge\s*0\s*\}")

# Notation lint should prevent reintroducing a few problematic substrings
# repository-wide (Issue #270).
RAW_BAD_SUBSTRINGS = [
    ("’", "Avoid Unicode right single quotation mark U+2019 (’); use ASCII ' or TeX like `\\\\prime`."),
    ("Σ*", "Avoid raw 'Σ*' (use TeX like `\\\\(\\\\Sigma^{\\\\ast}\\\\)`)."),
    ("for all", "Avoid raw 'for all' (use `\\\\forall` or rewrite prose in Japanese)."),
]

Q_UNICODE_SUBSCRIPT_RE = re.compile(r"q[₀-₉]")

STRICT_BAD_SUBSTRINGS = [
    ("log₂", "Use TeX like `\\\\log_2` (avoid Unicode log₂)."),
    ("∑", "Use TeX like `\\\\sum` (avoid Unicode ∑)."),
    ("≥", "Use TeX like `\\\\ge` (avoid Unicode ≥)."),
    ("≤", "Use TeX like `\\\\le` (avoid Unicode ≤)."),
    ("→", "Use TeX like `\\\\to` or rewrite prose (avoid Unicode →)."),
    ("·", "Use TeX like `\\\\cdot` (avoid Unicode ·)."),
    ("⊕", "Use TeX like `\\\\oplus` (avoid Unicode ⊕)."),
    ("≡", "Use TeX like `\\\\equiv` (avoid Unicode ≡)."),
    ("≠", "Use TeX like `\\\\ne` (avoid Unicode ≠)."),
    ("⌈", "Use TeX like `\\\\lceil`/`\\\\rceil` (avoid Unicode ⌈ ⌉)."),
    ("⌉", "Use TeX like `\\\\lceil`/`\\\\rceil` (avoid Unicode ⌈ ⌉)."),
    ("⌊", "Use TeX like `\\\\lfloor`/`\\\\rfloor` (avoid Unicode ⌊ ⌋)."),
    ("⌋", "Use TeX like `\\\\lfloor`/`\\\\rfloor` (avoid Unicode ⌊ ⌋)."),
]

BAD_SUBSTRINGS = [
    # Power set notation: keep it consistent with the guide (Appendix A).
    ("𝒫(", "Use TeX like `\\\\mathcal{P}(A)` for power sets (avoid Unicode 𝒫)."),
    ("𝒫（", "Use TeX like `\\\\mathcal{P}(A)` for power sets (avoid Unicode 𝒫)."),
    ("𝒫{", "Use TeX like `\\\\mathcal{P}(A)` for power sets (avoid Unicode 𝒫)."),
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

TYPICAL_DUPLICATED_TOKEN_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\bL\s+L\b"), "Possible duplicated token 'L L' (typo)."),
    (re.compile(r"∅\s+∅"), "Possible duplicated token '∅ ∅' (typo)."),
]

def scan_math_delimiters_forbidden_chars(
    path: Path,
    lineno: int,
    line: str,
    *,
    in_display_math: bool,
    in_dollar_math: bool,
) -> tuple[list[str], bool, bool]:
    """Scan math-delimited regions and reject fragile characters inside them.

    Issue #271: forbid raw '*' and U+2019 inside math regions to prevent Markdown
    emphasis parsing from corrupting notation. Inline code spans are expected to
    be stripped before calling this function.
    """

    def match_any_token(pos: int, tokens: list[str]):
        for tok in tokens:
            if line.startswith(tok, pos):
                return tok
        return None

    errors: list[str] = []

    # Inline math is treated as line-local in this linter.
    in_inline_math = False
    found_math_star = False
    found_math_u2019 = False
    found_math_ascii_apostrophe = False
    found_nested_inline_delim_in_display = False

    i = 0
    n = len(line)
    while i < n:
        if not in_inline_math and not in_dollar_math and not in_display_math:
            tok = match_any_token(i, DISPLAY_MATH_OPEN_TOKENS)
            if tok is not None:
                in_display_math = True
                i += len(tok)
                continue

        if in_display_math and not in_inline_math and not in_dollar_math:
            tok = match_any_token(i, DISPLAY_MATH_CLOSE_TOKENS)
            if tok is not None:
                in_display_math = False
                i += len(tok)
                continue
            tok = match_any_token(i, INLINE_MATH_OPEN_TOKENS + INLINE_MATH_CLOSE_TOKENS)
            if tok is not None:
                found_nested_inline_delim_in_display = True
                i += len(tok)
                continue

        if not in_inline_math and not in_display_math and line.startswith(DOLLAR_MATH_DELIM, i):
            in_dollar_math = not in_dollar_math
            i += len(DOLLAR_MATH_DELIM)
            continue

        if not in_display_math and not in_dollar_math:
            if not in_inline_math:
                tok = match_any_token(i, INLINE_MATH_OPEN_TOKENS)
                if tok is not None:
                    in_inline_math = True
                    i += len(tok)
                    continue
            else:
                tok = match_any_token(i, INLINE_MATH_CLOSE_TOKENS)
                if tok is not None:
                    in_inline_math = False
                    i += len(tok)
                    continue

        if in_display_math or in_dollar_math or in_inline_math:
            ch = line[i]
            if ch == "*":
                found_math_star = True
            elif ch == "'":
                found_math_ascii_apostrophe = True
            elif ch == "’":
                found_math_u2019 = True

        i += 1

    if found_nested_inline_delim_in_display:
        errors.append(
            f"{path}:{lineno}: Avoid nesting inline math {INLINE_MATH_OPEN}...{INLINE_MATH_CLOSE} "
            f"inside display math {DISPLAY_MATH_OPEN}...{DISPLAY_MATH_CLOSE}."
        )

    if found_math_u2019:
        errors.append(
            f"{path}:{lineno}: Avoid U+2019 (’) inside math regions; "
            f"use ASCII ' or TeX like `\\\\prime`/`^{{\\\\prime}}`."
        )

    if found_math_ascii_apostrophe:
        errors.append(
            f"{path}:{lineno}: Avoid ASCII apostrophe (') inside math regions; "
            f"use TeX like `\\\\prime`/`^{{\\\\prime}}` to prevent smart-quote conversion in HTML."
        )

    if found_math_star:
        errors.append(
            f"{path}:{lineno}: Avoid raw '*' inside math regions; "
            f"use TeX like `^{{\\\\ast}}` for Kleene closure, or `\\\\cdot`/`\\\\times` for multiplication."
        )

    return errors, in_display_math, in_dollar_math

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
    in_display_math = False
    in_dollar_math = False
    for lineno, raw in enumerate(text.splitlines(), start=1):
        line = raw.rstrip("\n")

        # Enforce a few raw patterns even in fenced code / inline code spans,
        # to match the repository-level acceptance criteria (Issue #270).
        for bad, msg in RAW_BAD_SUBSTRINGS:
            if bad in line:
                errors.append(f"{path}:{lineno}: {msg} (found: {bad})")

        m = UNICODE_SUBSCRIPT_RE.search(line)
        if m:
            errors.append(
                f"{path}:{lineno}: Avoid Unicode subscripts (use TeX like _{{...}} / ASCII like _...): "
                f"{m.group(0)}"
            )

        m = UNICODE_SUPERSCRIPT_RE.search(line)
        if m:
            errors.append(
                f"{path}:{lineno}: Avoid Unicode superscripts (use TeX like ^{{...}} / ASCII like ^...): "
                f"{m.group(0)}"
            )

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

        if path.as_posix() in STRICT_CHAPTER_PATHS:
            for bad, msg in STRICT_BAD_SUBSTRINGS:
                if bad in line_no_code:
                    errors.append(f"{path}:{lineno}: {msg} (found: {bad})")

            m = ALNUM_STAR_RE.search(line_no_code)
            if m:
                errors.append(
                    f"{path}:{lineno}: Avoid bare '*' after alphanumerics like `C*`/`X*`/`D*`; "
                    f"prefer TeX in math mode (e.g. `\\\\(C^{{\\\\ast}}\\\\)`). "
                    f"(found: {m.group(0)})"
                )

        if path.as_posix() in KLEENE_STAR_STRICT_PATHS:
            if "{0,1}*" in line_no_code:
                errors.append(
                    f"{path}:{lineno}: Avoid raw '{{0,1}}*' (use TeX like `\\\\(\\\\{{0,1\\\\}}^{{\\\\ast}}\\\\)`)."
                )

        if path.as_posix() in TM_NOTATION_STRICT_PATHS:
            m = Q_UNICODE_SUBSCRIPT_RE.search(line_no_code)
            if m:
                errors.append(
                    f"{path}:{lineno}: Avoid Unicode subscript state notation like '{m.group(0)}' (use TeX like `q_0`/`q_1`)."
                )
            if "qaccept" in line_no_code:
                errors.append(
                    f"{path}:{lineno}: Avoid 'qaccept' (use TeX like `q_{{\\\\mathrm{{accept}}}}`)."
                )
            if "qreject" in line_no_code:
                errors.append(
                    f"{path}:{lineno}: Avoid 'qreject' (use TeX like `q_{{\\\\mathrm{{reject}}}}`)."
                )
            if "⇀" in line_no_code:
                errors.append(
                    f"{path}:{lineno}: Avoid Unicode partial function arrow '⇀' (use TeX like `\\\\rightharpoonup`)."
                )

        if path.as_posix() in CFG_NOTATION_STRICT_PATHS:
            for bad, msg in CFG_NOTATION_STRICT_BAD_SUBSTRINGS:
                if bad in line_no_code:
                    errors.append(f"{path}:{lineno}: {msg} (found: {bad})")

        if path.as_posix() in CALLOUT_FREE_PATHS:
            m = CUSTOM_CALLOUT_RE.search(line_no_code)
            if m:
                errors.append(
                    f"{path}:{lineno}: Avoid custom full-width callout markers like '{m.group(0)}'; "
                    f"use Markdown headings or bold labels instead."
                )

        if path.as_posix() in MATHBB_R_GE0_TYPO_PATHS:
            if MATHBB_R_GE0_TYPO_RE.search(line_no_code):
                errors.append(
                    f"{path}:{lineno}: Avoid `\\\\mathbb{{R}}{{\\\\ge 0}}`; "
                    f"use `\\\\mathbb{{R}}_{{\\\\ge 0}}`."
                )

        math_errors, in_display_math, in_dollar_math = scan_math_delimiters_forbidden_chars(
            path,
            lineno,
            line_no_code,
            in_display_math=in_display_math,
            in_dollar_math=in_dollar_math,
        )
        errors.extend(math_errors)

        for rx, msg in TYPICAL_DUPLICATED_TOKEN_PATTERNS:
            m = rx.search(line_no_code)
            if m:
                errors.append(f"{path}:{lineno}: {msg} (found: {m.group(0)})")

        m = UNSAFE_CARET_STAR_RE.search(line_no_code)
        if m:
            errors.append(
                f"{path}:{lineno}: Avoid `^*` / `^{{*}}` in Markdown sources; prefer TeX `^{{\\ast}}` "
                f"(e.g. `\\\\(\\Sigma^{{\\ast}}\\\\)`), to prevent '*' being eaten by Markdown."
            )

        m = MISSING_KLEENE_STAR_RE.search(line_no_code)
        if m:
            errors.append(
                f"{path}:{lineno}: Possible missing Kleene star after `\\\\{{0,1\\\\}}^` "
                f"(use TeX like `\\\\(\\\\{{0,1\\\\}}^{{\\ast}}\\\\)`)."
            )

        if ") if (" in line_no_code:
            errors.append(
                f"{path}:{lineno}: Avoid raw 'if' inside math-like expressions; "
                f"use TeX like `\\\\text{{...}}` or rewrite prose in Japanese."
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
