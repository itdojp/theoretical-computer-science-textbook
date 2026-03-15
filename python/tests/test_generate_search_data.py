import importlib.util
from pathlib import Path


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
