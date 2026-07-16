from __future__ import annotations

import json
import sys
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from check_appendix_c_consistency import (  # noqa: E402
    AppendixSolution,
    LEGACY_APPENDIX_ALIASES,
    LEGACY_CHAPTER_ALIASES,
    check_repository,
    validate_cross_references,
    validate_html,
    validate_index,
)
from exercise_references import ExerciseQuestion  # noqa: E402


def _question(
    *,
    stable_id: str = "exq-ch1-001",
    block: str = (
        '1. <span id="exq-ch1-001"></span>問題\n\n'
        "- **詳細解答**: [対応解答](../appendices/c/#ex-sol-ch1-001)\n"
    ),
    line: int = 10,
) -> ExerciseQuestion:
    return ExerciseQuestion(1, 1, "基礎問題", stable_id, "問題", block, line, "list")


def _solution(
    *,
    stable_id: str = "ex-sol-ch1-001",
    source_id: str = "exq-ch1-001",
    source_label: str = "第1章 問題1（基礎）",
    source_part: str = "",
    solution_type: str = "詳細解答",
    line: int = 20,
) -> AppendixSolution:
    return AppendixSolution(
        1,
        1,
        stable_id,
        source_id,
        source_label,
        source_part,
        solution_type,
        "",
        line,
    )


def _write_repository_fixture(root: Path) -> tuple[Path, Path, Path, Path, Path, Path]:
    docs_root = root / "docs"
    src_root = root / "src"
    site_root = root / "_site"
    appendix_parts: list[str] = []
    index_items: list[dict[str, str]] = []

    for chapter in range(1, 13):
        question_id = f"exq-ch{chapter}-001"
        solution_id = f"ex-sol-ch{chapter}-001"
        chapter_text = f"""# 第{chapter}章

## 章末問題

### 基礎問題

1. <span id="{question_id}"></span>第{chapter}章の問題

- **詳細解答**: [付録Cの対応解答](../appendices/c/#{solution_id})
"""
        chapter_text += "\n".join(
            f'<span id="{alias}"></span>'
            for alias in LEGACY_CHAPTER_ALIASES.get(chapter, ())
        )
        for source_root in (docs_root, src_root):
            path = source_root / f"chapter-{chapter}" / "index.md"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(chapter_text, encoding="utf-8")

        appendix_parts.append(
            f"""## 第{chapter}章: 解答 {{#ex-sol-ch{chapter}}}

<span id="{solution_id}"></span>
### 練習問題{chapter}.1

**問題**: 第{chapter}章の問題

**元問題**: [第{chapter}章 問題1]({{{{ '/chapter-{chapter}/' | relative_url }}}}#{question_id})

**解答種別**: 詳細解答

解答本文。
"""
        )
        index_items.append(
            {
                "id": question_id,
                "kind": "exercise",
                "url": f"/theoretical-computer-science-textbook/chapter-{chapter}/#{question_id}",
            }
        )

        html = site_root / f"chapter-{chapter}" / "index.html"
        html.parent.mkdir(parents=True, exist_ok=True)
        chapter_html = [f'<p id="{question_id}">問題</p>']
        chapter_html.extend(
            f'<span id="{alias}"></span>'
            for alias in LEGACY_CHAPTER_ALIASES.get(chapter, ())
        )
        html.write_text("\n".join(chapter_html), encoding="utf-8")

    appendix_text = "\n".join(appendix_parts) + "\n" + "\n".join(
        f'<span id="{alias}"></span>' for alias in sorted(LEGACY_APPENDIX_ALIASES)
    )
    docs_appendix = docs_root / "appendices" / "c.md"
    src_appendix = src_root / "appendices" / "c.md"
    docs_appendix.parent.mkdir(parents=True, exist_ok=True)
    src_appendix.parent.mkdir(parents=True, exist_ok=True)
    docs_appendix.write_text(appendix_text, encoding="utf-8")
    src_appendix.write_text(appendix_text, encoding="utf-8")

    index_path = docs_root / "index.json"
    index_path.write_text(json.dumps({"items": index_items}), encoding="utf-8")
    appendix_html = site_root / "appendices" / "c" / "index.html"
    appendix_html.parent.mkdir(parents=True, exist_ok=True)
    appendix_html.write_text(
        "\n".join(
            [
                *(f'<span id="ex-sol-ch{chapter}-001"></span>' for chapter in range(1, 13)),
                *(f'<span id="{alias}"></span>' for alias in sorted(LEGACY_APPENDIX_ALIASES)),
            ]
        ),
        encoding="utf-8",
    )
    return docs_appendix, src_appendix, docs_root, src_root, index_path, site_root


def test_repository_fixture_satisfies_source_index_and_html_contract(tmp_path: Path) -> None:
    paths = _write_repository_fixture(tmp_path)

    assert check_repository(*paths) == []


def test_repository_contract_rejects_removed_legacy_alias(tmp_path: Path) -> None:
    paths = _write_repository_fixture(tmp_path)
    alias = LEGACY_CHAPTER_ALIASES[1][0]
    for source_root in (paths[2], paths[3]):
        chapter = source_root / "chapter-1" / "index.md"
        chapter.write_text(
            chapter.read_text(encoding="utf-8").replace(f'<span id="{alias}"></span>', ""),
            encoding="utf-8",
        )

    errors = check_repository(*paths)

    assert any(f"missing legacy exercise alias #{alias}" in error for error in errors)


def test_repository_contract_reports_missing_source_chapter_copy(tmp_path: Path) -> None:
    paths = _write_repository_fixture(tmp_path)
    missing = paths[3] / "chapter-7" / "index.md"
    missing.unlink()

    errors = check_repository(*paths)

    assert f"missing src chapter copy: {missing}" in errors


def test_cross_reference_validation_detects_duplicates_and_missing_reciprocal_links() -> None:
    question = _question(block="1. 問題\n    {: #exq-ch1-001 }\n")
    duplicate_question = _question(line=11)
    first = _solution()
    duplicate_mapping = _solution(stable_id="ex-sol-ch1-002", line=21)

    errors = validate_cross_references(
        [question, duplicate_question],
        [first, duplicate_mapping, _solution(source_id="exq-ch1-999", line=22)],
    )

    assert any("duplicate exercise ID" in error for error in errors)
    assert any("duplicate answer mapping" in error for error in errors)
    assert any("structured reciprocal link" in error for error in errors)
    assert any("missing source exercise" in error for error in errors)


def test_cross_reference_validation_detects_misleading_source_label() -> None:
    errors = validate_cross_references(
        [_question()],
        [_solution(source_label="第1章 問題10（基礎）")],
    )

    assert any("must identify 第1章 問題1" in error for error in errors)


def test_reciprocal_type_must_be_on_the_link_to_that_solution() -> None:
    question = _question(
        block=(
            '1. <span id="exq-ch1-001"></span>問題\n\n'
            "- **調査ガイド**: [対応解答](../appendices/c/#ex-sol-ch1-001)\n"
            "補足では **詳細解答** という語にも言及する。\n"
        )
    )

    errors = validate_cross_references([question], [_solution(solution_type="詳細解答")])

    assert any("has type 調査ガイド, expected 詳細解答" in error for error in errors)


def test_source_item_must_exist_and_match_reciprocal_link() -> None:
    question = _question(
        block=(
            '1. <span id="exq-ch1-001"></span>複数項目\n'
            "   (a) 甲\n"
            "   (b) 乙\n\n"
            "- **詳細解答**（項目: (z)）: "
            "[対応解答](../appendices/c/#ex-sol-ch1-001)\n"
        )
    )

    errors = validate_cross_references(
        [question],
        [_solution(source_part="(z)")],
    )

    assert any("has no item (z)" in error for error in errors)


def test_index_validation_detects_missing_exercise(tmp_path: Path) -> None:
    index_path = tmp_path / "index.json"
    index_path.write_text('{"items": []}', encoding="utf-8")

    errors = validate_index(index_path, [_question()])

    assert errors == [f"{index_path}: missing exercise IDs: ['exq-ch1-001']"]


def test_html_validation_detects_missing_question_and_solution_anchors(tmp_path: Path) -> None:
    chapter = tmp_path / "chapter-1" / "index.html"
    appendix = tmp_path / "appendices" / "c" / "index.html"
    chapter.parent.mkdir(parents=True)
    appendix.parent.mkdir(parents=True)
    chapter.write_text("<p>問題</p>", encoding="utf-8")
    appendix.write_text("<p>解答</p>", encoding="utf-8")

    errors = validate_html(tmp_path, [_question()], [_solution()])

    assert any("missing generated exercise anchor #exq-ch1-001" in error for error in errors)
    assert any("missing generated solution anchor #ex-sol-ch1-001" in error for error in errors)
