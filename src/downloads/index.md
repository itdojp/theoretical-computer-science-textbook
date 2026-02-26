---
layout: book
title: "オフライン版（PDF/EPUB）"
---

# オフライン版（PDF/EPUB）

本書のオフライン版（PDF/EPUB）は、現時点では GitHub Releases では配布していません（GitHub Releases/Tags は未運用）。必要な場合は、下記の手順でローカル生成してください。

## 入手方法

- ローカル生成（開発者向け）: 下記「ローカルでの生成」を参照してください。
- 将来的な配布先: GitHub Releases（配布開始後に掲載）
  - `https://github.com/itdojp/theoretical-computer-science-textbook/releases`

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
