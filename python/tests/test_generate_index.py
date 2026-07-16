from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


def _load_generate_index():
    repo_root = Path(__file__).resolve().parents[2]
    script = repo_root / "scripts" / "generate_index.py"
    spec = importlib.util.spec_from_file_location("generate_index", script)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _write_chapter(docs: Path, *, with_id: bool = True) -> None:
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

1. {anchor}安定 ID 付きの問題
""",
        encoding="utf-8",
    )


def test_build_index_includes_exercise_anchor_and_excerpt(tmp_path: Path) -> None:
    module = _load_generate_index()
    docs = tmp_path / "docs"
    _write_chapter(docs)

    data = module.build_index(docs)
    item = next(row for row in data["items"] if row["kind"] == "exercise")

    assert item["id"] == "exq-ch1-001"
    assert item["number"] == "1.1"
    assert item["name"] == "基礎問題"
    assert item["url"].endswith("/chapter-1/#exq-ch1-001")
    assert item["excerpt"] == "安定 ID 付きの問題"


def test_build_index_rejects_question_without_stable_id(tmp_path: Path) -> None:
    module = _load_generate_index()
    docs = tmp_path / "docs"
    _write_chapter(docs, with_id=False)

    with pytest.raises(ValueError, match="must contain exactly one exq stable ID"):
        module.build_index(docs)
