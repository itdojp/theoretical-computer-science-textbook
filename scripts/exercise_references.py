#!/usr/bin/env python3
"""Shared parsing helpers for chapter-end exercise references."""

from __future__ import annotations

import re
from dataclasses import dataclass

CATEGORY_RE = re.compile(r"^### (?!#)(?P<title>.+?)\s*$")
LIST_QUESTION_RE = re.compile(r"^(?P<number>\d+)\.\s+(?P<prompt>.+?)\s*$")
HEADING_QUESTION_RE = re.compile(r"^####\s+(?P<number>\d+)\.\s+(?P<prompt>.+?)\s*$")
EXERCISE_ID_RE = re.compile(r"\b(exq-ch(?P<chapter>\d+)-\d{3})\b")
EXERCISE_SPAN_RE = re.compile(r'^\s*<span\s+id="exq-ch\d+-\d{3}"\s*></span>\s*$')
FENCE_RE = re.compile(r"^\s*```")


@dataclass(frozen=True)
class ExerciseQuestion:
    chapter: int
    display_number: int
    category: str
    stable_id: str
    prompt: str
    block: str
    line: int
    kind: str


def collect_chapter_questions(text: str, chapter: int) -> tuple[list[ExerciseQuestion], list[str]]:
    """Collect chapter-end questions and validate one primary ID per block."""
    marker = "## 章末問題"
    if marker not in text:
        return [], [f"chapter {chapter}: missing '{marker}' section"]

    prefix, section = text.split(marker, 1)
    base_line = prefix.count("\n") + 1
    lines = section.splitlines()
    category = ""
    category_lines: list[int] = []
    starts: list[tuple[int, str, re.Match[str], str]] = []
    in_fence = False

    for index, line in enumerate(lines):
        if FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue

        category_match = CATEGORY_RE.match(line)
        if category_match:
            category = category_match.group("title").strip()
            category_lines.append(index)
            continue

        question_match = LIST_QUESTION_RE.match(line)
        kind = "list"
        if not question_match:
            question_match = HEADING_QUESTION_RE.match(line)
            kind = "heading"
        if question_match:
            starts.append((index, category, question_match, kind))

    questions: list[ExerciseQuestion] = []
    errors: list[str] = []
    block_starts: list[int] = []
    for start, _question_category, _match, kind in starts:
        block_start = start
        if kind == "heading":
            # Heading-style implementation questions use a separate span before
            # the heading so that renumbering the visible heading does not
            # replace its historical auto-generated anchor.  Include that span
            # in this question's block, not in the preceding question's block.
            previous = start - 1
            while previous >= 0 and not lines[previous].strip():
                previous -= 1
            if previous >= 0 and EXERCISE_SPAN_RE.fullmatch(lines[previous]):
                block_start = previous
        block_starts.append(block_start)

    for position, (start, question_category, match, kind) in enumerate(starts):
        boundaries = [len(lines)]
        if position + 1 < len(starts):
            boundaries.append(block_starts[position + 1])
        boundaries.extend(index for index in category_lines if index > start)
        end = min(boundaries)
        block = "\n".join(lines[block_starts[position]:end]).rstrip() + "\n"
        ids = EXERCISE_ID_RE.findall(block)
        stable_ids = [row[0] for row in ids]
        # ``base_line`` is the one-based line number of the section marker,
        # while ``start`` is the zero-based offset after that marker.
        display_line = base_line + start

        if not question_category or question_category == "取り組み方ガイド":
            errors.append(f"line {display_line}: chapter {chapter} question is outside an exercise category")
        if len(stable_ids) != 1:
            errors.append(
                f"line {display_line}: chapter {chapter} question {match.group('number')} "
                f"must contain exactly one exq stable ID (found {stable_ids})"
            )
            stable_id = stable_ids[0] if stable_ids else ""
        else:
            stable_id = stable_ids[0]
            id_match = EXERCISE_ID_RE.fullmatch(stable_id)
            assert id_match is not None, f"parser returned an invalid exercise ID: {stable_id}"
            id_chapter = int(id_match.group("chapter"))
            if id_chapter != chapter:
                errors.append(
                    f"line {display_line}: exercise ID {stable_id} does not match chapter {chapter}"
                )

        questions.append(
            ExerciseQuestion(
                chapter=chapter,
                display_number=int(match.group("number")),
                category=question_category,
                stable_id=stable_id,
                prompt=match.group("prompt").strip(),
                block=block,
                line=display_line,
                kind=kind,
            )
        )

    return questions, errors
