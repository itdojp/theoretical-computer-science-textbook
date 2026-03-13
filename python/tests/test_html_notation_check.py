import importlib.util
import sys
from pathlib import Path


def _load_html_notation_check():
    repo_root = Path(__file__).resolve().parents[2]
    script = repo_root / "scripts" / "html_notation_check.py"
    spec = importlib.util.spec_from_file_location("html_notation_check", script)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_main_rejects_mathbb_r_ge_zero_typo_in_built_html(tmp_path, monkeypatch) -> None:
    m = _load_html_notation_check()
    site_root = tmp_path / "_site"
    site_root.mkdir()
    (site_root / "index.html").write_text(
        '<script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js"></script>\n'
        '<p>\\(f: \\mathbb{R}{\\ge 0} \\to \\mathbb{R}_{\\ge 0}\\)</p>\n',
        encoding="utf-8",
    )
    monkeypatch.setattr(sys, "argv", ["html_notation_check.py", "--site-root", str(site_root)])

    assert m.main() == 1


def test_main_ignores_mathbb_r_ge_zero_typo_inside_code_blocks(tmp_path, monkeypatch) -> None:
    m = _load_html_notation_check()
    site_root = tmp_path / "_site"
    site_root.mkdir()
    (site_root / "index.html").write_text(
        '<script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js"></script>\n'
        '<pre><code>\\\\mathbb{R}{\\\\ge 0}</code></pre>\n',
        encoding="utf-8",
    )
    monkeypatch.setattr(sys, "argv", ["html_notation_check.py", "--site-root", str(site_root)])

    assert m.main() == 0


def test_main_rejects_markdown_emphasis_leaked_into_tex_span(tmp_path, monkeypatch) -> None:
    m = _load_html_notation_check()
    site_root = tmp_path / "_site"
    site_root.mkdir()
    (site_root / "index.html").write_text(
        '<script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js"></script>\n'
        '<p>\\(f: \\mathbb{R}<em>{\\ge 0} \\to \\mathbb{R}</em>{\\ge 0}\\)</p>\n',
        encoding="utf-8",
    )
    monkeypatch.setattr(sys, "argv", ["html_notation_check.py", "--site-root", str(site_root)])

    assert m.main() == 1
