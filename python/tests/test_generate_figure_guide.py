import importlib.util
import sys
from pathlib import Path


def _load_generate_figure_guide():
    repo_root = Path(__file__).resolve().parents[2]
    script = repo_root / "scripts" / "generate_figure_guide.py"
    spec = importlib.util.spec_from_file_location("generate_figure_guide", script)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_render_markdown_lists_figures_with_role_and_links() -> None:
    m = _load_generate_figure_guide()
    entries = [
        m.FigureEntry(
            chapter_num=3,
            chapter_title="第3章 形式言語とオートマトン理論",
            part_title="Part I: 数学的基礎",
            section_title="3.2 正規言語と正規表現",
            role="直観図",
            lead_text="Thompson 構成の各規則",
            alt_text="Thompson 構成法：段階図",
            asset_path="assets/images/diagrams/ch3_regex_to_nfa_thompson_steps.svg",
        )
    ]

    rendered = m.render_markdown(entries)

    assert "総図版数: 1" in rendered
    assert "Part I: 数学的基礎: 1 図" in rendered
    assert "[Thompson 構成法：段階図](../chapter-3/#32-正規言語と正規表現)" in rendered
    assert "[SVG](../assets/images/diagrams/ch3_regex_to_nfa_thompson_steps.svg)" in rendered
    assert "本文ラベル: `Thompson 構成の各規則`" in rendered


def test_slugify_heading_matches_kramdown_style_for_used_headings() -> None:
    m = _load_generate_figure_guide()

    assert m.slugify_heading("3.3.2 正規表現からNFAへの変換プロセス") == "332-正規表現からnfaへの変換プロセス"
    assert m.slugify_heading("最小DFAとの関係（実務的な見方）") == "最小dfaとの関係実務的な見方"


def test_main_check_detects_outdated_generated_files(tmp_path, monkeypatch) -> None:
    m = _load_generate_figure_guide()

    docs_root = tmp_path / "docs"
    appendices_dir = docs_root / "appendices"
    chapter_dir = docs_root / "chapter-1"
    src_appendices_dir = tmp_path / "src" / "appendices"
    appendices_dir.mkdir(parents=True)
    chapter_dir.mkdir(parents=True)
    src_appendices_dir.mkdir(parents=True)

    (docs_root / "book-config.json").write_text(
        """
{
  "structure": {
    "parts": [
      {
        "title": "Part I: 数学的基礎",
        "chapters": ["1"]
      }
    ]
  }
}
""".strip()
        + "\n",
        encoding="utf-8",
    )
    (chapter_dir / "index.md").write_text(
        """
---
title: "第1章 数学的基礎"
---

# 第1章 数学的基礎

## 図のある節

直観図：全体像

![理論計算機科学の体系と相互関連]({{ '/assets/images/diagrams/ch1_theoretical_cs_overview.svg' | relative_url }})
""".lstrip(),
        encoding="utf-8",
    )
    (appendices_dir / "h.md").write_text("stale\n", encoding="utf-8")
    (src_appendices_dir / "h.md").write_text("stale\n", encoding="utf-8")

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "generate_figure_guide.py",
            "--docs-root",
            str(docs_root),
            "--config",
            str(docs_root / "book-config.json"),
            "--docs-out",
            str(appendices_dir / "h.md"),
            "--src-out",
            str(src_appendices_dir / "h.md"),
            "--check",
        ],
    )

    assert m.main() == 1


def test_main_check_passes_for_repository_files(monkeypatch) -> None:
    m = _load_generate_figure_guide()
    repo_root = Path(__file__).resolve().parents[2]

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "generate_figure_guide.py",
            "--docs-root",
            str(repo_root / "docs"),
            "--config",
            str(repo_root / "docs" / "book-config.json"),
            "--docs-out",
            str(repo_root / "docs" / "appendices" / "h.md"),
            "--src-out",
            str(repo_root / "src" / "appendices" / "h.md"),
            "--check",
        ],
    )

    assert m.main() == 0
