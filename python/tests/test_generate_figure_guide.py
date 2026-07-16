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
    assert "## 目的別ショートリスト" in rendered
    assert "### 直観図を見たいとき" in rendered
    assert "[Thompson 構成法：段階図]({{ '/chapter-3/#32-正規言語と正規表現' | relative_url }})" in rendered
    assert "[SVG]({{ '/assets/images/diagrams/ch3_regex_to_nfa_thompson_steps.svg' | relative_url }})" in rendered
    assert "節: 「3.2 正規言語と正規表現」" in rendered
    assert "本文ラベル: 「Thompson 構成の各規則」" in rendered
    assert "図だけを拡大して見たいときは SVG リンク" in rendered
    assert "scripts/generate_figure_guide.py" not in rendered
    assert "`Thompson 構成の各規則`" not in rendered


def test_slugify_heading_matches_kramdown_style_for_used_headings() -> None:
    m = _load_generate_figure_guide()

    assert m.slugify_heading("3.3.2 正規表現からNFAへの変換プロセス") == "332-正規表現からnfaへの変換プロセス"
    assert m.slugify_heading("最小DFAとの関係（実務的な見方）") == "最小dfaとの関係実務的な見方"


def test_format_quoted_text_wraps_plain_text_without_code_span() -> None:
    m = _load_generate_figure_guide()

    assert m.format_quoted_text("AWGN 容量 \\(C = \\frac{1}{2} \\log_2(1+\\mathrm{SNR})\\) の曲線") == "「AWGN 容量 \\(C = \\frac{1}{2} \\log_2(1+\\mathrm{SNR})\\) の曲線」"


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


def test_build_purpose_shortlists_groups_entries_by_reader_goal() -> None:
    m = _load_generate_figure_guide()
    entries = [
        m.FigureEntry(
            chapter_num=3,
            chapter_title="第3章 形式言語とオートマトン理論",
            part_title="Part I: 数学的基礎",
            section_title="3.2 有限オートマトン",
            role="直観図",
            lead_text="有限オートマトンの全体像",
            alt_text="有限オートマトンの全体像",
            asset_path="assets/images/diagrams/ch3_finite_automata_overview.svg",
        ),
        m.FigureEntry(
            chapter_num=8,
            chapter_title="第8章 グラフ理論とネットワーク",
            part_title="Part III: 高度なトピック",
            section_title="8.2 単一始点最短路",
            role="例示図",
            lead_text="Dijkstra の逐次確定",
            alt_text="Dijkstra 法の逐次確定の例",
            asset_path="assets/images/diagrams/ch8_dijkstra_step_trace.svg",
        ),
        m.FigureEntry(
            chapter_num=9,
            chapter_title="第9章 論理学と形式的手法",
            part_title="Part III: 高度なトピック",
            section_title="9.1 命題論理",
            role="比較図",
            lead_text="DPLL と CDCL の対比",
            alt_text="DPLL と CDCL の対比",
            asset_path="assets/images/diagrams/ch9_dpll_cdcl_side_by_side.svg",
        ),
        m.FigureEntry(
            chapter_num=11,
            chapter_title="第11章 暗号理論の数学的基礎",
            part_title="Part IV: 応用理論",
            section_title="11.2 共通鍵暗号",
            role="構成図",
            lead_text="AEAD の処理フロー",
            alt_text="AEAD の処理フロー",
            asset_path="assets/images/diagrams/ch11_aead_flow_overview.svg",
        ),
        m.FigureEntry(
            chapter_num=None,
            chapter_title="付録I: 概念マップ",
            part_title="付録",
            section_title="12章の概念マップ",
            role="概念図",
            lead_text="必須・強く推奨・横断の3種で見る章依存",
            alt_text="本書12章の概念マップ",
            asset_path="assets/images/diagrams/appendix_i_reading_dependency_map.svg",
            appendix_id="i",
            source_anchor="appendix-i-map",
        ),
    ]

    shortlists = m.build_purpose_shortlists(entries)

    assert [entry.alt_text for entry in shortlists["直観図"]] == ["有限オートマトンの全体像"]
    assert [entry.alt_text for entry in shortlists["例示図"]] == ["Dijkstra 法の逐次確定の例"]
    assert [entry.alt_text for entry in shortlists["比較図"]] == ["DPLL と CDCL の対比"]
    assert [entry.alt_text for entry in shortlists["概念図"]] == ["本書12章の概念マップ"]
    assert [entry.alt_text for entry in shortlists["手順/構成図"]] == ["AEAD の処理フロー"]


def test_build_purpose_shortlists_does_not_fall_through_when_primary_bucket_is_full() -> None:
    m = _load_generate_figure_guide()
    entries = [
        m.FigureEntry(
            chapter_num=index + 1,
            chapter_title=f"第{index + 1}章",
            part_title="Part I: 数学的基礎",
            section_title=f"{index + 1}.1 直観図の節",
            role="直観図",
            lead_text=f"直観図 {index + 1}",
            alt_text=f"直観図 {index + 1}",
            asset_path=f"assets/images/diagrams/sample_{index + 1}.svg",
        )
        for index in range(m.PURPOSE_SHORTLIST_LIMIT)
    ]
    overflow_entry = m.FigureEntry(
        chapter_num=99,
        chapter_title="第99章",
        part_title="Part I: 数学的基礎",
        section_title="99.1 直観図の節",
        role="直観図",
        lead_text="直観図だけで分類される項目",
        alt_text="直観図の overflow 項目",
        asset_path="assets/images/diagrams/sample_overflow.svg",
    )

    shortlists = m.build_purpose_shortlists(entries + [overflow_entry])

    assert [entry.alt_text for entry in shortlists["直観図"]] == [f"直観図 {index + 1}" for index in range(m.PURPOSE_SHORTLIST_LIMIT)]
    assert "直観図の overflow 項目" not in [entry.alt_text for entry in shortlists["例示図"]]
    assert "直観図の overflow 項目" not in [entry.alt_text for entry in shortlists["比較図"]]
    assert "直観図の overflow 項目" not in [entry.alt_text for entry in shortlists["概念図"]]
    assert "直観図の overflow 項目" not in [entry.alt_text for entry in shortlists["手順/構成図"]]


def test_collect_figures_includes_appendix_i_images_and_skips_invalid_duplicates(tmp_path) -> None:
    m = _load_generate_figure_guide()
    docs_root = tmp_path / "docs"
    appendix_dir = docs_root / "appendices"
    appendix_dir.mkdir(parents=True)
    (appendix_dir / "i.md").write_text(
        """---
title: \"付録I: 概念マップ\"
---

# 付録I: 概念マップ

## 学習経路 {#reading-paths}

![最初の図]({{ '/assets/images/diagrams/concept-first.svg' | relative_url }})
![同じ図]({{ '/assets/images/diagrams/concept-first.svg' | relative_url }})
![外部画像](https://example.invalid/image.svg)
![不正な相対パス](../assets/images/diagrams/not-listed.svg)
![path traversal]({{ '/assets/images/diagrams/../../not-listed.svg' | relative_url }})
![encoded traversal]({{ '/assets/images/diagrams/%2e%2e/%2E%2E/not-listed.svg' | relative_url }})

## 章間の関係

![二番目の図]({{ '/assets/images/diagrams/concept-second.svg' | relative_url }})
""",
        encoding="utf-8",
    )

    entries = m.collect_figures(docs_root, {"structure": {"parts": []}})

    assert [entry.alt_text for entry in entries] == ["最初の図", "二番目の図"]
    assert all(entry.appendix_id == "i" for entry in entries)
    assert [entry.source_anchor for entry in entries] == ["reading-paths", "章間の関係"]

    rendered = m.render_markdown(entries)
    assert "### 付録I" in rendered
    assert rendered.count("appendix-i-figure-") == 2
    assert "同じ図" not in rendered
    assert "not-listed.svg" not in rendered
    assert "[付録Iへ戻る]({{ '/appendices/i/#reading-paths' | relative_url }})" in rendered


def test_collect_figures_without_appendix_i_keeps_chapter_only_behavior(tmp_path) -> None:
    m = _load_generate_figure_guide()
    docs_root = tmp_path / "docs"
    chapter_dir = docs_root / "chapter-1"
    chapter_dir.mkdir(parents=True)
    (chapter_dir / "index.md").write_text(
        """---
title: \"第1章\"
---

## 図の節 {#stable-figure-section}

![章の図]({{ '/assets/images/diagrams/ch1.svg' | relative_url }})
""",
        encoding="utf-8",
    )

    entries = m.collect_figures(docs_root, {"structure": {"parts": []}})

    assert len(entries) == 1
    assert entries[0].chapter_num == 1
    assert entries[0].appendix_id is None
    assert entries[0].source_anchor == "stable-figure-section"
    assert m.context_link(entries[0]) == "{{ '/chapter-1/#stable-figure-section' | relative_url }}"
    assert "### 付録I" not in m.render_markdown(entries)
