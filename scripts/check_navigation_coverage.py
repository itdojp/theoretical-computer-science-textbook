#!/usr/bin/env python3
"""Validate that docs navigation covers the published Markdown pages.

The scheduled nav-link workflow historically read only top-level `path` fields.
This checker uses the same source of truth (`docs/_data/navigation.yml`) but
flattens nested items as well, then verifies that every configured path has a
corresponding docs page and every docs page is represented by navigation (except
for the top page `/`). It intentionally uses only the Python standard library so
it can run in CI without extra dependencies.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote

NAV_PATH_RE = re.compile(r"^\s*path:\s*(?P<value>.+?)\s*$")
FRONT_MATTER_RE = re.compile(r"^---\r?\n(.*?)\r?\n---\r?\n", re.DOTALL)
SCALAR_RE = re.compile(r"^(?P<key>[A-Za-z0-9_-]+):\s*(?P<value>.*?)\s*$")

EXCLUDED_PAGE_PARTS = {"assets"}


class CheckError(ValueError):
    pass


def unquote_scalar(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
        return value[1:-1]
    return value


def normalize_public_path(value: str, *, source: str) -> str:
    path = unquote_scalar(value)
    if not path:
        raise CheckError(f"{source}: path must not be empty")
    if path.startswith(("http://", "https://", "mailto:")):
        raise CheckError(f"{source}: external paths are not expected in navigation: {path!r}")
    if "{{" in path or "}}" in path:
        raise CheckError(f"{source}: Liquid expressions are not allowed in canonical paths")
    if "#" in path or "?" in path:
        raise CheckError(f"{source}: path must not include query or fragment: {path!r}")
    if "\\" in path:
        raise CheckError(f"{source}: path must use forward slashes: {path!r}")
    if not path.startswith("/"):
        path = "/" + path
    decoded = unquote(path)
    if any(part in (".", "..") for part in decoded.split("/") if part):
        raise CheckError(f"{source}: path traversal is not allowed: {path!r}")
    if "%2f" in path.lower() or "%5c" in path.lower():
        raise CheckError(f"{source}: encoded path separators are not allowed: {path!r}")
    lower = path.lower()
    if path != "/" and not lower.endswith((".html", ".htm", ".pdf", ".txt", "/")):
        path += "/"
    return path


def parse_front_matter(path: Path) -> dict[str, str]:
    match = FRONT_MATTER_RE.match(path.read_text(encoding="utf-8"))
    if not match:
        return {}
    data: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if line[:1].isspace():
            continue
        scalar = SCALAR_RE.match(line)
        if scalar:
            data[scalar.group("key")] = unquote_scalar(scalar.group("value"))
    return data


def navigation_paths(nav_path: Path) -> list[str]:
    paths: list[str] = []
    for lineno, line in enumerate(nav_path.read_text(encoding="utf-8").splitlines(), start=1):
        match = NAV_PATH_RE.match(line)
        if not match:
            continue
        paths.append(normalize_public_path(match.group("value"), source=f"{nav_path}:{lineno}"))
    return paths


def default_public_path(md_path: Path) -> str:
    rel = md_path.relative_to("docs")
    if md_path.name == "index.md":
        parent = rel.parent.as_posix()
        return "/" if parent == "." else f"/{parent}/"
    return f"/{rel.with_suffix('').as_posix()}/"


def docs_pages() -> dict[str, Path]:
    pages: dict[str, Path] = {}
    for md_path in sorted(Path("docs").rglob("*.md")):
        rel_parts = md_path.relative_to("docs").parts
        if any(part.startswith("_") for part in rel_parts):
            continue
        if any(part in EXCLUDED_PAGE_PARTS for part in rel_parts):
            continue
        fm = parse_front_matter(md_path)
        public_path = fm.get("permalink") or default_public_path(md_path)
        public_path = normalize_public_path(public_path, source=f"{md_path}:permalink")
        if public_path in pages:
            raise CheckError(f"duplicate public path: {public_path} ({pages[public_path]} and {md_path})")
        pages[public_path] = md_path
    return pages


def duplicates(values: list[str]) -> list[str]:
    seen: set[str] = set()
    dupes: list[str] = []
    for value in values:
        if value in seen and value not in dupes:
            dupes.append(value)
        seen.add(value)
    return dupes


def main() -> int:
    try:
        nav = navigation_paths(Path("docs/_data/navigation.yml"))
        pages = docs_pages()
    except CheckError as exc:
        print(exc, file=sys.stderr)
        return 1

    errors: list[str] = []
    for duplicate in duplicates(nav):
        errors.append(f"duplicate navigation path: {duplicate}")

    page_paths = set(pages)
    nav_paths = set(nav)
    for path in sorted(nav_paths - page_paths):
        errors.append(f"navigation path has no docs page: {path}")

    listed_paths = nav_paths | {"/"}
    for path in sorted(page_paths - listed_paths):
        errors.append(f"docs page is not listed in navigation: {pages[path]} -> {path}")

    if errors:
        print("navigation coverage check failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    root_pages = sum(1 for p in page_paths if p == "/")
    print(
        f"OK: {len(nav_paths)} navigation paths cover {len(page_paths) - root_pages} docs pages"
        f" (root '/' is implicit; {len(page_paths)} total)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
