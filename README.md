# 理論計算機科学教科書

[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-deployed-green)](https://itdojp.github.io/theoretical-computer-science-textbook/)
[![License: CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg)](https://github.com/itdojp/it-engineer-knowledge-architecture/blob/main/LICENSE.md)
[![Jekyll](https://img.shields.io/badge/Jekyll-3.10-red)](https://jekyllrb.com/)

離散数学と基本的なプログラミング経験を持つ学部上級生・大学院初年度・ソフトウェアエンジニアに向けて、集合・論理から計算可能性・複雑性・情報理論・暗号・並行計算までを日本語で体系的に学べる理論計算機科学の教科書です。

## 読者向け導線

- 公開サイト（正本）: https://itdojp.github.io/theoretical-computer-science-textbook/
- 本書の目的と構成: https://itdojp.github.io/theoretical-computer-science-textbook/introduction/purpose/
- 学習の進め方: https://itdojp.github.io/theoretical-computer-science-textbook/introduction/learning-guide/
- オフライン版の提供状況: https://itdojp.github.io/theoretical-computer-science-textbook/downloads/
- フィードバック窓口: https://itdojp.github.io/theoretical-computer-science-textbook/introduction/feedback/

## この本の約束

- 集合・論理・形式言語・計算可能性・複雑性・情報理論・暗号・並行計算のつながりを、一冊の流れで俯瞰できるようにする
- 定義・定理・証明を読むための基礎体力を付け、理論の前提・結論・限界を追えるようにする
- 実務メモ・演習・付録を通じて、理論が実装や設計判断にどう接続するかを見失わないようにする

## 想定読者

- 情報系学部3〜4年生、または大学院初年度で、離散数学と基本的なプログラミング経験がある読者
- 計算可能性・複雑性・形式言語・情報理論を体系で学び直したいソフトウェアエンジニア

## 非対象読者

- 集合・論理・関数・証明技法の基礎がまだなく、補強しながら読む準備がない読者
- 競技プログラミングの即効テクニックや面接対策だけを短時間で得たい読者
- 暗号理論や並行計算だけを専門書レベルで深掘りしたい読者

## 読み方の入口

- **通読コース**: `はじめに → 前提知識 → 第1章〜第12章 → 付録C`
- **講義補助コース**: `第1章〜第3章 → 講義対象章 → 付録A/C`
- **実務者の拾い読み**: `前提知識 → 第6章・第7章・第8章 → 必要に応じて第4章・第5章・第10章〜第12章`
- **再学習コース**: `本書の目的と構成 → 前提知識の自己診断 → 苦手章の再読 → 付録C/F`

詳細は公開サイトの「学習の進め方」を参照してください。

## 収録範囲

### Part I: 数学的基礎（第1〜3章）

- 第1章: 数学的基礎
- 第2章: 計算理論の基礎
- 第3章: 形式言語とオートマトン理論

### Part II: 計算理論（第4〜6章）

- 第4章: 計算可能性
- 第5章: 計算複雑性理論
- 第6章: アルゴリズムの数学的解析

### Part III: 高度なトピック（第7〜9章）

- 第7章: データ構造の理論
- 第8章: グラフ理論とネットワーク
- 第9章: 論理学と形式的手法

### Part IV: 応用理論（第10〜12章）

- 第10章: 情報理論
- 第11章: 暗号理論の数学的基礎
- 第12章: 並行計算の理論

### 付録

- 数学記法ガイド
- アルゴリズム実装例
- 練習問題解答
- 用語集・索引
- 実世界への応用例
- 学習進捗チェックリスト

## 配布ポリシー

- **Web版** を正本とします。
- **公式 PDF / EPUB** は現時点では未提供です。
- **GitHub Releases / Tags 経由の配布** は現時点では未運用です。
- 将来の配布形態は公開サイトのダウンロード案内で更新します。

## このリポジトリについて

- `docs/` が GitHub Pages / Jekyll の build source です。
- `src/` は同期ミラーです。本文修正時は対応箇所を同内容に保ちます。
- `scripts/` に検索データ生成、索引生成、回帰チェック、オフライン版生成補助を置いています。
- 公開中の更新履歴は README 内ではなく、公開サイトの changelog を正本とします。https://itdojp.github.io/theoretical-computer-science-textbook/changelog/

## コントリビュートする方へ

詳細は `CONTRIBUTING.md` を参照してください。ここでは最低限の入口だけ示します。

### 前提条件

- Git
- Ruby 3.2 以上
- Node.js 20 以上
- Python 3.11 以上

### クイックスタート

```bash
git clone https://github.com/itdojp/theoretical-computer-science-textbook.git
cd theoretical-computer-science-textbook
bundle install
npm install
npm run dev
```

### 変更時の基本ルール

1. 本文は `docs/` を編集し、対応する `src/` ミラーも同期する
2. 生成物や索引に影響する変更では関連スクリプトを実行する
3. PR には変更範囲と実行した検証コマンドを明記する
4. 読者向け案内と contributor 向け案内を混在させない

### 代表的な検証コマンド

生成物を持つ変更では、まず生成コマンドを実行し、その後に `--check` で差分が残っていないことを確認してください。
`notation_lint.py` は source Markdown 側の記法崩れを、`html_notation_check.py` は Jekyll build 後の HTML における renderer 起因の崩れを検出します。

```bash
# 生成が必要なもの
python3 scripts/generate_search_data.py
python3 scripts/generate_index.py

# 生成漏れチェック
python3 scripts/generate_search_data.py --check
python3 scripts/generate_index.py --check

# 本文・ビルド検証
python3 scripts/docs_regression_lint.py
python3 scripts/notation_lint.py
bundle exec jekyll build --source docs --config docs/_config.yml --destination _site
python3 scripts/html_notation_check.py --site-root _site
make test
npm run spellcheck
```

## 技術構成

- 静的サイト生成: Jekyll 3.10.x
- 数式表示: MathJax 3
- 図表: Mermaid 10
- 配信: GitHub Pages
- CI: GitHub Actions

## ライセンス

本書は ITDO Inc. の統一ライセンスに従います。

- ライセンス本文: https://github.com/itdojp/it-engineer-knowledge-architecture/blob/main/LICENSE.md
- クリエイティブ・コモンズ: CC BY-NC-SA 4.0

商用利用は別途ライセンス契約が必要です。

## 連絡先

- 著者: ITDO Inc.（株式会社アイティードゥ）
- Email: knowledge@itdo.jp
- GitHub: https://github.com/itdojp
