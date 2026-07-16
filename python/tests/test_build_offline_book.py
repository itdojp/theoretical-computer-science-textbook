import importlib.util
import json
from pathlib import Path

import pytest


def _load_build_offline_book():
    repo_root = Path(__file__).resolve().parents[2]
    script = repo_root / "scripts" / "build_offline_book.py"
    spec = importlib.util.spec_from_file_location("build_offline_book", script)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_normalize_for_pdf_rewrites_set_difference_tokens():
    m = _load_build_offline_book()
    text = "ヒント: 初期分割 {F, Q\\F} から開始する。\nA \\ B も同様。\n"
    out = m.normalize_for_pdf(text)
    assert f"Q \u2216 F" in out
    assert f"A \u2216 B" in out


def test_normalize_for_pdf_does_not_touch_code_fences():
    m = _load_build_offline_book()
    text = "```\nQ\\F\n```\n"
    out = m.normalize_for_pdf(text)
    assert "Q\\F" in out


def test_normalize_for_pdf_does_not_touch_latex_commands():
    m = _load_build_offline_book()
    text = "q\\in Q\nQ\\in F\nA\\cap B\n"
    out = m.normalize_for_pdf(text)
    assert out == text


def test_normalize_math_delimiters_for_pandoc():
    m = _load_build_offline_book()
    text = (
        r"inline \\(x \\in \\mathbb{R}\\) end" "\n"
        r"\\[" "\n" r"\\sum_i x_i" "\n" r"\\]" "\n"
    )

    out = m.normalize_math_delimiters_for_pandoc(text)

    assert "inline $x \\in \\mathbb{R}$ end" in out
    assert "$$\n\\sum_i x_i\n$$" in out


def test_normalize_single_backslash_math_delimiters_for_pandoc():
    m = _load_build_offline_book()
    text = (
        r"inline \(p \in \mathbb{R}\) end" "\n"
        r"\[\sum_i x_i\]" "\n"
    )

    out = m.normalize_math_delimiters_for_pandoc(text)

    assert "inline $p \\in \\mathbb{R}$ end" in out
    assert "$$\\sum_i x_i$$" in out


def test_normalize_inline_math_trims_invalid_boundary_spaces():
    m = _load_build_offline_book()

    out = m.normalize_math_delimiters_for_pandoc(
        r"double \\( \lvert X \rvert \\) and single \( p \)" "\n"
    )

    assert out == "double $\\lvert X \\rvert$ and single $p$\n"


def test_normalize_math_delimiters_preserves_single_commands_and_line_breaks():
    m = _load_build_offline_book()
    text = (
        r"\\(x \in \mathbb{R}\\)" "\n"
        r"\\[\begin{aligned}" "\n"
        r"a & = b \\\\" "\n"
        r"c & = d" "\n"
        r"\end{aligned}\\]" "\n"
    )

    out = m.normalize_math_delimiters_for_pandoc(text)

    assert "$x \\in \\mathbb{R}$" in out
    assert "$$\\begin{aligned}\n" in out
    assert "a & = b \\\\\n" in out
    assert "\\end{aligned}$$" in out


def test_normalize_math_delimiters_preserves_literal_parenthesis_before_closer():
    m = _load_build_offline_book()

    out = m.normalize_math_delimiters_for_pandoc(
        r"\\(T(\\langle R\rangle\\)\\)" "\n"
    )

    assert out == "$T(\\langle R\\rangle)$\n"


def test_normalize_math_delimiters_rejects_unclosed_math():
    m = _load_build_offline_book()

    with pytest.raises(ValueError, match="unclosed Web math delimiter"):
        m.normalize_math_delimiters_for_pandoc(r"\\(x \\in X")


def test_normalize_math_delimiters_preserves_code():
    m = _load_build_offline_book()
    text = (
        "`\\\\(inline-code\\\\)` and \\\\(math\\\\)\n"
        "```text\n\\\\(fenced\\\\)\n```\n"
        "~~~text\n\\\\[fenced\\\\]\n~~~\n"
    )

    out = m.normalize_math_delimiters_for_pandoc(text)

    assert "`\\\\(inline-code\\\\)` and $math$" in out
    assert "```text\n\\\\(fenced\\\\)\n```" in out
    assert "~~~text\n\\\\[fenced\\\\]\n~~~" in out


def test_normalize_math_delimiters_preserves_multiline_code_span():
    m = _load_build_offline_book()
    text = (
        "`code span starts\n"
        "\\\\(still code\\\\)\n"
        "` and \\\\(math\\\\)\n"
    )

    out = m.normalize_math_delimiters_for_pandoc(text)

    assert out == (
        "`code span starts\n"
        "\\\\(still code\\\\)\n"
        "` and $math$\n"
    )


def test_preprocess_real_chapter_six_normalizes_doubled_latex_commands():
    m = _load_build_offline_book()
    root = Path(__file__).resolve().parents[2]
    chapter = (root / "docs/chapter-6/index.md").read_text(encoding="utf-8")

    out = m.preprocess_markdown(chapter)

    assert r"$z_v\in\mathbb{R}$" in out
    assert r"$z_v\\in\\mathbb{R}$" not in out


def test_preprocess_real_chapter_two_produces_valid_pandoc_inline_math():
    m = _load_build_offline_book()
    root = Path(__file__).resolve().parents[2]
    chapter = (root / "docs/chapter-2/index.md").read_text(encoding="utf-8")

    out = m.preprocess_markdown(chapter)

    assert r"**定理 2.10** $\lvert \Sigma \rvert \ge 2$ を仮定" in out


def test_preprocess_real_appendix_normalizes_single_backslash_delimiters():
    m = _load_build_offline_book()
    root = Path(__file__).resolve().parents[2]
    appendix = (root / "docs/appendices/d.md").read_text(encoding="utf-8")

    out = m.preprocess_markdown(appendix)

    assert r"$p$ に対し" in out
    assert r"\(p\)" not in out


def test_rewrite_exercise_cross_links_for_offline_uses_internal_anchors():
    m = _load_build_offline_book()
    text = (
        "[解答](../appendices/c/#ex-sol-ch7-003)\n"
        "[章別解答](../appendices/c/#ex-sol-ch7)\n"
        "[元問題](../../chapter-7/#exq-ch7-003)\n"
        "[通常リンク](../appendices/d/)\n"
    )

    out = m.rewrite_exercise_cross_links_for_offline(text)

    assert "[解答](#ex-sol-ch7-003)" in out
    assert "[章別解答](#ex-sol-ch7)" in out
    assert "[元問題](#exq-ch7-003)" in out
    assert "[通常リンク](../appendices/d/)" in out


def test_preprocess_real_exercise_links_are_clickable_in_offline_book():
    m = _load_build_offline_book()
    root = Path(__file__).resolve().parents[2]
    chapter = (root / "docs/chapter-7/index.md").read_text(encoding="utf-8")
    appendix = (root / "docs/appendices/c.md").read_text(encoding="utf-8")

    chapter_out = m.preprocess_markdown(chapter)
    appendix_out = m.preprocess_markdown(appendix)

    assert "[付録Cの対応解答](#ex-sol-ch7-003)" in chapter_out
    assert "[第7章 問題3（基礎）](#exq-ch7-003)" in appendix_out
    assert "../appendices/c/#ex-sol-ch7-003" not in chapter_out
    assert "../../chapter-7/#exq-ch7-003" not in appendix_out


def test_publication_front_matter_uses_canonical_metadata():
    m = _load_build_offline_book()
    root = Path(__file__).resolve().parents[2]
    config = json.loads((root / "docs/book-config.json").read_text(encoding="utf-8"))

    front_matter = m.build_publication_front_matter(config)

    assert f"title: {config['title']}\n" in front_matter
    assert f"author: {config['author']}\n" in front_matter
    assert f"version: {config['version']}\n" in front_matter
    assert f"date: {config['publication']['release_date']}\n" in front_matter
    assert f"last_updated: {config['publication']['last_updated']}\n" in front_matter
