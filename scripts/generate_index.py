#!/usr/bin/env python3
"""Generate a machine-readable index (index.json) for definitions/theorems/etc.

Design goals:
- No extra dependencies (stdlib only).
- Deterministic output (stable ordering).
- Works without custom Jekyll plugins (generate and commit the JSON).

The index is intended for search/RAG and for stable cross-references via IDs.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


KIND_TO_PREFIX = {
    "定義": "def",
    "定理": "thm",
    "補題": "lem",
    "命題": "prop",
    "系": "cor",
    "例": "ex",
}

LABEL_RE = re.compile(
    r"^(?P<indent>\s*)\*\*(?P<kind>定義|定理|補題|命題|系|例)\s+(?P<num>\d+(?:\.\d+)+)\*\*(?P<rest>.*)$"
)
IAL_RE = re.compile(r"^\s*\{:\s*#(?P<id>[A-Za-z0-9_-]+)\s*\}\s*$")
HEADING_RE = re.compile(r"^#{1,6}\s+")
HR_RE = re.compile(r"^---\s*$")
FENCE_RE = re.compile(r"^\s*```")


def compute_id(kind: str, num: str) -> str:
    return f"{KIND_TO_PREFIX[kind]}-{num.replace('.', '-')}"


def parse_baseurl(config_path: Path) -> str:
    text = config_path.read_text(encoding="utf-8")
    m = re.search(r"(?m)^baseurl:\s*(.+?)\s*$", text)
    if not m:
        return ""
    val = m.group(1).strip().strip('"').strip("'")
    if val == "/":
        return ""
    return val


def parse_front_matter(text: str) -> dict[str, str]:
    # Minimal YAML-ish parser: only `key: value` on a single line is supported.
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}
    fm = text[4:end].splitlines()
    out: dict[str, str] = {}
    for line in fm:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def compute_page_url(docs_root: Path, md_path: Path, front_matter: dict[str, str]) -> str:
    permalink = front_matter.get("permalink")
    if permalink:
        if not permalink.startswith("/"):
            permalink = "/" + permalink
        if permalink != "/" and not permalink.endswith("/"):
            permalink += "/"
        return permalink

    rel = md_path.relative_to(docs_root).with_suffix("")
    rel_posix = rel.as_posix()
    if rel_posix.endswith("/index"):
        rel_posix = rel_posix[: -len("/index")]
    if rel_posix == "index":
        return "/"
    if not rel_posix.startswith("/"):
        rel_posix = "/" + rel_posix
    if not rel_posix.endswith("/"):
        rel_posix += "/"
    return rel_posix


def strip_markdown(s: str) -> str:
    s = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r"\1", s)
    s = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", s)

    # Preserve MathJax spans before stripping HTML-like tags and Markdown
    # emphasis. A blanket ``<...>`` removal would otherwise corrupt comparisons
    # such as ``\(R < C\)`` and ``\(\epsilon > 0\)``, while blanket underscore
    # removal corrupts LaTeX subscripts such as ``\mathbb{R}_{\ge 0}``.
    math_spans: list[str] = []

    def _protect_math(match: re.Match[str]) -> str:
        math_spans.append(match.group(0))
        return f"\u0000MATH{len(math_spans) - 1}\u0000"

    s = re.sub(r"\\\\\(.+?\\\\\)", _protect_math, s)
    s = re.sub(r"\\\\\[.+?\\\\\]", _protect_math, s)
    s = re.sub(r"<[^>]+>", "", s)
    s = s.replace("`", "")
    s = s.replace("*", "")
    s = s.replace("_", "")

    for i, span in enumerate(math_spans):
        s = s.replace(f"\u0000MATH{i}\u0000", span)

    s = re.sub(r"\s+", " ", s).strip()
    return s


def extract_name(rest: str) -> str | None:
    rest = rest.strip()
    m = re.match(r"^\*\*([^*]+)\*\*", rest)
    if m:
        return m.group(1).strip()
    m = re.match(r"^（([^）]+)）", rest)
    if m:
        return m.group(1).strip()
    return None


def excerpt_from_lines(lines: list[str], start: int, max_chars: int = 240) -> str:
    in_fence = False
    buf: list[str] = []

    i = start
    while i < len(lines):
        raw = lines[i].rstrip("\n")

        if FENCE_RE.match(raw):
            in_fence = not in_fence
            i += 1
            continue
        if in_fence:
            i += 1
            continue

        if not raw.strip():
            break
        if HEADING_RE.match(raw) or HR_RE.match(raw) or LABEL_RE.match(raw):
            break
        if IAL_RE.match(raw):
            i += 1
            continue

        buf.append(raw.strip())
        joined = strip_markdown(" ".join(buf))
        if len(joined) >= max_chars:
            return joined[:max_chars].rstrip()

        i += 1

    joined = strip_markdown(" ".join(buf))
    return joined[:max_chars].rstrip()


def iter_markdown_files(docs_root: Path) -> list[Path]:
    out: list[Path] = []
    for p in docs_root.rglob("*.md"):
        if any(part.startswith("_") for part in p.relative_to(docs_root).parts):
            continue
        out.append(p)
    return sorted(out, key=lambda x: x.as_posix())


def build_index(docs_root: Path) -> dict:
    baseurl = parse_baseurl(docs_root / "_config.yml")
    items: list[dict] = []

    for md in iter_markdown_files(docs_root):
        text = md.read_text(encoding="utf-8")
        fm = parse_front_matter(text)
        page_title = fm.get("title")
        page_url = compute_page_url(docs_root, md, fm)

        lines = text.splitlines(keepends=True)
        i = 0
        while i < len(lines):
            line = lines[i].rstrip("\n")
            m = LABEL_RE.match(line)
            if not m:
                i += 1
                continue

            kind = m.group("kind")
            num = m.group("num")
            stmt_id = compute_id(kind, num)

            # Only index statements that already have a matching stable ID line.
            next_line = lines[i + 1].rstrip("\n") if i + 1 < len(lines) else ""
            m_ial = IAL_RE.match(next_line)
            if not m_ial or m_ial.group("id") != stmt_id:
                i += 1
                continue

            name = extract_name(m.group("rest"))
            excerpt = excerpt_from_lines(lines, i + 2)

            items.append(
                {
                    "id": stmt_id,
                    "kind": KIND_TO_PREFIX[kind],
                    "label": kind,
                    "number": num,
                    "name": name,
                    "url": f"{baseurl}{page_url}#{stmt_id}" if baseurl else f"{page_url}#{stmt_id}",
                    "page_title": page_title,
                    "page_url": f"{baseurl}{page_url}" if baseurl else page_url,
                    "source_path": md.as_posix(),
                    "excerpt": excerpt,
                }
            )

            i += 1

    data = {
        "schema_version": 1,
        "baseurl": baseurl,
        "items": items,
    }
    return data


def dump_json(data: dict) -> str:
    # Deterministic output: sort_keys and stable separators.
    return json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--docs-root", default="docs", help="Jekyll source directory (default: docs)")
    ap.add_argument("--out", default="docs/index.json", help="Output path (default: docs/index.json)")
    ap.add_argument("--check", action="store_true", help="Fail if the output file is not up-to-date")
    args = ap.parse_args()

    docs_root = Path(args.docs_root)
    out_path = Path(args.out)

    data = build_index(docs_root)
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

    out_path.write_text(rendered, encoding="utf-8")
    print(f"wrote: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
