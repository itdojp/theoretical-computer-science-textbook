# コントリビューションガイド

この文書は contributor 向けです。読者として本書を利用したい場合は、まず公開サイトを参照してください。

- 公開サイト: https://itdojp.github.io/theoretical-computer-science-textbook/
- フィードバック窓口: https://itdojp.github.io/theoretical-computer-science-textbook/introduction/feedback/

## 受け付けるコントリビューション

- 誤字脱字、数式、記法、リンク切れの修正
- 技術的な誤りや説明不足の修正
- 学習導線、索引、図表、付録の改善
- アクセシビリティ、検索性、ナビゲーションの改善
- 実装課題、ビルド、CI、検証スクリプトの改善

## 事前に理解しておくべきこと

### build source と同期ミラー

- `docs/` が GitHub Pages / Jekyll の build source です。
- `src/` は同期ミラーです。本文を編集したら、対応する `src/` 側も同内容に保ってください。
- 図表は主に `docs/assets/images/diagrams/` にあります。
- 生成スクリプトは `scripts/` にあります。

### 読者向け導線との切り分け

- README は「読む人」と「直す人」の入口を分けています。
- contributor 向けの運用説明は README に過剰に増やさず、この文書へ集約してください。
- 公開版の promise や読者案内を変更する場合は、公開サイト側との整合も同時に確認してください。

## 推奨ワークフロー

1. 関連 Issue を確認し、必要なら先に論点を整理する
2. `main` から作業ブランチを切る
3. `docs/` を編集し、必要な `src/` ミラーを同期する
4. 影響範囲に応じて生成・検証コマンドを実行する
5. 変更概要と検証結果を添えて Pull Request を作成する

## 最低限の検証

本文や付録を更新した場合は、原則として次を実行してください。
`generate_search_data.py` / `generate_index.py` は生成系コマンド、`--check` 付きは生成漏れ検知用です。生成物が変わる変更では、まず生成し、その後に `--check` で差分が残っていないことを確認してください。
`notation_lint.py` は source Markdown の記法崩れを、`html_notation_check.py` は build 後 HTML の renderer 起因の崩れを検出する役割です。

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
npm run spellcheck
```

実装課題や Python 参照実装に影響する場合は、追加で以下も実行してください。

```bash
make test
```

## Pull Request の書き方

- 変更の目的と Issue 番号を明記する
- どのファイル群を更新したかを簡潔に示す
- 実行した検証コマンドを列挙する
- 読者向け変更と contributor 向け変更を同一 PR に混在させすぎない

## Stable ID（定義・定理・例）

本書では、定義・定理・系・例などを安定 ID で参照できるようにしています。

- 形式: kramdown の IAL で段落に ID を付与する
- 例: `**定理 9.3** ...` の直後に `{: #thm-9-3 }`
- 規約
  - 定義: `def-<章>-<番号>`
  - 定理: `thm-<章>-<番号>`
  - 系: `cor-<章>-<番号>`
  - 例: `ex-<章>-<番号>`

Stable ID 付きの項目は `docs/index.json` に機械可読インデックスとして集約しています。

- 生成: `python3 scripts/generate_index.py`
- 検証: `python3 scripts/generate_index.py --check`

## 記法上の注意

- 数式は原則 TeX（`\\(...\\)` / `\\[...\\]`）で記述してください。
- Unicode 数学記号や疑似 LaTeX は避けてください。ただし `docs/appendices/d.md` の記号索引は例外です。
- prime は ASCII `'` に依存せず、TeX の `^{\\prime}` / `\\prime` を使用してください。
- 回帰検出は `scripts/notation_lint.py` と `scripts/html_notation_check.py` で行います。

## ライセンス同意

コントリビューションを送ることで、以下に同意したものとみなします。

- コントリビューション内容が CC BY-NC-SA 4.0 で提供されること
- 株式会社アイティードゥが商用ライセンス契約において当該コントリビューション内容を利用できること

## お問い合わせ

- ITDO Inc.（株式会社アイティードゥ）
- Email: knowledge@itdo.jp
