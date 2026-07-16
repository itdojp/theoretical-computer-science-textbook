#!/usr/bin/env python3
"""Validate stable exercise IDs and Appendix C bidirectional references."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path

from exercise_references import ExerciseQuestion, collect_chapter_questions

CHAPTER_SECTION_RE = re.compile(r"^## 第(?P<chapter>\d+)章: .*?(?:\s+\{#(?P<anchor>ex-sol-ch\d+)\})?$", re.M)
SOLUTION_HEADING_RE = re.compile(r"^### 練習問題(?P<chapter>\d+)\.(?P<number>\d+).*?$", re.M)
SOLUTION_ID_RE = re.compile(r'<span\s+id="(?P<id>ex-sol-ch(?P<chapter>\d+)-\d{3})"\s*></span>')
SOURCE_LINK_RE = re.compile(
    r"^\*\*元問題\*\*:\s*\[(?P<label>[^\]]+)\]"
    r"\(\{\{\s*['\"]/chapter-(?P<path_chapter>\d+)/['\"]\s*\|\s*relative_url\s*\}\}"
    r"#(?P<id>exq-ch(?P<id_chapter>\d+)-\d{3})\)\s*$",
    re.M,
)
SOURCE_PART_RE = re.compile(r"^\*\*元問題の項目\*\*:\s*(?P<part>.+?)\s*$", re.M)
SOLUTION_TYPE_RE = re.compile(r"^\*\*解答種別\*\*:\s*(?P<kind>詳細解答|調査ガイド|参照実装)\s*$", re.M)
SOLUTION_LINK_RE = re.compile(r"\.\./appendices/c/#(?P<id>ex-sol-ch\d+-\d{3})")
RECIPROCAL_LINK_RE = re.compile(
    r"^-\s+\*\*(?P<kind>詳細解答|調査ガイド|参照実装)\*\*"
    r"(?:（項目:\s*(?P<part>[^）]+)）)?\s*:\s*"
    r"\[[^\]]+\]\(\.\./appendices/c/#(?P<id>ex-sol-ch\d+-\d{3})\)\s*$",
    re.M,
)
EXPLICIT_IAL_ANCHOR_RE = re.compile(r"\{#([A-Za-z0-9_-]+)\}")
HTML_ID_RE = re.compile(r'<(?:span|a)\s+id="([^"]+)"')
APPENDIX_LINK_RE = re.compile(r"\(#(?P<id>ex-[A-Za-z0-9_-]+)\)")
SOURCE_PART_VALUE_RE = re.compile(r"^\([a-z]\)(?:\s*,\s*\([a-z]\))*$")
SOURCE_PART_TOKEN_RE = re.compile(r"\(([a-z])\)")
RECIPROCAL_LINE_RE = re.compile(
    r"^-\s+\*\*(?:詳細解答|調査ガイド|参照実装)\*\*.*$", re.M
)

LEGACY_CHAPTER_ALIASES: dict[int, tuple[str, ...]] = {
    1: (
        "1-集合演算を実装せよ",
        "2-グラフの基本アルゴリズムを実装せよ",
        "3-関係の性質を判定するプログラムを作成せよ",
    ),
    2: (
        "1-簡単なチューリング機械シミュレータを実装せよ",
        "2-Post対応問題のインスタンスを解く総当たりアルゴリズムを実装せよ",
    ),
    3: (
        "1-DFAとNFAのシミュレータを実装せよ",
        "2-文脈自由文法のCYK構文解析アルゴリズムを実装せよ",
    ),
}

LEGACY_APPENDIX_ALIASES = {
    "ex-1-3",
    "ex-2-1",
    "ex-3-1",
    "ex-3-2",
    "ex-3-3",
    "ex-3-4",
    "ex-3-5",
    "ex-4-2",
    "ex-4-7",
    "ex-5-2",
    "ex-5-3",
    "ex-5-5",
    "ex-6-1",
    "ex-6-2",
    "ex-6-3",
    "ex-7-4",
    "ex-7-6",
    "ex-7-14",
    "ex-8-1",
    "ex-8-2",
    "ex-9-3",
    "ex-10-1",
    "ex-10-2",
    "ex-10-4",
    "ex-11-1",
    "ex-11-2",
    "ex-11-3",
    "ex-12-4",
    "ex-12-5",
    "ex-12-6",
    "ex-12-7",
    "ex-12-8",
}


@dataclass(frozen=True)
class AppendixSolution:
    chapter: int
    number: int
    stable_id: str
    source_id: str
    source_label: str
    source_part: str
    solution_type: str
    block: str
    line: int


class IdCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        value = dict(attrs).get("id")
        if value:
            self.ids.add(value)


def line_no(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def source_part_tokens(value: str) -> tuple[str, ...]:
    return tuple(SOURCE_PART_TOKEN_RE.findall(value))


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
        if chapter in ranges:
            errors.append(f"line {line_no(text, match.start())}: duplicate chapter section {chapter}")
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        ranges[chapter] = (match.start(), end)
    return ranges, errors


def _preceding_solution_id(text: str, heading_start: int) -> tuple[str, int] | None:
    prefix = text[:heading_start]
    nonempty = [line for line in prefix.splitlines() if line.strip()]
    if not nonempty:
        return None
    match = SOLUTION_ID_RE.fullmatch(nonempty[-1].strip())
    if not match:
        return None
    return match.group("id"), int(match.group("chapter"))


def collect_appendix_solutions(text: str) -> tuple[list[AppendixSolution], list[str]]:
    errors: list[str] = []
    ranges, range_errors = collect_chapter_ranges(text)
    errors.extend(range_errors)
    for chapter in range(1, 13):
        if chapter not in ranges:
            errors.append(f"missing chapter section: 第{chapter}章")

    matches = list(SOLUTION_HEADING_RE.finditer(text))
    solutions: list[AppendixSolution] = []
    numbers_by_chapter: dict[int, list[int]] = {chapter: [] for chapter in range(1, 13)}

    for idx, match in enumerate(matches):
        chapter = int(match.group("chapter"))
        number = int(match.group("number"))
        block_end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        block = text[match.end():block_end]
        current_line = line_no(text, match.start())
        numbers_by_chapter.setdefault(chapter, []).append(number)

        if chapter in ranges:
            start, end = ranges[chapter]
            if not (start <= match.start() < end):
                errors.append(f"line {current_line}: 練習問題{chapter}.{number} is outside 第{chapter}章 section")

        stable = _preceding_solution_id(text, match.start())
        if not stable:
            errors.append(f"line {current_line}: 練習問題{chapter}.{number} lacks preceding stable solution anchor")
            stable_id = ""
        else:
            stable_id, stable_chapter = stable
            if stable_chapter != chapter:
                errors.append(f"line {current_line}: solution ID {stable_id} does not match chapter {chapter}")

        if "**問題**:" not in block:
            errors.append(f"line {current_line}: 練習問題{chapter}.{number} lacks '**問題**:'")

        source_matches = list(SOURCE_LINK_RE.finditer(block))
        if len(source_matches) != 1:
            errors.append(
                f"line {current_line}: 練習問題{chapter}.{number} must contain exactly one '**元問題**:' link"
            )
            source_id = ""
            source_label = ""
        else:
            source = source_matches[0]
            source_id = source.group("id")
            source_label = source.group("label").strip()
            if int(source.group("path_chapter")) != chapter or int(source.group("id_chapter")) != chapter:
                errors.append(f"line {current_line}: source link for 練習問題{chapter}.{number} crosses chapters")

        part_matches = list(SOURCE_PART_RE.finditer(block))
        if len(part_matches) > 1:
            errors.append(f"line {current_line}: 練習問題{chapter}.{number} declares multiple source-item lines")
        source_part = part_matches[0].group("part").strip() if part_matches else ""

        type_matches = list(SOLUTION_TYPE_RE.finditer(block))
        if len(type_matches) != 1:
            errors.append(
                f"line {current_line}: 練習問題{chapter}.{number} must declare exactly one valid '**解答種別**:'"
            )
            solution_type = ""
        else:
            solution_type = type_matches[0].group("kind")

        solutions.append(
            AppendixSolution(
                chapter=chapter,
                number=number,
                stable_id=stable_id,
                source_id=source_id,
                source_label=source_label,
                source_part=source_part,
                solution_type=solution_type,
                block=block,
                line=current_line,
            )
        )

    for chapter, numbers in numbers_by_chapter.items():
        if numbers != sorted(numbers):
            errors.append(f"第{chapter}章 exercise order is not ascending: {numbers}")
        if len(numbers) != len(set(numbers)):
            errors.append(f"第{chapter}章 exercise numbers contain duplicates: {numbers}")

    anchors = set(EXPLICIT_IAL_ANCHOR_RE.findall(text)) | set(HTML_ID_RE.findall(text))
    missing_legacy = sorted(LEGACY_APPENDIX_ALIASES - anchors)
    if missing_legacy:
        errors.append(f"missing legacy Appendix C aliases: {missing_legacy}")
    for link in APPENDIX_LINK_RE.finditer(text):
        target = link.group("id")
        if target not in anchors:
            errors.append(f"line {line_no(text, link.start())}: broken Appendix C anchor link #{target}")

    return solutions, errors


def collect_questions(docs_root: Path) -> tuple[list[ExerciseQuestion], list[str]]:
    questions: list[ExerciseQuestion] = []
    errors: list[str] = []
    for chapter in range(1, 13):
        path = docs_root / f"chapter-{chapter}" / "index.md"
        if not path.exists():
            errors.append(f"missing chapter file: {path}")
            continue
        chapter_text = path.read_text(encoding="utf-8")
        chapter_questions, chapter_errors = collect_chapter_questions(chapter_text, chapter)
        for alias in LEGACY_CHAPTER_ALIASES.get(chapter, ()):
            if f'id="{alias}"' not in chapter_text:
                errors.append(f"{path}: missing legacy exercise alias #{alias}")
        questions.extend(chapter_questions)
        errors.extend(f"{path}: {error}" for error in chapter_errors)

        numbers = [question.display_number for question in chapter_questions]
        expected = list(range(1, len(numbers) + 1))
        if numbers != expected:
            errors.append(f"{path}: display numbers must be chapter-wide 1..N (actual={numbers})")
    return questions, errors


def validate_cross_references(
    questions: list[ExerciseQuestion], solutions: list[AppendixSolution]
) -> list[str]:
    errors: list[str] = []
    question_by_id: dict[str, ExerciseQuestion] = {}
    for question in questions:
        if not question.stable_id:
            continue
        if question.stable_id in question_by_id:
            errors.append(
                f"duplicate exercise ID {question.stable_id}: lines "
                f"{question_by_id[question.stable_id].line} and {question.line}"
            )
        question_by_id[question.stable_id] = question

    solution_by_id: dict[str, AppendixSolution] = {}
    source_keys: dict[tuple[str, str], AppendixSolution] = {}
    for solution in solutions:
        if solution.stable_id:
            if solution.stable_id in solution_by_id:
                errors.append(f"duplicate solution ID {solution.stable_id}")
            solution_by_id[solution.stable_id] = solution
        if solution.source_id not in question_by_id:
            errors.append(f"line {solution.line}: missing source exercise {solution.source_id!r}")
            continue

        key = (solution.source_id, solution.source_part)
        if key in source_keys:
            errors.append(
                f"line {solution.line}: duplicate answer mapping for source {solution.source_id} "
                f"item {solution.source_part or '(whole problem)'}"
            )
        source_keys[key] = solution

        question = question_by_id[solution.source_id]
        if question.chapter != solution.chapter:
            errors.append(f"line {solution.line}: source {solution.source_id} is in the wrong chapter")
        expected_label = re.compile(
            rf"^第{question.chapter}章\s+問題{question.display_number}(?:（|$)"
        )
        if not expected_label.search(solution.source_label):
            errors.append(
                f"line {solution.line}: source label {solution.source_label!r} must identify "
                f"第{question.chapter}章 問題{question.display_number}"
            )

        requested_parts = source_part_tokens(solution.source_part)
        if solution.source_part and (
            not SOURCE_PART_VALUE_RE.fullmatch(solution.source_part) or not requested_parts
        ):
            errors.append(
                f"line {solution.line}: invalid source-item syntax {solution.source_part!r}"
            )
        if requested_parts:
            question_without_answer_links = RECIPROCAL_LINE_RE.sub("", question.block)
            available_parts = set(source_part_tokens(question_without_answer_links))
            missing_parts = [part for part in requested_parts if part not in available_parts]
            if missing_parts:
                formatted = ", ".join(f"({part})" for part in missing_parts)
                errors.append(
                    f"line {solution.line}: source {solution.source_id} has no item {formatted}"
                )

        reciprocal_matches = [
            match
            for match in RECIPROCAL_LINK_RE.finditer(question.block)
            if match.group("id") == solution.stable_id
        ]
        if len(reciprocal_matches) != 1:
            errors.append(
                f"line {solution.line}: source {solution.source_id} must contain exactly one "
                f"structured reciprocal link to {solution.stable_id}"
            )
        else:
            reciprocal = reciprocal_matches[0]
            if reciprocal.group("kind") != solution.solution_type:
                errors.append(
                    f"line {solution.line}: reciprocal link to {solution.stable_id} has type "
                    f"{reciprocal.group('kind')}, expected {solution.solution_type}"
                )
            reciprocal_parts = source_part_tokens(reciprocal.group("part") or "")
            if reciprocal_parts != requested_parts:
                errors.append(
                    f"line {solution.line}: reciprocal link to {solution.stable_id} identifies "
                    f"items {reciprocal_parts}, expected {requested_parts}"
                )

    for question in questions:
        for match in SOLUTION_LINK_RE.finditer(question.block):
            target = match.group("id")
            if target not in solution_by_id:
                errors.append(f"line {question.line}: broken solution link #{target}")

    return errors


def validate_index(index_path: Path, questions: list[ExerciseQuestion]) -> list[str]:
    if not index_path.exists():
        return [f"missing exercise index: {index_path}"]
    try:
        data = json.loads(index_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"{index_path}: invalid JSON: {exc}"]

    indexed = {
        item.get("id"): item
        for item in data.get("items", [])
        if isinstance(item, dict) and item.get("kind") == "exercise"
    }
    expected = {question.stable_id: question for question in questions if question.stable_id}
    errors: list[str] = []
    missing = sorted(set(expected) - set(indexed))
    extra = sorted(set(indexed) - set(expected))
    if missing:
        errors.append(f"{index_path}: missing exercise IDs: {missing}")
    if extra:
        errors.append(f"{index_path}: unknown exercise IDs: {extra}")
    for stable_id, question in expected.items():
        item = indexed.get(stable_id)
        if not item:
            continue
        expected_suffix = f"/chapter-{question.chapter}/#{stable_id}"
        if not str(item.get("url", "")).endswith(expected_suffix):
            errors.append(f"{index_path}: {stable_id} URL must end with {expected_suffix}")
    return errors


def _html_ids(path: Path) -> set[str]:
    parser = IdCollector()
    parser.feed(path.read_text(encoding="utf-8"))
    return parser.ids


def validate_html(site_root: Path, questions: list[ExerciseQuestion], solutions: list[AppendixSolution]) -> list[str]:
    errors: list[str] = []
    questions_by_chapter: dict[int, list[ExerciseQuestion]] = {}
    for question in questions:
        questions_by_chapter.setdefault(question.chapter, []).append(question)
    for chapter, rows in questions_by_chapter.items():
        path = site_root / f"chapter-{chapter}" / "index.html"
        if not path.exists():
            errors.append(f"missing built chapter page: {path}")
            continue
        ids = _html_ids(path)
        for alias in LEGACY_CHAPTER_ALIASES.get(chapter, ()):
            if alias not in ids:
                errors.append(f"{path}: missing generated legacy exercise alias #{alias}")
        for question in rows:
            if question.stable_id and question.stable_id not in ids:
                errors.append(f"{path}: missing generated exercise anchor #{question.stable_id}")

    appendix_path = site_root / "appendices" / "c" / "index.html"
    if not appendix_path.exists():
        errors.append(f"missing built Appendix C page: {appendix_path}")
    else:
        ids = _html_ids(appendix_path)
        for alias in sorted(LEGACY_APPENDIX_ALIASES):
            if alias not in ids:
                errors.append(f"{appendix_path}: missing generated legacy Appendix C alias #{alias}")
        for solution in solutions:
            if solution.stable_id and solution.stable_id not in ids:
                errors.append(f"{appendix_path}: missing generated solution anchor #{solution.stable_id}")
    return errors


def check_repository(
    docs_appendix: Path,
    src_appendix: Path,
    docs_root: Path,
    src_root: Path,
    index_path: Path,
    site_root: Path | None = None,
) -> list[str]:
    errors: list[str] = []
    docs = docs_appendix.read_text(encoding="utf-8")
    src = src_appendix.read_text(encoding="utf-8")
    if docs != src:
        errors.append(f"{docs_appendix} and {src_appendix} differ")

    for chapter in range(1, 13):
        docs_chapter = docs_root / f"chapter-{chapter}" / "index.md"
        src_chapter = src_root / f"chapter-{chapter}" / "index.md"
        if docs_chapter.exists() and src_chapter.exists():
            if docs_chapter.read_text(encoding="utf-8") != src_chapter.read_text(encoding="utf-8"):
                errors.append(f"{docs_chapter} and {src_chapter} differ")

    questions, question_errors = collect_questions(docs_root)
    solutions, solution_errors = collect_appendix_solutions(docs)
    errors.extend(question_errors)
    errors.extend(solution_errors)
    errors.extend(validate_cross_references(questions, solutions))
    errors.extend(validate_index(index_path, questions))
    if site_root is not None:
        errors.extend(validate_html(site_root, questions, solutions))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--docs", default="docs/appendices/c.md")
    parser.add_argument("--src", default="src/appendices/c.md")
    parser.add_argument("--docs-root", default="docs")
    parser.add_argument("--src-root", default="src")
    parser.add_argument("--index", default="docs/index.json")
    parser.add_argument("--site-root")
    args = parser.parse_args()

    errors = check_repository(
        Path(args.docs),
        Path(args.src),
        Path(args.docs_root),
        Path(args.src_root),
        Path(args.index),
        Path(args.site_root) if args.site_root else None,
    )
    if errors:
        print("appendix C consistency check failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    questions, _ = collect_questions(Path(args.docs_root))
    solutions, _ = collect_appendix_solutions(Path(args.docs).read_text(encoding="utf-8"))
    suffix = " + generated HTML" if args.site_root else ""
    print(f"ok: {len(questions)} chapter exercises, {len(solutions)} Appendix C solutions{suffix}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
