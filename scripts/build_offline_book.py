#!/usr/bin/env python3
"""Build a single Markdown source for offline exports (PDF/EPUB).

This repository is authored as a Jekyll site under `docs/` and contains:
- YAML front matter (Jekyll)
- Liquid `relative_url` expressions (Jekyll)
- kramdown IAL lines like `{: #thm-1-1 }` (stable anchors for the website)

Pandoc (or other offline converters) should not see those site-specific syntaxes.
This script concatenates pages in a book-like order and applies a small,
deterministic preprocessing to produce a plain Markdown file.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from pathlib import Path


RELATIVE_URL_RE = re.compile(
    r"""\{\{\s*['"](?P<path>[^'"]+)['"]\s*\|\s*relative_url\s*\}\}"""
)

# kramdown IAL used for stable anchors in the website build.
STABLE_ID_IAL_RE = re.compile(r"^\s*\{:\s*#[-A-Za-z0-9_]+\s*\}\s*$")

EXERCISE_CROSS_LINK_RE = re.compile(
    r"(?:\.\./appendices/c/|chapter-\d+/)#"
    # ``ex-sol-chN`` is the chapter-level Appendix C anchor; the optional
    # three-digit suffix identifies an individual solution.
    r"(?P<id>exq-ch\d+-\d{3}|ex-sol-ch\d+(?:-\d{3})?)"
)

# kramdown accepts the source's empty HTML spans as link targets, but Pandoc's
# LaTeX writer may discard raw HTML. Convert only the stable exercise anchors
# to Pandoc-native attributed spans before PDF/EPUB conversion.
EXERCISE_ANCHOR_RE = re.compile(
    r'<span\s+id="(?P<id>exq-ch\d+-\d{3}|ex-sol-ch\d+-\d{3})"\s*></span>'
)

# Markdown images: keep parsing simple and conservative.
MD_IMAGE_RE = re.compile(
    r"""!\[(?P<alt>[^\]]*)\]\((?P<url>\S+?)(?P<rest>\s+\"[^\"]*\")?\)"""
)


def strip_front_matter(text: str) -> str:
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return text

    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return "".join(lines[i + 1 :])

    # No closing delimiter; keep original for safety.
    return text


def rewrite_liquid_relative_url(text: str) -> str:
    def repl(m: re.Match) -> str:
        path = m.group("path")
        # Liquid `relative_url` output always starts with `/`; offline prefers relative paths.
        return path.lstrip("/")

    return RELATIVE_URL_RE.sub(repl, text)


def remove_stable_id_ial_lines(text: str) -> str:
    out: list[str] = []
    for line in text.splitlines(keepends=True):
        if STABLE_ID_IAL_RE.match(line.rstrip("\n")):
            continue
        out.append(line)
    return "".join(out)


def rewrite_exercise_cross_links_for_offline(text: str) -> str:
    """Point exercise links at anchors in the concatenated offline document."""
    return EXERCISE_CROSS_LINK_RE.sub(lambda match: f"#{match.group('id')}", text)


def rewrite_exercise_anchors_for_offline(text: str) -> str:
    """Preserve stable exercise targets in Pandoc's native AST."""
    return EXERCISE_ANCHOR_RE.sub(lambda match: f"[]{{#{match.group('id')}}}", text)


def normalize_math_delimiters_for_pandoc(text: str) -> str:
    """Convert Web math syntax to Pandoc `$`/`$$` syntax.

    The Web source contains both single and doubled delimiters (``\\(``,
    ``\\\\(``, ``\\[``, ``\\\\[``) and both single- and double-escaped LaTeX
    commands. Pandoc needs one backslash for a command and two for an ``aligned``
    line break, so even-length runs are halved only while inside math. Fenced
    blocks and inline code are preserved.
    """
    fence_character: str | None = None
    fence_length = 0
    math_closer: str | None = None
    code_delimiter: str | None = None
    out: list[str] = []
    for line in text.splitlines(keepends=True):
        fence = re.match(r"^\s*(`{3,}|~{3,})", line)
        if fence_character is not None and math_closer is None and code_delimiter is None:
            out.append(line)
            if (
                fence
                and fence.group(1)[0] == fence_character
                and len(fence.group(1)) >= fence_length
            ):
                fence_character = None
                fence_length = 0
            continue
        if fence and math_closer is None and code_delimiter is None:
            fence_character = fence.group(1)[0]
            fence_length = len(fence.group(1))
            out.append(line)
            continue

        position = 0
        while position < len(line):
            if math_closer is not None:
                if line.startswith(math_closer + math_closer, position):
                    # A few Web formulas encode a literal closing parenthesis
                    # with the same doubled token immediately before the real
                    # math closer (``...\\\\)\\\\)``). Keep the first character
                    # inside math and let the second token close the span.
                    out.append(math_closer[-1])
                    position += len(math_closer)
                    continue
                if line.startswith(math_closer, position):
                    if math_closer.endswith(")"):
                        while out and out[-1] in (" ", "\t"):
                            out.pop()
                    out.append("$$" if math_closer.endswith("]") else "$")
                    position += len(math_closer)
                    math_closer = None
                    continue
                if line[position] == "\\":
                    run_end = position + 1
                    while run_end < len(line) and line[run_end] == "\\":
                        run_end += 1
                    run_length = run_end - position
                    normalized_length = run_length // 2 if run_length % 2 == 0 else run_length
                    out.append("\\" * normalized_length)
                    position = run_end
                    continue
                out.append(line[position])
                position += 1
                continue

            if code_delimiter is not None:
                if line.startswith(code_delimiter, position):
                    out.append(code_delimiter)
                    position += len(code_delimiter)
                    code_delimiter = None
                else:
                    out.append(line[position])
                    position += 1
                continue

            if line[position] == "`":
                run_end = position + 1
                while run_end < len(line) and line[run_end] == "`":
                    run_end += 1
                code_delimiter = line[position:run_end]
                out.append(code_delimiter)
                position = run_end
                continue

            if line.startswith("\\\\(", position):
                out.append("$")
                math_closer = "\\\\)"
                position += 3
                while position < len(line) and line[position] in (" ", "\t"):
                    position += 1
                continue
            if line.startswith("\\\\[", position):
                out.append("$$")
                math_closer = "\\\\]"
                position += 3
                continue
            if line.startswith("\\(", position):
                out.append("$")
                math_closer = "\\)"
                position += 2
                while position < len(line) and line[position] in (" ", "\t"):
                    position += 1
                continue
            if line.startswith("\\[", position):
                out.append("$$")
                math_closer = "\\]"
                position += 2
                continue

            out.append(line[position])
            position += 1
    if math_closer is not None:
        raise ValueError(f"unclosed Web math delimiter; expected {math_closer!r}")
    return "".join(out)


def load_book_config(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build_publication_front_matter(cfg: dict) -> str:
    """Build Pandoc metadata from the canonical publication fields."""
    title = cfg.get("title") or "理論計算機科学教科書"
    author = cfg.get("author") or "株式会社アイティードゥ"
    version = cfg.get("version") or ""
    publication = cfg.get("publication", {})
    release_date = publication.get("release_date", "")
    last_updated = publication.get("last_updated", "")

    parts = ["---\n", f"title: {title}\n", f"author: {author}\n"]
    if version:
        parts.append(f"version: {version}\n")
    if release_date:
        parts.append(f"date: {release_date}\n")
    if last_updated:
        parts.append(f"last_updated: {last_updated}\n")
    parts.extend(("lang: ja\n", "---\n\n"))
    return "".join(parts)


def build_source_file_list(docs_root: Path, cfg: dict) -> list[Path]:
    structure = cfg.get("structure", {})
    out: list[Path] = []

    # Cover / landing page as a preface.
    out.append(docs_root / "index.md")

    intro = structure.get("introduction", {}).get("sections", [])
    for sec in intro:
        rel = sec.get("file")
        if rel:
            out.append(docs_root / rel)

    parts = structure.get("parts", [])
    if parts:
        for part in parts:
            opener = str(part.get("opener_file", "")).strip()
            if opener:
                out.append(docs_root / opener)
            for cid in part.get("chapters", []):
                chapter_id = str(cid).strip()
                if chapter_id:
                    out.append(docs_root / f"chapter-{chapter_id}/index.md")
    else:
        for ch in structure.get("chapters", []):
            cid = str(ch.get("id", "")).strip()
            if cid:
                out.append(docs_root / f"chapter-{cid}/index.md")

    # Appendices
    out.append(docs_root / "appendices/index.md")
    for app in structure.get("appendices", []):
        aid = str(app.get("id", "")).strip()
        if aid:
            out.append(docs_root / f"appendices/{aid}.md")

    # Validate existence early.
    missing = [p.as_posix() for p in out if not p.exists()]
    if missing:
        raise SystemExit("missing source files:\n" + "\n".join(f"- {m}" for m in missing))

    return out


def preprocess_markdown(text: str) -> str:
    text = strip_front_matter(text)
    text = rewrite_liquid_relative_url(text)
    text = rewrite_exercise_cross_links_for_offline(text)
    text = rewrite_exercise_anchors_for_offline(text)
    text = remove_stable_id_ial_lines(text)
    text = normalize_math_delimiters_for_pandoc(text)
    return text


# `Q\F` のような表記（集合差/制限）を、PDF向けに安全な表記へ正規化するためのパターン。
# `\in` などの LaTeX コマンド（右辺が小文字で始まる）には誤爆しないよう、左右とも大文字開始に限定する。
SET_DIFF_TOKEN_RE = re.compile(
    r"(?P<l>[A-Z][A-Za-z0-9]*)\s*\\{1,2}\s*(?P<r>[A-Z][A-Za-z0-9]*)"
)


def normalize_for_pdf(text: str) -> str:
    """Pandoc->LaTeX PDF のための軽量な正規化.

    本文中の `Q\\F` や `A \\ B` のような「バックスラッシュを集合差/制限として使う表記」は、
    LaTeX 出力時に `\\F` のような制御綴になりエラー/誤表示の原因になる。

    PDF向けには、コードブロック以外の箇所だけを対象に、Unicode の集合差記号 `∖`（U+2216）
    へ置換する。
    """

    in_fence = False
    out: list[str] = []
    for raw in text.splitlines(keepends=True):
        line = raw
        stripped = line.lstrip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            out.append(line)
            continue
        if in_fence:
            out.append(line)
            continue

        # "A \\ B" / "A\\B" / "A\\\\B" を集合差記号へ正規化（PDF向け）。
        line = SET_DIFF_TOKEN_RE.sub(r"\g<l> ∖ \g<r>", line)

        out.append(line)

    return "".join(out)


def rewrite_images_for_pdf(text: str) -> str:
    """Rewrite local SVG image references to .pdf for LaTeX-friendly embedding."""

    def repl(m: re.Match) -> str:
        url = m.group("url")
        rest = m.group("rest") or ""

        # Keep remote URLs unchanged.
        if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", url):
            return m.group(0)

        # Prefer vector PDFs for diagrams in PDF output.
        if url.startswith("assets/") and url.lower().endswith(".svg"):
            url = url[: -len(".svg")] + ".pdf"

        return f"![{m.group('alt')}]({url}{rest})"

    return MD_IMAGE_RE.sub(repl, text)


def collect_local_svg_paths(text: str) -> set[str]:
    paths: set[str] = set()
    for m in MD_IMAGE_RE.finditer(text):
        url = m.group("url")
        if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", url):
            continue
        if url.startswith("assets/") and url.lower().endswith(".svg"):
            paths.add(url)
    return paths


def ensure_svg_converted_to_pdf(docs_root: Path, out_root: Path, svg_relpaths: set[str]) -> None:
    """Convert `docs_root/<svg>` into `out_root/<svg>.pdf` (same relative layout)."""
    if not svg_relpaths:
        return

    if shutil.which("rsvg-convert") is None:
        raise SystemExit("rsvg-convert not found (install librsvg2-bin)")

    for rel in sorted(svg_relpaths):
        src = docs_root / rel
        dst = out_root / rel
        dst = dst.with_suffix(".pdf")
        dst.parent.mkdir(parents=True, exist_ok=True)

        # Vector PDF keeps diagrams sharp while remaining LaTeX-compatible.
        subprocess.run(
            ["rsvg-convert", "-f", "pdf", "-o", str(dst), str(src)],
            check=True,
        )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--docs-root", default="docs", help="Jekyll source directory (default: docs)")
    ap.add_argument(
        "--config",
        default="docs/book-config.json",
        help="Book structure config (default: docs/book-config.json)",
    )
    ap.add_argument("--out", default="dist/book.md", help="Output Markdown path (default: dist/book.md)")
    ap.add_argument(
        "--target",
        choices=["epub", "pdf"],
        default="epub",
        help="Output target; affects preprocessing (default: epub)",
    )
    ap.add_argument(
        "--asset-out",
        default="dist",
        help="For --target=pdf, where converted assets are written (default: dist)",
    )
    args = ap.parse_args()

    docs_root = Path(args.docs_root)
    cfg = load_book_config(Path(args.config))
    files = build_source_file_list(docs_root, cfg)

    combined_text = ""
    for p in files:
        raw = p.read_text(encoding="utf-8")
        processed = preprocess_markdown(raw).rstrip() + "\n\n"
        combined_text += processed

    if args.target == "pdf":
        combined_text = normalize_for_pdf(combined_text)
        svg_paths = collect_local_svg_paths(combined_text)
        ensure_svg_converted_to_pdf(docs_root, Path(args.asset_out), svg_paths)
        combined_text = rewrite_images_for_pdf(combined_text)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(build_publication_front_matter(cfg) + combined_text, encoding="utf-8")
    print(f"wrote: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
