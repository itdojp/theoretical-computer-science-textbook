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


def load_book_config(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


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
    text = remove_stable_id_ial_lines(text)
    return text


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

    title = cfg.get("title") or "理論計算機科学教科書"
    author = cfg.get("author") or "株式会社アイティードゥ"
    version = cfg.get("version") or ""

    parts: list[str] = []
    parts.append("---\n")
    parts.append(f"title: {title}\n")
    parts.append(f"author: {author}\n")
    if version:
        parts.append(f"version: {version}\n")
    parts.append("lang: ja\n")
    parts.append("---\n\n")

    combined_text = ""
    for p in files:
        raw = p.read_text(encoding="utf-8")
        processed = preprocess_markdown(raw).rstrip() + "\n\n"
        combined_text += processed

    if args.target == "pdf":
        svg_paths = collect_local_svg_paths(combined_text)
        ensure_svg_converted_to_pdf(docs_root, Path(args.asset_out), svg_paths)
        combined_text = rewrite_images_for_pdf(combined_text)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("".join(parts) + combined_text, encoding="utf-8")
    print(f"wrote: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

