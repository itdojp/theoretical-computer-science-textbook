from pathlib import Path
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[2]
DOCS_MAP = ROOT / "docs/appendices/i.md"
SRC_MAP = ROOT / "src/appendices/i.md"
SVG_MAP = ROOT / "docs/assets/images/diagrams/appendix_i_reading_dependency_map.svg"


def _read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_concept_map_mirror_and_all_chapter_routes() -> None:
    docs = DOCS_MAP.read_text(encoding="utf-8")
    assert docs == SRC_MAP.read_text(encoding="utf-8")

    for chapter in range(1, 13):
        assert f"'/chapter-{chapter}/'" in docs
        assert f"**[第{chapter}章]" in docs


def test_concept_map_preserves_reader_contracts() -> None:
    text = DOCS_MAP.read_text(encoding="utf-8")

    for marker in (
        "初読前",
        "読書中",
        "読了後",
        "必須前提",
        "強く推奨する前提",
        "応用・横断的関連",
        "目的別ショートカット",
        "横断概念の再読経路",
        "安全なメッセージ配送基盤",
        "図は主要辺の俯瞰",
        "主要辺のテキスト版",
    ):
        assert marker in text

    for part in range(1, 5):
        assert f"appendix-i-part-{part}" in text

    for concept in (
        "証明・反例",
        "計算モデルと言語",
        "還元と下界",
        "漸近解析・確率・償却",
        "グラフと最適化",
        "論理・仕様・検証",
        "情報・安全性・並行性",
    ):
        assert f"**{concept}**" in text


def test_concept_map_svg_and_text_edge_contracts_match() -> None:
    text = DOCS_MAP.read_text(encoding="utf-8")
    svg = SVG_MAP.read_text(encoding="utf-8")
    text_lanes = (
        "**必須前提（実線）**: 1→2・3・6・7・8・9・10・11・12、2→4・5",
        "**強く推奨する前提（破線）**: 3→4、4→5、5→6・11、6→7・8・10・12、7→8、3→9、10→11、9→12",
        "**応用・横断的関連（点線）**: 4↔9、7↔12、8↔10・12、9↔11、10↔12、11↔12",
    )
    svg_lanes = (
        "1→2・3・6・7・8・9・10・11・12　　2→4・5",
        "3⇢4　4⇢5　5⇢6・11　6⇢7・8・10・12　7⇢8　3⇢9　10⇢11　9⇢12",
        "4⋯9　　7⋯12　　8⋯10・12　　9⋯11　　10⋯12　　11⋯12",
    )

    for lane in text_lanes:
        assert lane in text
    for lane in svg_lanes:
        assert lane in svg

    for chapter_contract in (
        "第7章 データ構造の理論]({{ '/chapter-7/' | relative_url }})**\n   - 必須前提: 第1章の関係・関数・漸近記法。\n   - 強く推奨する前提: 第6章。",
        "第8章 グラフ理論とネットワーク]({{ '/chapter-8/' | relative_url }})**\n   - 必須前提: 第1章のグラフ。\n   - 強く推奨する前提: 第6章のアルゴリズム解析と第7章",
        "第11章 暗号理論の数学的基礎]({{ '/chapter-11/' | relative_url }})**\n    - 必須前提: 第1章の確率・合同算術・証明。\n    - 強く推奨する前提: 第5章の計算量的困難さと第10章",
    ):
        assert chapter_contract in text


def test_concept_map_svg_has_accessible_name_description_and_three_edge_styles() -> None:
    root = ET.parse(SVG_MAP).getroot()
    namespace = {"svg": "http://www.w3.org/2000/svg"}
    title = root.find("svg:title", namespace)
    description = root.find("svg:desc", namespace)

    assert root.get("role") == "img"
    labelled_by = root.get("aria-labelledby", "").split()
    assert title is not None and title.get("id") in labelled_by
    assert description is not None and description.get("id") in labelled_by
    assert title.text and "12章" in title.text
    assert description.text and "テキスト版" in description.text

    svg_text = SVG_MAP.read_text(encoding="utf-8")
    for edge_class in ("required", "recommended", "related"):
        assert f'class="{edge_class}"' in svg_text
    for edge_label in ("必須前提（実線）", "強く推奨する前提（破線）", "応用・横断的関連（点線）"):
        assert edge_label in svg_text


def test_concept_map_entry_points_and_figure_guide_are_wired() -> None:
    introduction = _read("docs/introduction/index.md")
    purpose = _read("docs/introduction/purpose.md")
    guide = _read("docs/introduction/learning-guide.md")
    layout = _read("docs/_layouts/book.html")
    figure_guide = _read("docs/appendices/h.md")

    assert "'/appendices/i/'" in introduction
    assert introduction == _read("src/introduction/index.md")
    assert "'/appendices/i/'" in purpose
    assert "'/appendices/i/'" in guide
    assert purpose == _read("src/introduction/purpose.md")
    assert guide == _read("src/introduction/learning-guide.md")
    assert "'/appendices/i/'" in layout
    assert "付録I: 概念マップ" in layout
    assert "appendix_i_reading_dependency_map.svg" in figure_guide
    assert "'/appendices/i/#appendix-i-map'" in figure_guide
    assert "**概念図**" in figure_guide
    assert figure_guide == _read("src/appendices/h.md")

    for part in range(1, 5):
        docs = _read(f"docs/part-{part}/index.md")
        src = _read(f"src/part-{part}/index.md")
        assert docs == src
        assert f"../appendices/i/#appendix-i-part-{part}" in docs
