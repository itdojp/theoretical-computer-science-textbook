#!/usr/bin/env python3
"""Check structural consistency of Appendix C exercise answers.

This checker is intentionally structural. It verifies that the public docs copy and
source copy of Appendix C stay synchronized, that each Appendix C exercise block
has a problem statement, that exercises appear under the matching chapter section
in numeric order, and that explicit Appendix C exercise anchors referenced in the
quick navigation exist.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

CHAPTER_SECTION_RE = re.compile(r"^## 第(?P<chapter>\d+)章: .*?(?:\s+\{#(?P<anchor>ex-sol-ch\d+)\})?$", re.M)
EXERCISE_RE = re.compile(r"^### 練習問題(?P<chapter>\d+)\.(?P<number>\d+).*?$", re.M)
EXPLICIT_ANCHOR_RE = re.compile(r"\{#([A-Za-z0-9_-]+)\}")
APPENDIX_LINK_RE = re.compile(r"\(#(ex-[A-Za-z0-9_-]+)\)")


def line_no(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def collect_chapter_ranges(text: str) -> tuple[dict[int, tuple[int, int]], list[str]]:
    matches = list(CHAPTER_SECTION_RE.finditer(text))
    ranges: dict[int, tuple[int, int]] = {}
    errors: list[str] = []
    for idx, match in enumerate(matches):
        chapter = int(match.group("chapter"))
        expected_anchor = f"ex-sol-ch{chapter}"
        actual_anchor = match.group("anchor")
        if actual_anchor != expected_anchor:
            errors.append(
                f"line {line_no(text, match.start())}: 第{chapter}章 section must declare "
                f"'{{#{expected_anchor}}}' anchor"
            )
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        ranges[chapter] = (match.start(), end)
    return ranges, errors


def check_appendix(text: str) -> list[str]:
    errors: list[str] = []
    ranges, range_errors = collect_chapter_ranges(text)
    errors.extend(range_errors)

    for chapter in range(1, 13):
        if chapter not in ranges:
            errors.append(f"missing chapter section: 第{chapter}章")

    exercises_by_chapter: dict[int, list[tuple[int, int, int, int]]] = {chapter: [] for chapter in range(1, 13)}
    exercises = list(EXERCISE_RE.finditer(text))
    for idx, match in enumerate(exercises):
        chapter = int(match.group("chapter"))
        number = int(match.group("number"))
        block_end = exercises[idx + 1].start() if idx + 1 < len(exercises) else len(text)
        block = text[match.end() : block_end]

        if chapter not in ranges:
            errors.append(f"line {line_no(text, match.start())}: exercise for missing chapter {chapter}")
            continue

        start, end = ranges[chapter]
        if not (start <= match.start() < end):
            errors.append(
                f"line {line_no(text, match.start())}: 練習問題{chapter}.{number} is outside 第{chapter}章 section"
            )

        if "**問題**:" not in block:
            errors.append(f"line {line_no(text, match.start())}: 練習問題{chapter}.{number} lacks '**問題**:'")

        exercises_by_chapter.setdefault(chapter, []).append((number, match.start(), match.end(), block_end))

    for chapter, rows in exercises_by_chapter.items():
        numbers = [number for number, *_ in rows]
        if numbers != sorted(numbers):
            errors.append(f"第{chapter}章 exercise order is not ascending: {numbers}")
        if len(numbers) != len(set(numbers)):
            errors.append(f"第{chapter}章 exercise numbers contain duplicates: {numbers}")

    anchors = set(EXPLICIT_ANCHOR_RE.findall(text))

    for link in APPENDIX_LINK_RE.finditer(text):
        target = link.group(1)
        if target not in anchors:
            errors.append(f"line {line_no(text, link.start())}: broken Appendix C anchor link #{target}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--docs", default="docs/appendices/c.md")
    parser.add_argument("--src", default="src/appendices/c.md")
    args = parser.parse_args()

    docs_path = Path(args.docs)
    src_path = Path(args.src)
    docs = docs_path.read_text(encoding="utf-8")
    src = src_path.read_text(encoding="utf-8")

    errors: list[str] = []
    if docs != src:
        errors.append(f"{docs_path} and {src_path} differ")

    errors.extend(check_appendix(docs))

    if errors:
        print("appendix C consistency check failed:")
        for error in errors:
            print(error)
        return 1

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
