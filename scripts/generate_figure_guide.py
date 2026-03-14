#!/usr/bin/env python3
"""Generate a public figure guide appendix.

The project already contains many SVG diagrams, but the public book currently
has no dedicated "figure guide / list of figures" page. This script extracts
diagram references from chapter Markdown files and generates Appendix H in both
`docs/` and the synced `src/` mirror.
"""

from __future__ import annotations

import argparse
import json
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path


HEADING_RE = re.compile(r"^(?P<marks>#{1,6})\s+(?P<text>.+?)\s*$")
LIQUID_RELATIVE_URL_RE = re.compile(
    r"""\{\{\s*['"](?P<path>[^'"]+)['"]\s*\|\s*relative_url\s*\}\}"""
)
MD_IMAGE_RE = re.compile(r"!\[(?P<alt>[^\]]*)\]\((?P<url>.+?)\)")
CHAPTER_PATH_RE = re.compile(r"chapter-(?P<num>\d+)/index\.md$")
ROLE_LINE_RE = re.compile(
    r"^(?P<role>直観図|例示図|比較図|概念図|構成図|模式図|補助図)\s*[：:]\s*(?P<label>.+?)\s*$"
)


@dataclass(frozen=True)
class FigureEntry:
    chapter_num: int
    chapter_title: str
    part_title: str
    section_title: str
    role: str
    lead_text: str | None
    alt_text: str
    asset_path: str


PURPOSE_SHORTLIST_LIMIT = 4
PURPOSE_ORDER = [
    "直観図",
    "例示図",
    "比較図",
    "手順/構成図",
]


def entry_text(entry: FigureEntry) -> str:
    return " ".join(
        part for part in [entry.role, entry.lead_text or "", entry.alt_text, entry.section_title] if part
    )


def matches_purpose(entry: FigureEntry, purpose: str) -> bool:
    text = entry_text(entry)

    if purpose == "直観図":
        return entry.role == "直観図" or "直観" in text

    if purpose == "例示図":
        return entry.role == "例示図" or any(keyword in text for keyword in ["実行例", "逐次", "例", "トレース"])

    if purpose == "比較図":
        return entry.role == "比較図" or any(
            keyword in text for keyword in ["比較", "対比", "包含関係", "階層", "種類", "違い"]
        )

    if purpose == "手順/構成図":
        return entry.role in {"構成図", "模式図"} or any(
            keyword in text for keyword in ["構成", "フロー", "流れ", "仕組み", "操作", "アルゴリズム", "受理方式"]
        )

    return False


def build_purpose_shortlists(entries: list[FigureEntry]) -> dict[str, list[FigureEntry]]:
    shortlists = {purpose: [] for purpose in PURPOSE_ORDER}

    for entry in entries:
        matched_purpose = next((purpose for purpose in PURPOSE_ORDER if matches_purpose(entry, purpose)), None)
        if matched_purpose is None:
            continue
        if len(shortlists[matched_purpose]) >= PURPOSE_SHORTLIST_LIMIT:
            continue
        shortlists[matched_purpose].append(entry)

    return shortlists


def load_book_config(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_front_matter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}

    out: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if not line.strip() or line.lstrip().startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        out[key.strip()] = value.strip().strip('"').strip("'")
    return out


def resolve_url(raw_url: str) -> str:
    raw_url = raw_url.strip()
    match = LIQUID_RELATIVE_URL_RE.fullmatch(raw_url)
    if match:
        return match.group("path").lstrip("/")
    return raw_url


def build_part_map(book_cfg: dict) -> dict[int, str]:
    part_map: dict[int, str] = {}
    structure = book_cfg.get("structure", {})
    for part in structure.get("parts", []):
        part_title = str(part.get("title", "")).strip()
        for chapter_id in part.get("chapters", []):
            try:
                part_map[int(str(chapter_id).strip())] = part_title
            except ValueError:
                continue
    return part_map


def slugify_heading(text: str) -> str:
    normalized = unicodedata.normalize("NFKC", text).lower()
    out: list[str] = []

    for char in normalized:
        if (
            char.isalnum()
            or ("ぁ" <= char <= "ゖ")
            or ("ァ" <= char <= "ヺ")
            or ("一" <= char <= "龥")
            or char in {"-", "_"}
        ):
            out.append(char)
        elif char.isspace():
            out.append("-")

    slug = "".join(out)
    return re.sub(r"-+", "-", slug).strip("-")


def format_quoted_text(text: str) -> str:
    return f"「{text.strip()}」"


def infer_role(lines: list[str], image_line_index: int) -> tuple[str, str | None]:
    for idx in range(image_line_index - 1, -1, -1):
        stripped = lines[idx].strip()
        if not stripped:
            continue
        if stripped.startswith("![") or stripped.startswith("{:"):
            continue
        if HEADING_RE.match(stripped):
            return "図版", None
        role_match = ROLE_LINE_RE.match(stripped)
        if role_match:
            return role_match.group("role"), role_match.group("label").strip()
        return "図版", None
    return "図版", None


def collect_figures(docs_root: Path, book_cfg: dict) -> list[FigureEntry]:
    part_map = build_part_map(book_cfg)
    entries: list[FigureEntry] = []

    chapter_files: list[tuple[int, Path]] = []
    for md_path in docs_root.glob("chapter-*/index.md"):
        chapter_match = CHAPTER_PATH_RE.search(md_path.as_posix())
        if not chapter_match:
            continue
        chapter_files.append((int(chapter_match.group("num")), md_path))

    for chapter_num, md_path in sorted(chapter_files, key=lambda item: item[0]):

        raw = md_path.read_text(encoding="utf-8")
        front_matter = parse_front_matter(raw)
        chapter_title = front_matter.get("title", f"第{chapter_num}章").strip()
        part_title = part_map.get(chapter_num, "その他")

        lines = raw.splitlines()
        current_headings: dict[int, str] = {}

        for line_index, line in enumerate(lines):
            heading_match = HEADING_RE.match(line.strip())
            if heading_match:
                level = len(heading_match.group("marks"))
                current_headings[level] = heading_match.group("text").strip()
                for deeper in range(level + 1, 7):
                    current_headings.pop(deeper, None)
                continue

            image_match = MD_IMAGE_RE.search(line)
            if not image_match:
                continue

            asset_path = resolve_url(image_match.group("url"))
            if not asset_path.startswith("assets/images/diagrams/"):
                continue

            section_title = chapter_title
            for level in range(6, 1, -1):
                if level in current_headings:
                    section_title = current_headings[level]
                    break

            role, lead_text = infer_role(lines, line_index)
            alt_text = image_match.group("alt").strip() or Path(asset_path).stem

            entries.append(
                FigureEntry(
                    chapter_num=chapter_num,
                    chapter_title=chapter_title,
                    part_title=part_title,
                    section_title=section_title,
                    role=role,
                    lead_text=lead_text,
                    alt_text=alt_text,
                    asset_path=asset_path,
                )
            )

    return entries


def render_markdown(entries: list[FigureEntry]) -> str:
    total_figures = len(entries)
    purpose_shortlists = build_purpose_shortlists(entries)
    part_order: list[str] = []
    part_counts: dict[str, int] = {}
    chapter_order: list[int] = []
    chapter_counts: dict[int, int] = {}
    chapter_titles: dict[int, str] = {}
    figures_by_chapter: dict[int, list[FigureEntry]] = {}

    for entry in entries:
        if entry.part_title not in part_counts:
            part_order.append(entry.part_title)
            part_counts[entry.part_title] = 0
        part_counts[entry.part_title] += 1

        if entry.chapter_num not in chapter_counts:
            chapter_order.append(entry.chapter_num)
            chapter_counts[entry.chapter_num] = 0
            chapter_titles[entry.chapter_num] = entry.chapter_title
            figures_by_chapter[entry.chapter_num] = []
        chapter_counts[entry.chapter_num] += 1
        figures_by_chapter[entry.chapter_num].append(entry)

    out: list[str] = [
        "---",
        'title: "付録H: 図版ガイドと図一覧"',
        "layout: book",
        "---",
        "",
        "# 付録H: 図版ガイドと図一覧",
        "",
        "この付録は、本書の図版を**見返す入口**として使うための読者向けガイドです。",
        "本文の途中で見た図を後から探し直したいとき、章をまたいで似た図を比較したいとき、図の役割を確認したいときに参照してください。",
        "",
        "## この付録の使い方",
        "",
        "- **最初に読む場所ではありません**。本文を読んでいて図に助けられた箇所を、後から戻るための一覧です。",
        "- **本文の節リンク** と **SVG 直接リンク** を併記しています。前者は文脈確認用、後者は図だけを拡大して見たいときに使ってください。",
        "- **章内の位置** は「節」で示しています。厳密な図番号ではなく、読者が再訪しやすい再参照導線を優先しています。",
        "",
        "## 図ラベルの読み方",
        "",
        "- **直観図**: 定義や証明を置き換えるものではなく、何が本質かを先に掴むための図です。",
        "- **例示図**: アルゴリズムの逐次実行、状態変化、構成の具体例を追うための図です。",
        "- **比較図**: 複数の手法・クラス・見方の差分を見比べるための図です。",
        "- **構成図 / 模式図**: 装置の構成や処理フローを順に追うための図です。",
        "- **図版**: 本文に明示ラベルがない図です。節名と alt テキストで文脈を補っています。",
        "",
        "## 目的別ショートリスト",
        "",
        "図で詰まったときは、まず次の目的別ショートリストから近いものを開いてください。",
        "",
    ]

    for purpose in PURPOSE_ORDER:
        shortlist = purpose_shortlists[purpose]
        if not shortlist:
            continue

        out.extend([f"### {purpose}を見たいとき", ""])
        for entry in shortlist:
            section_anchor = slugify_heading(entry.section_title)
            chapter_link = "{{ '" + f"/chapter-{entry.chapter_num}/#{section_anchor}" + "' | relative_url }}"
            svg_link = "{{ '" + f"/{entry.asset_path}" + "' | relative_url }}"
            out.append(
                f"- [{entry.alt_text}]({chapter_link}) — {entry.chapter_title} / 節: {format_quoted_text(entry.section_title)} / [SVG]({svg_link})"
            )
        out.append("")

    out.extend(
        [
        "## 図版サマリー",
        "",
        f"- 総図版数: {total_figures}",
        ]
    )

    for part_title in part_order:
        out.append(f"- {part_title}: {part_counts[part_title]} 図")

    out.extend(["", "## 図一覧", ""])

    current_part = None
    for chapter_num in chapter_order:
        chapter_entries = figures_by_chapter[chapter_num]
        chapter_part = chapter_entries[0].part_title
        if chapter_part != current_part:
            out.extend([f"### {chapter_part}", ""])
            current_part = chapter_part

        chapter_title = chapter_titles[chapter_num]
        out.append(f"#### {chapter_title}（{chapter_counts[chapter_num]} 図）")
        for entry in chapter_entries:
            section_anchor = slugify_heading(entry.section_title)
            chapter_link = "{{ '" + f"/chapter-{entry.chapter_num}/#{section_anchor}" + "' | relative_url }}"
            svg_link = "{{ '" + f"/{entry.asset_path}" + "' | relative_url }}"
            bullet = (
                f"- **{entry.role}**: [{entry.alt_text}]({chapter_link})"
                f" — 節: {format_quoted_text(entry.section_title)} / [SVG]({svg_link})"
            )
            if entry.lead_text:
                bullet += f" / 本文ラベル: {format_quoted_text(entry.lead_text)}"
            out.append(bullet)
        out.append("")

    out.extend(
        [
            "## 補足",
            "",
            "- 図版の追加・差し替えに合わせてこの付録を更新する場合は、`python3 scripts/generate_figure_guide.py` を実行してください。",
            "- 本文側の図ラベルを増やす場合でも、ここでは読者が探し直しやすい最小限の情報を優先してください。",
            "",
        ]
    )

    return "\n".join(out)


def write_outputs(rendered: str, docs_out: Path, src_out: Path) -> None:
    docs_out.parent.mkdir(parents=True, exist_ok=True)
    src_out.parent.mkdir(parents=True, exist_ok=True)
    docs_out.write_text(rendered, encoding="utf-8")
    src_out.write_text(rendered, encoding="utf-8")


def check_outputs(rendered: str, docs_out: Path, src_out: Path) -> int:
    for path in (docs_out, src_out):
        if not path.exists():
            print(f"missing: {path}")
            return 1
        if path.read_text(encoding="utf-8") != rendered:
            print(f"out-of-date: {path}")
            return 1
    print("ok")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--docs-root", default="docs", help="Jekyll source directory (default: docs)")
    ap.add_argument(
        "--config",
        default="docs/book-config.json",
        help="Book structure config (default: docs/book-config.json)",
    )
    ap.add_argument(
        "--docs-out",
        default="docs/appendices/h.md",
        help="Generated docs appendix path (default: docs/appendices/h.md)",
    )
    ap.add_argument(
        "--src-out",
        default="src/appendices/h.md",
        help="Generated src mirror path (default: src/appendices/h.md)",
    )
    ap.add_argument("--check", action="store_true", help="Fail if generated outputs are not up-to-date")
    args = ap.parse_args()

    docs_root = Path(args.docs_root)
    book_cfg = load_book_config(Path(args.config))
    entries = collect_figures(docs_root, book_cfg)
    rendered = render_markdown(entries)

    docs_out = Path(args.docs_out)
    src_out = Path(args.src_out)

    if args.check:
        return check_outputs(rendered, docs_out, src_out)

    write_outputs(rendered, docs_out, src_out)
    print(f"wrote: {docs_out}")
    print(f"wrote: {src_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
