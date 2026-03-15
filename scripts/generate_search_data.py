#!/usr/bin/env python3
"""Generate a small, deterministic search index JSON for client-side search.

This repository is served via GitHub Pages, so we cannot rely on custom Jekyll
plugins. Instead, we generate a JSON file at build time and commit it.

Design goals:
- No extra dependencies (stdlib only).
- Deterministic output (stable ordering).
- Extract a reasonable title + excerpt for each Markdown page under docs/.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


BASEURL_RE = re.compile(r"(?m)^baseurl:\s*(?P<val>.+?)\s*$")
TITLE_RE = re.compile(r"(?m)^title:\s*(?P<val>.+?)\s*$")
LIQUID_RE = re.compile(r"(?s)\{\{.*?\}\}|\{%.*?%\}")
FENCE_RE = re.compile(r"(?s)```.*?```")
INLINE_CODE_RE = re.compile(r"`[^`]+`")
HTML_TAG_RE = re.compile(r"(?s)<[^>]+>")
MD_IMAGE_RE = re.compile(r"!\[([^\]]*)\]\([^)]+\)")
MD_LINK_RE = re.compile(r"\[([^\]]+)\]\([^)]+\)")
HEADING_MARK_RE = re.compile(r"(?m)^#{1,6}\s+")
KRAMDOWN_INLINE_IAL_RE = re.compile(r"(?m)\s+\{#[A-Za-z0-9_-]+\}\s*$")
KRAMDOWN_BLOCK_IAL_RE = re.compile(r"(?m)^\{:\s*#[A-Za-z0-9_-]+\s*\}\s*$")


def read_baseurl(cfg_path: Path) -> str:
    if not cfg_path.exists():
        return ""
    text = cfg_path.read_text(encoding="utf-8")
    m = BASEURL_RE.search(text)
    if not m:
        return ""
    val = m.group("val").strip().strip('"').strip("'")
    if not val or val == "null":
        return ""
    if not val.startswith("/"):
        val = "/" + val
    return val.rstrip("/")


def split_front_matter(text: str) -> tuple[str, str]:
    # Jekyll front matter: starts with --- and ends with --- on its own line.
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return "", text
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            fm = "".join(lines[1:i])
            body = "".join(lines[i + 1 :])
            return fm, body
    return "", text


def extract_title(front_matter: str, body: str, fallback: str) -> str:
    if front_matter:
        m = TITLE_RE.search(front_matter)
        if m:
            val = m.group("val").strip()
            # Best-effort YAML scalar parsing (quoted or unquoted).
            if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                val = val[1:-1]
            if val:
                return val

    for line in body.splitlines():
        s = line.strip()
        if s.startswith("# "):
            return s[2:].strip()

    return fallback


def md_to_text(text: str) -> str:
    # Remove Liquid templates early to avoid leaking template syntax into tokens.
    text = LIQUID_RE.sub(" ", text)
    text = FENCE_RE.sub(" ", text)
    text = INLINE_CODE_RE.sub(" ", text)
    text = KRAMDOWN_BLOCK_IAL_RE.sub(" ", text)
    text = KRAMDOWN_INLINE_IAL_RE.sub("", text)
    text = MD_IMAGE_RE.sub(r"\1", text)
    text = MD_LINK_RE.sub(r"\1", text)
    text = HEADING_MARK_RE.sub("", text)
    text = HTML_TAG_RE.sub(" ", text)

    # Drop common Markdown punctuation.
    text = text.replace("*", " ").replace("_", " ").replace("|", " ").replace(">", " ")
    text = text.replace("[", " ").replace("]", " ").replace("(", " ").replace(")", " ")

    # Collapse whitespace.
    text = re.sub(r"\s+", " ", text).strip()
    return text


def page_url_from_rel(rel: Path) -> str:
    # rel is path under docs/
    if rel.as_posix() == "index.md":
        return "/"

    if rel.name == "index.md":
        parts = rel.parts[:-1]
        return "/" + "/".join(parts) + "/"

    stem = rel.with_suffix("")
    return "/" + "/".join(stem.parts) + "/"


def is_public_page(md: Path, docs_root: Path) -> bool:
    rel = md.relative_to(docs_root)
    # Exclude Jekyll internals and assets.
    if any(p.startswith("_") for p in rel.parts):
        return False
    if rel.parts and rel.parts[0] in {"assets"}:
        return False
    return True


def build_search_data(docs_root: Path, cfg_path: Path) -> dict:
    baseurl = read_baseurl(cfg_path)
    items: list[dict] = []

    for md in sorted(docs_root.rglob("*.md")):
        if not is_public_page(md, docs_root):
            continue
        rel = md.relative_to(docs_root)
        page_url = page_url_from_rel(rel)

        raw = md.read_text(encoding="utf-8")
        fm, body = split_front_matter(raw)
        title = extract_title(fm, body, fallback=rel.as_posix())
        excerpt = md_to_text(body)[:220]

        full_url = (baseurl + page_url) if baseurl else page_url
        items.append(
            {
                "title": title,
                "url": full_url,
                "source_path": md.as_posix(),
                "excerpt": excerpt,
            }
        )

    data = {
        "schema_version": 1,
        "baseurl": baseurl,
        "items": items,
    }
    return data


def dump_json(data: dict) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--docs-root", default="docs", help="Jekyll source directory (default: docs)")
    ap.add_argument(
        "--config",
        default="docs/_config.yml",
        help="Jekyll config to read baseurl from (default: docs/_config.yml)",
    )
    ap.add_argument(
        "--out",
        default="docs/assets/search-data.json",
        help="Output path (default: docs/assets/search-data.json)",
    )
    ap.add_argument("--check", action="store_true", help="Fail if the output file is not up-to-date")
    args = ap.parse_args()

    docs_root = Path(args.docs_root)
    cfg_path = Path(args.config)
    out_path = Path(args.out)

    data = build_search_data(docs_root, cfg_path)
    rendered = dump_json(data)

    if args.check:
        if not out_path.exists():
            print(f"missing: {out_path}")
            return 1
        current = out_path.read_text(encoding="utf-8")
        if current != rendered:
            print(f"out-of-date: {out_path}")
            return 1
        print("ok")
        return 0

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(rendered, encoding="utf-8")
    print(f"wrote: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
