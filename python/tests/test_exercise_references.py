from __future__ import annotations

import sys
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from exercise_references import collect_chapter_questions  # noqa: E402


def test_collects_list_and_heading_questions_without_stealing_next_span() -> None:
    text = """# Chapter

## 章末問題

### 基礎問題

1. <span id="exq-ch1-001"></span>一つ目の問題

- **詳細解答**: [対応解答](../appendices/c/#ex-sol-ch1-001)

### 実装課題

<span id="exq-ch1-002"></span>
#### 2. 二つ目の問題

本文。

<span id="exq-ch1-003"></span>
#### 3. 三つ目の問題

本文。
"""

    questions, errors = collect_chapter_questions(text, 1)

    assert errors == []
    assert [question.stable_id for question in questions] == [
        "exq-ch1-001",
        "exq-ch1-002",
        "exq-ch1-003",
    ]
    assert "ex-sol-ch1-001" in questions[0].block
    assert "exq-ch1-003" not in questions[1].block


def test_reports_missing_and_cross_chapter_ids() -> None:
    text = """## 章末問題

### 基礎問題

1. ID がない問題

2. 別章の ID を持つ問題
    {: #exq-ch2-002 }
"""

    questions, errors = collect_chapter_questions(text, 1)

    assert [question.stable_id for question in questions] == ["", "exq-ch2-002"]
    assert any("must contain exactly one" in error for error in errors)
    assert any("does not match chapter 1" in error for error in errors)
