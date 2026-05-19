# 第11章 PQC 標準化記述の保守方針

## 目的

第11章 11.3.5「耐量子暗号（PQC）の標準化動向」は、NIST の標準化状況に依存する時点付き記述を含む。本文の読者が、最終標準、策定中の標準、運用上の注意を混同しないように、確認対象、更新条件、記録方法を定める。

この文書は Issue #355 の保守成果物であり、本文を変更する前の判断基準として使う。

## 2026-05-14（Asia/Tokyo）時点の確認済み標準情報

| 項目 | 本文での扱い | 公式確認先 | 2026-05-14（Asia/Tokyo）時点の判断 |
| --- | --- | --- | --- |
| FIPS 203 / ML-KEM | 最終 FIPS。KEM として紹介する。 | https://csrc.nist.gov/pubs/fips/203/final | 最終 FIPS。2025-11-17 の planning note に errata 予定があるため、改訂時は本文のリンク先と表現を再確認する。 |
| FIPS 204 / ML-DSA | 最終 FIPS。署名方式として紹介する。 | https://csrc.nist.gov/pubs/fips/204/final | 最終 FIPS。2026-02-23 の planning note に minor issues の errata 予定があるため、改訂時は本文のリンク先と表現を再確認する。 |
| FIPS 205 / SLH-DSA | 最終 FIPS。ステートレスなハッシュベース署名として紹介する。 | https://csrc.nist.gov/pubs/fips/205/final | 最終 FIPS。現行本文の分類と整合している。 |
| HQC | ML-KEM のバックアップ KEM として、標準化対象に選定済みと説明する。 | https://www.nist.gov/news-events/news/2025/03/nist-selects-hqc-fifth-algorithm-post-quantum-encryption | NIST は HQC をバックアップ KEM として選定している。最終 FIPS ではなく、標準化プロセス中として扱う。 |
| FALCON / FN-DSA / FIPS 206 | 追加署名標準として扱われる予定と説明する。 | https://csrc.nist.gov/Projects/Post-Quantum-Cryptography/Post-Quantum-Cryptography-Standardization | NIST は FALCON を FIPS 206 として開発中と説明している。最終 FIPS として断定しない。 |
| KEM 運用ガイダンス | 必要に応じて運用上の補足に反映する。 | https://csrc.nist.gov/pubs/sp/800/227/final | SP 800-227 は KEM の性質・用途・実装推奨を扱う関連資料。本文で KEM 運用を詳述する場合に参照する。 |

## 本文更新が必要になる条件

次のいずれかに該当する場合、`docs/chapter-11/index.md` と `src/chapter-11/index.md` を同一内容で更新する。

1. NIST が FIPS 203 / 204 / 205 の改訂版を公開し、アルゴリズム名、標準名、パラメータ集合、または安全性説明に本文へ影響する変更がある。
2. HQC の draft または final FIPS が公開され、本文の「選定済み」「最終文書化状況は変わり得る」という表現が古くなる。
3. FIPS 206 / FN-DSA が draft または final として公開され、本文の「予定」という表現が古くなる。
4. NIST の PQC プロジェクトページが、2026年5月時点の本文と異なる標準一覧、移行方針、または推奨を明示する。
5. 外部リンクの恒久 URL が変わる、または CSRC の publication ページが obsoleted / withdrawn を示す。

## 更新時の編集規則

- 時点依存の文は「YYYY年M月時点で」の形で明示する。
- final、draft、selected、in development を区別し、draft や選定済みの方式を最終 FIPS として記述しない。
- 本文中では標準名と方式名を併記する。例: FIPS 203 / ML-KEM、FIPS 204 / ML-DSA、FIPS 205 / SLH-DSA。
- 方式の安全性については「量子計算機に対して破れない」と断定せず、「現時点で耐量子を意図して標準化された」「NIST 文書では量子計算機を持つ攻撃者も想定している」など、根拠と範囲を示す。
- `docs/` と `src/` の章本文を同時に更新し、差分後に同期確認を行う。
- 本文を変更しない場合も、対象 Issue または PR に「確認日、確認した公式ページ、本文変更不要の理由」を記録する。

## 確認手順

1. 公式ページのみを一次情報として確認する。優先順は CSRC publication ページ、NIST PQC project ページ、NIST news、Federal Register notice とする。
2. FIPS 203 / 204 / 205 の publication ページで planning note、document history、errata を確認する。
3. PQC standardization process と selected algorithms ページで HQC、FALCON / FN-DSA、FIPS 206 / FIPS 207 の状態を確認する。
4. 変更がある場合は本文の該当段落だけを小さな PR とし、必要なら脚注・注記に分離する。
5. PR では少なくとも次を記録する。
   - 確認した URL と確認日
   - 本文変更の有無
   - `docs/` と `src/` の同期確認結果
   - 実行したローカル検証と GitHub Actions 結果

## 今回の判断

2026-05-14（Asia/Tokyo）の確認では、第11章の現行本文は次の理由で修正不要と判断する。

- FIPS 203、FIPS 204、FIPS 205 は引き続き最終 FIPS として公開されている。
- HQC は ML-KEM のバックアップ KEM として選定済みだが、本文は最終標準として断定していない。
- FALCON 由来 FN-DSA / FIPS 206 は開発中または予定として扱うのが妥当であり、本文は「予定」「最終文書化状況は変わり得る」と限定している。
- FIPS 203 と FIPS 204 には planning note / errata 予定があるが、現時点では本文の標準名・方式名・final FIPS という分類を変更する根拠にはならない。

## 再確認メモ — 2026-05-19（Asia/Tokyo）

Issue #366 の第11章深掘りレビューで、次の一次情報を再確認した。

- FIPS 203 / 204 / 205 の CSRC publication page は引き続き final FIPS として公開されている。
- NIST の selected algorithms page は HQC と FALCON / FN-DSA / FIPS 206 を FIPS coming soon として扱っており、最終 FIPS として断定しない現行分類と整合する。
- NIST の HQC news は HQC を ML-KEM のバックアップ KEM として選定した根拠として引き続き有効である。
- SP 800-227 final は KEM 運用ガイダンスとして引き続き参照対象である。

この再確認では、FIPS 203 / 204 / 205 の final 分類、HQC の selected / in-progress 分類、FALCON / FN-DSA / FIPS 206 の planned / coming-soon 分類を変更する根拠は見つからなかった。本文では、HQC と FIPS 206 系を最終 FIPS と誤読しないよう注意書きを補強する。
