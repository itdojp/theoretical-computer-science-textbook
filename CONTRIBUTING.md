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
- 付録H（図版ガイド）は `python3 scripts/generate_figure_guide.py` の生成物です。

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
npm run check:exercises
npm run check:theorems

# 本文・ビルド検証
python3 scripts/docs_regression_lint.py
python3 scripts/notation_lint.py
bundle exec jekyll build --source docs --config docs/_config.yml --destination _site
npm run check:exercises:html
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

## Stable ID（章末問題・付録C解答）

章末問題は、表示番号や区分を変更しても外部参照が壊れない安定 ID を持ちます。

- 問題 ID: `exq-ch<章番号>-<3桁通番>`（例: `exq-ch7-003`）
- 解答 ID: `ex-sol-ch<章番号>-<3桁通番>`（例: `ex-sol-ch7-003`）
- 問題の通番は一度割り当てた後は再利用・振り直しをしない
- 表示番号は章全体で `1..N` とし、区分間で重複させない
- 通常の番号付きリストでは、問題文の先頭に inline span を置く（例: `3. <span id="exq-ch7-003"></span>問題文`）。リスト末尾の IAL は、問題文の段落構造によって kramdown が ID を生成しない場合があるため使用しない
- `####` 見出しを使う実装問題では、見出し直前に `<span id="exq-ch7-013"></span>` を置く。既存の見出し URL が変わる場合は旧アンカーも alias span として残す

付録Cの各解答には安定 ID の span、`**元問題**:` の直接リンク、必要に応じた `**元問題の項目**:`、および `**解答種別**:` を記載します。解答種別は `詳細解答`、`調査ガイド`、`参照実装` のいずれかです。元問題側にも同じ解答種別をラベルにした付録Cへのリンクを置いてください。同一問題の複数項目へ解答する場合は、`元問題の項目` を重複しない値にします。

索引と検索データを再生成した後、source と build 後 HTML を検査します。

```bash
python3 scripts/generate_index.py
python3 scripts/generate_search_data.py
npm run check:exercises
bundle exec jekyll build --source docs --config docs/_config.yml --destination _site
npm run check:exercises:html
```

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
