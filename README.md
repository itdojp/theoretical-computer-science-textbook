# 理論計算機科学教科書

[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-deployed-green)](https://itdojp.github.io/theoretical-computer-science-textbook/)
[![License: CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg)](https://github.com/itdojp/it-engineer-knowledge-architecture/blob/main/LICENSE.md)
[![Jekyll](https://img.shields.io/badge/Jekyll-4.3-red)](https://jekyllrb.com/)

数学的基礎から始まり、計算理論、アルゴリズム、複雑性理論、そして最新の研究トピックまでを包括的にカバーする理論計算機科学の教科書。大学生、大学院生、研究者向けの体系的学習リソース。

## 📚 教科書内容

### Part I: 数学的基礎（第1〜3章）
- **第1章**: 数学的基礎 - 集合論、論理学、証明技法
- **第2章**: 計算理論の基礎 - チューリング機械、計算可能性
- **第3章**: 形式言語とオートマトン理論 - 正規言語から文脈自由言語

### Part II: 計算理論（第4〜6章）
- **第4章**: 計算可能性 - 決定可能性、停止問題、Riceの定理
- **第5章**: 計算複雑性理論 - P vs NP、NP完全性、複雑性クラス
- **第6章**: アルゴリズムの数学的解析 - 設計手法、計算量解析

### Part III: 高度なトピック（第7〜9章）
- **第7章**: データ構造の理論 - 効率的なデータ操作の基盤
- **第8章**: グラフ理論とネットワーク - グラフアルゴリズムと応用
- **第9章**: 論理学・形式的手法 - プログラム検証と形式仕様

### Part IV: 応用理論（第10〜12章）
- **第10章**: 情報理論 - 情報の定量化と符号化
- **第11章**: 暗号理論の数学的基礎 - 現代暗号の理論的基盤
- **第12章**: 並行計算の理論 - 並列・分散システムの理論

### 付録
- **付録A**: 数学記法ガイド - 統一された数学記法
- **付録B**: アルゴリズム実装例 - Python実装と複雑性解析
- **付録C**: 練習問題解答 - 全章の詳細解答
- **付録D**: 用語集・索引 - 3,500+専門用語の日英対訳
- **付録E**: 実世界への応用例 - 理論の実用的応用事例
- **付録F**: 学習進捗チェックリスト - 自己評価ツール

## 🌐 オンライン版

**📖 [理論計算機科学教科書を読む](https://itdojp.github.io/theoretical-computer-science-textbook/)**

## ✨ 特徴

- **📱 レスポンシブデザイン**: モバイル・タブレット・デスクトップ対応
- **🧮 数式サポート**: MathJax 3.0による美しい数式表示
- **📊 図表サポート**: Mermaidによるインタラクティブな図表
- **🗂️ 階層ナビゲーション**: 章・付録間のシームレスな移動
- **🔍 検索機能**: コンテンツ全体の検索対応
- **📑 進捗管理**: 学習チェックリストによる進捗追跡

## 🎯 対象読者

- **大学生**: 理論計算機科学の基礎を学びたい学生
- **大学院生**: より深い理論的知識を求める研究者
- **研究者**: 最新の理論トピックを確認したい専門家
- **エンジニア**: 理論的背景を理解したい実務者

## 📖 学習ガイド

### 推奨学習パス

1. **初学者向け** (6〜8ヶ月): 第1〜3章、6-8章
2. **標準コース** (12〜15ヶ月): 第1〜10章
3. **完全マスター** (18〜24ヶ月): 全12章+付録
4. **研究者向け** (集中学習): 第4〜5章、9章、11-12章

### 前提知識
- 数学（微分積分、線形代数、離散数学）
- プログラミング基礎
- データ構造とアルゴリズムの基本知識

## 🛠️ 開発・コントリビューション

このプロジェクトは [Book Publishing Template v3.0](https://github.com/itdojp/book-formatter) を使用しています。

### ローカル開発環境のセットアップ

#### 前提条件
- Git
- Ruby 3.0以上
- Node.js 18以上

#### クイックスタート

```bash
# リポジトリをクローン
git clone https://github.com/itdojp/theoretical-computer-science-textbook.git
cd theoretical-computer-science-textbook

# 依存関係をインストール
bundle install
npm install

# ローカルサーバーを起動
bundle exec jekyll serve --source docs
# または
npm run dev

# ブラウザで http://localhost:4000 を開く
```

#### NPM スクリプト

```bash
npm run dev          # 開発サーバー起動
npm run build        # 本番ビルド
npm run test         # テスト実行
npm run lint         # Markdown linting
npm run spellcheck   # スペルチェック
```

### ファイル構成

```
docs/
├── _config.yml              # Jekyll設定
├── _layouts/                # レイアウトテンプレート
├── _includes/               # 共通パーツ
├── assets/                  # CSS/JS/画像
├── src/
│   ├── introduction/        # 導入部
│   ├── chapter-1/          # 第1章
│   ├── ...                 # 第2〜12章
│   └── appendices/         # 付録
├── index.md                # メインページ
└── package.json            # NPM設定

scripts/                    # ビルドスクリプト
templates/                  # テンプレートファイル
tests/                     # テストファイル
```

### コンテンツの編集

1. **章の追加・編集**: `docs/src/chapter-X/index.md`
2. **付録の編集**: `docs/src/appendices/X.md`
3. **図表の作成・編集**: `docs/assets/images/diagrams/`
   - SVG図表推奨（学術品質のベクター形式）
   - 詳細は [SVG作成ガイド](SVG_CREATION_GUIDE.md) を参照
4. **ナビゲーション更新**: `docs/_includes/sidebar.html`
5. **スタイル変更**: `docs/_layouts/default.html`

### GitHub Pages 自動デプロイ

コミットを `main` ブランチにプッシュすると、GitHub Actions が自動的にサイトをビルド・デプロイします。

## 🔧 技術仕様

- **静的サイトジェネレーター**: Jekyll 4.3
- **CSS フレームワーク**: カスタムCSS（Bootstrap非依存）
- **数式レンダリング**: MathJax 3.0
- **図表生成**: Mermaid 10
- **デプロイ**: GitHub Pages
- **CI/CD**: GitHub Actions

## ✍️ 本書の流儀（スタイルガイド要点）

- **対数の底**: 明記がない限り、対数は底2（log₂）を用います。容量やエントロピー、相互情報量などの単位を [bits] に統一するためです。底が異なる場合は本文中で明記します（例: logₑ, log₁₀）。

- **内部リンク方針**: Pretty URL を基本とし、拡張子（.md/.html）は記述しません。末尾スラッシュを付与したパス、または相対パスで統一します。
  - 例: `../chapter-5/`、`/src/appendices/`
  - 章や付録間の参照は、原則としてビルド後の相対リンクで一貫。

- **実務メモの位置付け**: 各章に「【実務メモ】」として、理論の応用上の注意や落とし穴（例: ハッシュの負荷率、再ハッシュ、メモリモデルの可視性/再順序、暗号モードの安全運用、Dijkstraの非負辺前提など）を短く併記しています。これは学習者が実装・運用でつまずきやすいポイントを事前に示すための補助的記述であり、理論の定理・証明の厳密性を損なわない範囲で記載しています。
  - 実務メモは章テキストの補助的要素であり、本筋の定義・定理・証明とは区別されます。
  - 追加・改訂の提案は Issue / PR にて歓迎します。

## 📄 ライセンス

本書は ITDO Inc. の統一ライセンスに従います。

- ライセンス本文: https://github.com/itdojp/it-engineer-knowledge-architecture/blob/main/LICENSE.md
- クリエイティブ・コモンズ: CC BY-NC-SA 4.0（非営利・継承・表示）

商用利用をご希望の場合は、商用ライセンス契約が必要です（詳細は上記ライセンスを参照）。

## 👥 著者・コントリビューター

- **著者**: ITDO Inc. (株式会社アイティードゥ)
- **Email**: knowledge@itdo.jp
- **GitHub**: [@itdojp](https://github.com/itdojp)

## 🤝 コントリビューション

コントリビューションを歓迎します！以下の方法で参加できます：

1. **Issues**: バグ報告、機能要望、質問
2. **Pull Requests**: コンテンツの改善、誤字修正、新機能
3. **Discussions**: 学習方法、理論的議論、フィードバック

### コントリビューションガイドライン

1. フォークしてブランチを作成
2. 変更をコミット
3. テストを実行して確認
4. Pull Request を作成

## 📈 更新履歴

- **v1.0.0** (2025-07): 初版リリース - 全12章+付録完成
- **v0.9.0** (2025-07): Book Publishing Template v3.0 移行
- **v0.8.0** (2025-07): GitHub Pages対応

## 🔗 関連リンク

- [Book Publishing Template](https://github.com/itdojp/book-formatter)
- [SVG図表作成ガイド](SVG_CREATION_GUIDE.md) - 学術品質の図表作成手法
- [ITDO Inc. 公式サイト](https://itdo.jp)
- [理論計算機科学参考文献](docs/src/appendices/reading-list.md)

---

**🎓 学習者の皆様へ**: この教科書が皆様の理論計算機科学の学習に役立つことを願っています。質問やフィードバックは Issues でお気軽にお寄せください。

**📚 読書開始**: [理論計算機科学教科書を読み始める →](https://itdojp.github.io/theoretical-computer-science-textbook/)
