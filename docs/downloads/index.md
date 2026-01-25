---
layout: book
title: "オフライン版（PDF/EPUB）"
---

# オフライン版（PDF/EPUB）

本書は、GitHub Releases にて PDF/EPUB のオフライン版を配布します。

## 入手方法（推奨）

- GitHub Releases: `itdojp/theoretical-computer-science-textbook` の Releases から取得してください。
  - `https://github.com/itdojp/theoretical-computer-science-textbook/releases`
  - リポジトリが Private の場合、アクセス権限がないと閲覧できません。

## 生成物

- `theoretical-computer-science-textbook-<tag>.pdf`
- `theoretical-computer-science-textbook-<tag>.epub`

## ローカルでの生成（開発者向け）

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
