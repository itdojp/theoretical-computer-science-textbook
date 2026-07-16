import importlib.util
import json
from pathlib import Path


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
