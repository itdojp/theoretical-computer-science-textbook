#!/usr/bin/env python3
"""Check that effort metadata has one canonical source and consistent readers."""

from __future__ import annotations

import argparse
import json
import re
import sys
from decimal import Decimal
from pathlib import Path
from typing import Any

RANGE_RE = re.compile(r"^約?(\d+(?:\.\d+)?)〜(\d+(?:\.\d+)?)時間$")
CHAPTER_KEYS = {str(number) for number in range(1, 13)}


def _read(path: Path, errors: list[str]) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        errors.append(f"{path}: cannot read file: {exc}")
        return ""


def _range(value: Any, name: str, errors: list[str]) -> tuple[Decimal, Decimal] | None:
    if not isinstance(value, str) or not (match := RANGE_RE.fullmatch(value)):
        errors.append(f"{name}: expected low〜high時間, got {value!r}")
        return None
    low, high = Decimal(match.group(1)), Decimal(match.group(2))
    if low > high:
        errors.append(f"{name}: low must not exceed high")
        return None
    return low, high


def _required_string(value: Any, name: str, errors: list[str]) -> str | None:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{name}: required non-empty string")
        return None
    return value


def validate_data(root: Path, errors: list[str]) -> dict[str, Any] | None:
    path = root / "docs/_data/chapter_effort.json"
    try:
        data = json.loads(_read(path, errors))
    except json.JSONDecodeError as exc:
        errors.append(f"{path}: invalid JSON: {exc}")
        return None
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        errors.append(f"{path}: schema_version must be 1")
        return None
    definitions = data.get("definitions")
    if not isinstance(definitions, dict):
        errors.append("chapter_effort.json: definitions must be an object")
        return None
    for key in ("text_browsing_time", "standard_learning"):
        if not isinstance(definitions.get(key), dict):
            errors.append(f"chapter_effort.json: definitions.{key} is required")
    text = definitions.get("text_browsing_time", {})
    standard = definitions.get("standard_learning", {})
    if isinstance(text, dict):
        _range(text.get("value"), "definitions.text_browsing_time.value", errors)
        for key in ("label", "basis", "scope"):
            _required_string(text.get(key), f"definitions.text_browsing_time.{key}", errors)
    total = _range(standard.get("total") if isinstance(standard, dict) else None,
                   "definitions.standard_learning.total", errors)
    if isinstance(standard, dict):
        for key in ("label", "basis", "exercise_scope"):
            _required_string(standard.get(key), f"definitions.standard_learning.{key}", errors)

    courses = data.get("courses")
    if not isinstance(courses, dict):
        errors.append("chapter_effort.json: courses must be an object")
    else:
        for key in ("through", "lecture_support", "selective", "relearning"):
            if not isinstance(courses.get(key), dict):
                errors.append(f"courses.{key}: required object")
            else:
                _required_string(courses[key].get("display"), f"courses.{key}.display", errors)

    chapters = data.get("chapters")
    if not isinstance(chapters, dict) or set(chapters) != CHAPTER_KEYS:
        actual = sorted(chapters) if isinstance(chapters, dict) else None
        errors.append(f"chapters: exact keys 1..12 required (actual={actual!r})")
    else:
        ranges = []
        for key in sorted(chapters, key=int):
            value = chapters[key].get("standard_learning_time") if isinstance(chapters[key], dict) else None
            parsed = _range(value, f"chapters.{key}.standard_learning_time", errors)
            if parsed:
                ranges.append(parsed)
        if total and ranges and (sum(x[0] for x in ranges), sum(x[1] for x in ranges)) != total:
            errors.append(f"chapter sums must equal total {total}, got "
                          f"{sum(x[0] for x in ranges), sum(x[1] for x in ranges)}")
    return data


def validate_readers(root: Path, data: dict[str, Any], errors: list[str]) -> None:
    layout = root / "docs/_layouts/book.html"
    layout_text = _read(layout, errors)
    active_layout = re.sub(r"<!--.*?-->", "", layout_text, flags=re.DOTALL)
    active_layout = re.sub(r"{%\s*comment\s*%}.*?{%\s*endcomment\s*%}", "", active_layout,
                           flags=re.DOTALL)
    layout_contracts = {
        "canonical chapter lookup": r"{%\s*assign\s+chapter_effort\s*=\s*site\.data\.chapter_effort\.chapters\[chapter_key\]\s*%}",
        "standard learning time output": r"{{\s*chapter_effort\.standard_learning_time(?:\s*\|\s*escape)?\s*}}",
        "standard learning time label": r"標準学習時間",
    }
    for name, pattern in layout_contracts.items():
        if not re.search(pattern, active_layout):
            errors.append(f"{layout}: missing active {name}")

    index = _read(root / "docs/index.md", errors)
    guide_candidates = (root / "docs/src/introduction/learning-guide.md",
                        root / "src/introduction/learning-guide.md",
                        root / "docs/introduction/learning-guide.md")
    definitions = data.get("definitions", {})
    text_definition = definitions.get("text_browsing_time", {})
    standard_definition = definitions.get("standard_learning", {})
    courses = data.get("courses", {})
    if not isinstance(text_definition, dict) or not isinstance(standard_definition, dict):
        return
    definition_values = {
        "text browsing label": text_definition.get("label"),
        "text browsing value": text_definition.get("value"),
        "text browsing basis": text_definition.get("basis"),
        "text browsing scope": text_definition.get("scope"),
        "standard-learning label": standard_definition.get("label"),
        "standard-learning total": standard_definition.get("total"),
        "standard-learning basis": standard_definition.get("basis"),
        "standard-learning exercise scope": standard_definition.get("exercise_scope"),
    }
    for name, value in definition_values.items():
        if isinstance(value, str) and value not in index:
            errors.append(f"{root / 'docs/index.md'}: {name} drifted")
    existing_guides = [path for path in guide_candidates if path.exists()]
    if not existing_guides:
        existing_guides = [guide_candidates[0]]
    for guide_path in existing_guides:
        guide = _read(guide_path, errors)
        for name, value in definition_values.items():
            if isinstance(value, str) and value not in guide:
                errors.append(f"{guide_path}: {name} drifted")
        for key, course in (courses.items() if isinstance(courses, dict) else ()):
            display = course.get("display") if isinstance(course, dict) else None
            if isinstance(display, str) and display not in guide:
                errors.append(f"{guide_path}: courses.{key}.display drifted")


def validate_legacy(root: Path, errors: list[str]) -> None:
    chapter_roots = [root / "docs/src", root / "src", root / "docs"]
    for base in chapter_roots:
        if not base.exists():
            continue
        for path in base.glob("chapter-*/**/*.md"):
            text = _read(path, errors)
            frontmatter = re.match(r"\A---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
            if frontmatter and re.search(r"(?m)^estimated_time\s*:", frontmatter.group(1)):
                errors.append(f"{path}: legacy estimated_time remains in front matter")
    config = root / "docs/book-config.json"
    text = _read(config, errors)
    if re.search(r'"estimated_time"\s*:', text):
        errors.append(f"{config}: legacy estimated_time remains")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="repository root")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    errors: list[str] = []
    data = validate_data(root, errors)
    if data is not None:
        validate_readers(root, data, errors)
    validate_legacy(root, errors)
    if errors:
        print("effort metadata check failed:", file=sys.stderr)
        print("\n".join(f"- {error}" for error in errors), file=sys.stderr)
        return 1
    print("OK: effort metadata is canonical and reader-facing references are synchronized")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
