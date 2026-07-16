import importlib.util
from pathlib import Path

import pytest


def _load_generate_search_data():
    repo_root = Path(__file__).resolve().parents[2]
    script = repo_root / "scripts" / "generate_search_data.py"
    spec = importlib.util.spec_from_file_location("generate_search_data", script)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_md_to_text_removes_kramdown_inline_anchor() -> None:
    m = _load_generate_search_data()
    text = "## 現在の提供状況 {#downloads-current}\n本文"

    assert m.md_to_text(text) == "現在の提供状況 本文"


def test_md_to_text_removes_kramdown_block_anchor() -> None:
    m = _load_generate_search_data()
    text = "## 第1章\n{: #appendix-e-chapter-1 }\n本文"

    assert m.md_to_text(text) == "第1章 本文"


def _write_search_chapter(docs: Path, *, with_id: bool = True) -> None:
    docs.mkdir(parents=True)
    (docs / "_config.yml").write_text(
        'baseurl: "/theoretical-computer-science-textbook"\n', encoding="utf-8"
    )
    chapter = docs / "chapter-1" / "index.md"
    chapter.parent.mkdir()
    anchor = '<span id="exq-ch1-001"></span>' if with_id else ""
    chapter.write_text(
        f"""---
title: 第1章
---

## 章末問題

### 基礎問題

1. {anchor}検索できる章末問題
""",
        encoding="utf-8",
    )


def test_search_data_includes_each_exercise_as_an_anchor_item(tmp_path: Path) -> None:
    module = _load_generate_search_data()
    docs = tmp_path / "docs"
    _write_search_chapter(docs)

    data = module.build_search_data(docs, docs / "_config.yml")
    exercise = next(row for row in data["items"] if "問題1（基礎問題）" in row["title"])

    assert exercise["url"].endswith("/chapter-1/#exq-ch1-001")
    assert exercise["excerpt"] == "検索できる章末問題"


def test_search_data_rejects_question_without_stable_id(tmp_path: Path) -> None:
    module = _load_generate_search_data()
    docs = tmp_path / "docs"
    _write_search_chapter(docs, with_id=False)

    with pytest.raises(ValueError, match="must contain exactly one exq stable ID"):
        module.build_search_data(docs, docs / "_config.yml")
