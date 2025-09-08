# Issue トリアージ方針（運用メモ）

このリポジトリのIssuesを効率よく管理するための手順です。

## 優先度ラベル

- `priority: high` — ビルド/閲覧不能、内容の誤り（学習者影響大）、セキュリティ
- `priority: medium` — 品質改善（図/文面/ナビゲーション）
- `priority: low` — 細かなリファクタ、提案、将来要望

補助ラベル: `bug`, `a11y`, `docs`, `content`, `diagram`, `dependencies`

## クローズポリシー

- 120日以上アクティビティ無しのIssueは自動で `stale`（ワークフローで運用）
- 14日間無反応なら自動クローズ（例外: `priority: high`, `security`, `bug`, `pinned`, `dependencies`）
- 再現手順や情報不足のものは `needs-more-info` を付けてコメント→2週間でクローズ候補

## トリアージ手順（定例）

1) オープンIssuesを確認（最新100件）

```bash
gh issue list -R itdojp/theoretical-computer-science-textbook --state open --limit 100 --sort updated
```

2) 重要度順に並べ替え・ラベル付与

```bash
# 例: 明確な内容誤り
gh issue edit <num> -R itdojp/theoretical-computer-science-textbook --add-label "bug,priority: high,content"

# 例: 図の改善要望
gh issue edit <num> -R itdojp/theoretical-computer-science-textbook --add-label "diagram,priority: medium"
```

3) 古い/解決済みのクローズ

```bash
# 明確に解決済み（該当PR/コミット有）
gh issue close <num> -R itdojp/theoretical-computer-science-textbook \
  -c "現在の main にて解消済みのためクローズします。問題が続く場合はreopenください。"

# 情報不足
gh issue comment <num> -R itdojp/theoretical-computer-science-textbook \
  -b "再現手順と使用環境の詳細をご提供ください。2週間無反応の場合はクローズします。"
gh issue edit <num> -R itdojp/theoretical-computer-science-textbook --add-label needs-more-info
```

4) 高優先度の即時対応

- 直接修正 or 再現→修正→PR。PRテンプレートに「修正内容/再現/影響範囲/スクショ」を添付。

## 備考

- a11y（SVG）は現状全件対応済み。新規追加分のみ監視。
- 8章ネットワークフロー関連は補助図・脚注整備済み。追加要望は `diagram` ラベルに集約。

