---
layout: book
title: "オフライン版（PDF/EPUB）"
---

# オフライン版（PDF/EPUB）

本書はWeb版を内容の正本とし、固定版をオフラインで読むためのPDF/EPUBをGitHub Releasesで提供します。`v1.2.0`はRelease準備中であり、完了まではWeb版を利用してください。

## クイックナビ {#downloads-quick-nav}

- [現在の提供状況](#downloads-current)
- [読者向けの案内](#downloads-reader)
- [版と成果物の関係](#downloads-status)
- [ローカルでの生成（開発者・コントリビューター向け）](#downloads-local-build)
- [Release運用](#downloads-future)

## 現在の提供状況 {#downloads-current}

- **Web版**: 利用できます。訂正を含む最新版は公開サイトを正本としてください。
- **公式 PDF / EPUB**: `v1.2.0` tagのRelease完了後に提供します。
- **配布先**: [GitHub Releases](https://github.com/itdojp/theoretical-computer-science-textbook/releases)
- **配布予定tag**: `v1.2.0`

## 読者向けの案内 {#downloads-reader}

- 継続的に更新される本文、内部リンク、検索、図表参照にはWeb版を利用してください。
- ReleaseのPDF/EPUBは、版番号とtagが固定されたオフライン閲覧用スナップショットです。
- 同じ版番号のPDFとEPUBは、同じcanonical metadataと本文から自動生成します。
- Release後に入った訂正は次の版へ反映します。現在の差分は[更新履歴](../changelog/)で確認してください。

## 版と成果物の関係 {#downloads-status}

| 項目 | v1.2.0 |
| --- | --- |
| Release tag | `v1.2.0` |
| 公開日 | 2026-07-16 |
| 公式成果物 | PDF / EPUB（Release準備中） |
| 内容の正本 | Web版 |
| 署名 | 未提供 |

成果物のファイル名にはtagを含めます。Release pageでtagとファイル名が一致することを確認して利用してください。

## ローカルでの生成（開発者・コントリビューター向け） {#downloads-local-build}

以下は、環境構築済みの開発者が手元で同じ入力から生成するための手順です。

前提:

- `pandoc`
- `rsvg-convert`（`librsvg2-bin` 由来。PDF生成時に図版SVGをPDFへ変換）
- PDF生成時はXeLaTeXとNoto CJKフォント

例:

```bash
# EPUB
python3 scripts/build_offline_book.py --target epub --out dist/book.epub.md
pandoc dist/book.epub.md -o dist/theoretical-computer-science-textbook.epub --toc --resource-path=docs

# PDF
python3 scripts/build_offline_book.py --target pdf --out dist/book.pdf.md --asset-out dist
pandoc dist/book.pdf.md -o dist/theoretical-computer-science-textbook.pdf --toc --resource-path=dist --pdf-engine=xelatex
```

公式成果物は `.github/workflows/release-artifacts.yml` がtag push時に生成します。ローカル生成物は公式Release assetではありません。

## Release運用 {#downloads-future}

- 版番号 `X.Y.Z` に対応するtagは `vX.Y.Z` とします。
- tagの版とcanonical metadataの版が一致しない場合、Release workflowを失敗させます。
- PDF/EPUBは同じtagのGitHub Releaseへ添付します。
- Web版はmainから継続公開し、Release artifactより新しい訂正を含む場合があります。
