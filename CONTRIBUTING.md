# コントリビューションガイド

理論計算機科学教科書への貢献をありがとうございます！このガイドでは、プロジェクトへの貢献方法について説明します。

## 🚀 クイックスタート

### 1. 開発環境のセットアップ

#### 前提条件
- Git
- Ruby 3.0以上
- Node.js 18以上

#### ローカル環境での開発

```bash
# 1. リポジトリをフォーク・クローン
git clone https://github.com/YOUR_USERNAME/theoretical-computer-science-textbook.git
cd theoretical-computer-science-textbook

# 2. 依存関係をインストール
npm run install:deps

# 3. 開発サーバーを起動
npm run dev

# ブラウザで http://localhost:4000 を開く
```

#### Docker を使用した開発（推奨）

```bash
# Docker Compose で開発環境を起動
docker-compose up

# ブラウザで http://localhost:4000 を開く
```

### 2. 開発ワークフロー

```bash
# 新しい機能ブランチを作成
git checkout -b feature/your-feature-name

# 変更を実装
# ...

# テストを実行
npm test

# 変更をコミット
git add .
git commit -m "feat: 新機能の説明"

# ブランチをプッシュ
git push origin feature/your-feature-name

# GitHub で Pull Request を作成
```

## 📝 コントリビューションの種類

### 1. コンテンツの改善
- **誤字・脱字の修正**: 小さな修正でも歓迎
- **説明の改善**: より分かりやすい説明への書き換え
- **例題の追加**: 理解を助ける具体例
- **図表の改善**: Mermaid図の追加・修正

### 2. 技術的改善
- **レイアウトの改善**: CSS/HTML の改善
- **パフォーマンス向上**: サイトの高速化
- **アクセシビリティ**: 使いやすさの向上
- **SEO最適化**: 検索エンジン対応

### 3. 新機能の追加
- **インタラクティブ要素**: 練習問題、クイズ
- **ナビゲーション改善**: より使いやすいUI
- **検索機能**: コンテンツ検索の強化

## 📋 ガイドライン

### コミットメッセージ

[Conventional Commits](https://www.conventionalcommits.org/) 形式を使用してください：

```
type(scope): description

例:
feat(chapter-1): 新しい例題を追加
fix(navigation): ページナビゲーションのバグを修正
docs(readme): インストール手順を更新
style(css): レスポンシブデザインを改善
```

#### コミットタイプ
- `feat`: 新機能
- `fix`: バグ修正
- `docs`: ドキュメント
- `style`: スタイル変更
- `refactor`: リファクタリング
- `test`: テスト
- `chore`: その他

### コードスタイル

#### Markdown
- 見出しは `#` 記法を使用
- リストは `-` を使用
- 行長は120文字以内
- 日本語と英語の間にスペースを挿入

#### 数式
- MathJax記法を使用: `$inline$` や `$$display$$`
- 複雑な数式は改行して見やすく

#### 図表
- Mermaid記法を使用
- グラフ、フローチャート、状態遷移図など

### ファイル構成

```
docs/
├── src/
│   ├── chapter-X/
│   │   └── index.md          # 章のメインコンテンツ
│   ├── appendices/
│   │   └── X.md             # 付録コンテンツ
│   └── introduction/
│       └── *.md             # 導入部
├── _layouts/                # Jekyll レイアウト
├── _includes/               # 共通パーツ
└── assets/                  # CSS/JS/画像
```

## 🧪 テスト

### ローカルテスト

```bash
# Markdownの品質チェック
npm run lint

# スペルチェック
npm run spellcheck

# リンクチェック
npm run check-links

# ビルドテスト
npm run build
```

### 自動テスト

GitHub Actions が以下を自動実行します：
- Markdown linting
- スペルチェック
- リンクチェック
- ビルドテスト

## 📖 コンテンツガイド

### 章の構成

```markdown
---
title: "章タイトル"
layout: default
---

# 章タイトル

## 学習目標
- 目標1
- 目標2

## X.1 セクション1
### 定義
### 例題
### 練習問題

## X.2 セクション2
...

## まとめ

## 練習問題
1. 問題1
2. 問題2
```

### 数式の書き方

```markdown
インライン数式: $f(n) = O(n^2)$

ディスプレイ数式:
$$
\sum_{i=1}^{n} i = \frac{n(n+1)}{2}
$$
```

### 図表の書き方

```markdown
```mermaid
graph TD
    A[開始] --> B{条件}
    B -->|Yes| C[処理1]
    B -->|No| D[処理2]
    C --> E[終了]
    D --> E
```
```

## 🔍 レビュープロセス

### Pull Request の要件

1. **明確な説明**: 何を変更したか、なぜ変更したか
2. **テストの通過**: すべての自動テストがパス
3. **スクリーンショット**: UI変更の場合は before/after
4. **関連Issue**: 該当する場合はIssue番号を記載

### レビュー基準

- **正確性**: 内容が学術的に正確
- **明確性**: 読者にとって理解しやすい
- **一貫性**: 既存のスタイルと一致
- **完全性**: 必要な情報がすべて含まれている

## 🐛 バグ報告

### Issue テンプレート

```markdown
## バグの説明
明確で簡潔な説明

## 再現手順
1. ページXに移動
2. ボタンYをクリック
3. エラーが発生

## 期待される動作
何が起こるべきだったか

## 環境
- OS: [e.g. Windows 10]
- ブラウザ: [e.g. Chrome 91]
- デバイス: [e.g. Mobile, Desktop]

## スクリーンショット
該当する場合は添付
```

## 🌟 機能要望

新機能のアイデアがある場合：

1. 既存のIssueを確認
2. 新しいIssueを作成
3. 詳細な説明と使用例を提供
4. 実装方法があれば提案

## 📚 参考資料

- [Jekyll Documentation](https://jekyllrb.com/docs/)
- [GitHub Pages Documentation](https://docs.github.com/en/pages)
- [MathJax Documentation](https://docs.mathjax.org/)
- [Mermaid Documentation](https://mermaid-js.github.io/mermaid/)

## 💬 コミュニケーション

- **Issues**: バグ報告、機能要望
- **Discussions**: 質問、アイデア、フィードバック
- **Pull Requests**: コードレビュー、議論

## 🙏 謝辞

すべてのコントリビューターに感謝します！あなたの貢献が教育リソースの向上に役立っています。

---

質問がある場合は、お気軽にIssueを作成するか、Discussionsで質問してください。