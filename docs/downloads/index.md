---
layout: book
title: "オフライン版（PDF/EPUB）"
---

# オフライン版（PDF/EPUB）

このページは、本書を Web 以外で読みたい読者向けに、**現在提供しているもの** と **まだ提供していないもの** を整理するための案内です。

## クイックナビ {#downloads-quick-nav}

- [現在の提供状況](#downloads-current)
- [読者向けの案内](#downloads-reader)
- [いま分かること / まだ未提供のこと](#downloads-status)
- [ローカルでの生成（開発者・コントリビューター向け）](#downloads-local-build)
- [将来的な配布先](#downloads-future)

## 現在の提供状況 {#downloads-current}

- **Web版**: 利用できます。最新版は公開サイトを正本としてください。
- **公式 PDF / EPUB**: 現時点では未提供です。
- **GitHub Releases / Tags 経由の配布**: 現時点では未運用です。

## 読者向けの案内 {#downloads-reader}

- まずは Web版を利用してください。内部リンク、検索、図表参照は Web版が最も安定しています。
- 長時間の移動や社内ネットワーク制約などでオフライン閲覧が必要な場合、現時点では一般読者向けのワンクリック配布はありません。
- 正式配布を開始した場合、このページに配布先と対象バージョンを掲載します。

## いま分かること / まだ未提供のこと {#downloads-status}

- **分かること**: 公開サイトで読める最新版、オフライン版の将来的な配布先、開発者向けの生成手順
- **未提供のこと**: 署名済み配布物、公式 PDF / EPUB の定期リリース、印刷向け完成版の別配布

## ローカルでの生成（開発者・コントリビューター向け） {#downloads-local-build}

以下は、環境構築済みの読者・開発者が手元で生成したい場合の手順です。一般読者向けの簡易配布手順ではありません。

前提:
- `pandoc`
- `rsvg-convert`（`librsvg2-bin` 由来。PDF生成時に図版SVGをPDFへ変換）

例:

```bash
# EPUB
python3 scripts/build_offline_book.py --target epub --out dist/book.epub.md
pandoc dist/book.epub.md -o dist/theoretical-computer-science-textbook.epub --toc --resource-path=docs

# PDF
python3 scripts/build_offline_book.py --target pdf --out dist/book.pdf.md --asset-out dist
pandoc dist/book.pdf.md -o dist/theoretical-computer-science-textbook.pdf --toc --resource-path=dist
```

## 将来的な配布先 {#downloads-future}

- GitHub Releases
  - `https://github.com/itdojp/theoretical-computer-science-textbook/releases`
