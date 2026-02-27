---
layout: book
title: "第8章 グラフ理論とネットワーク"
subtitle: "グラフアルゴリズムと応用"
chapter: 8
description: "グラフ理論の基礎からネットワーク解析まで"
estimated_time: "5〜6週間"
difficulty: "★★★☆"
sections:
  - "グラフの基本概念"
  - "探索アルゴリズム"
  - "最短路問題"
  - "最大流問題"
  - "マッチング理論"
  - "グラフ彩色"
  - "ネットワーク解析"
---

# 第8章 グラフ理論とネットワーク

## はじめに

グラフ理論は、オブジェクト間の関係を数学的に表現し分析する強力な枠組みを提供します。ネットワーク、回路設計、ソーシャルメディア、交通システムなど、現実世界の多くの問題がグラフとして自然にモデル化されます。本章では、グラフの基本的な性質から始まり、最短路、ネットワークフロー、マッチングなどの古典的問題とその効率的なアルゴリズムを詳しく学びます。

グラフアルゴリズムの理論は、単なる抽象的な数学ではありません。インターネットのルーティング、SNSの友人推薦、配送経路の最適化など、日常的に使用される技術の基盤となっています。本章では、これらの応用を念頭に置きながら、理論的な深さと実践的な洞察の両方を提供します。

### 学習目標

- グラフの表現（隣接行列/リスト、圧縮表現）と計算量の違いを説明できる
- BFS/DFS の性質と到達性・木辺/後退辺の関係を説明できる
- 最短路（Dijkstra, Bellman–Ford, DAG 最短路）の適用条件と計算量を説明できる
- 最大流最小カット（Edmonds–Karp, Dinic）の考え方を概説できる
- 二部グラフマッチングとの関係（Kőnig の定理の直観）を説明できる

## 8.1 グラフの基本理論

### 8.1.1 グラフの表現と基本概念

**定義 8.1** **グラフ** \\(G = (V, E)\\) は頂点集合 \\(V\\) と辺集合 \\(E\\) から構成される。
{: #def-8-1 }
- 無向グラフ：\\(E \\subseteq \\{(u, v) \\mid u, v \\in V, u \\ne v\\}\\)
- 有向グラフ：E ⊆ V × V

**グラフの表現方法**：
1. **隣接行列**：A[i,j] = 1 if (i,j) ∈ E
   - 空間：\\(O(\\lvert V\\rvert^2)\\)
   - 辺の存在確認：O(1)
   - 全辺の走査：\\(O(\\lvert V\\rvert^2)\\)

2. **隣接リスト**：各頂点の隣接頂点のリスト
   - 空間：\\(O(\\lvert V\\rvert + \\lvert E\\rvert)\\)
   - 頂点の隣接頂点走査：O(deg(v))
   - 全辺の走査：\\(O(\\lvert V\\rvert + \\lvert E\\rvert)\\)

【実務上の注意（表現とメモリ）】
- 疎グラフ（\\(\\lvert E\\rvert \\ll \\lvert V\\rvert^2\\)）では隣接リストが有利、密グラフでは隣接行列が簡潔かつ高速。
- 重み付き疎グラフの大規模処理では、CSR/COO といった圧縮表現がキャッシュ効率と並列化で有利。
- 0/1重みや単位重みでは、BFSや0-1 BFS（デック使用）で大幅な高速化が可能。
- 有向/無向や自己ループ・多重辺の扱いを明確に（アルゴリズムの仮定に影響）。

### 8.1.2 基本的なグラフの性質

**定理 8.1**（握手補題）無向グラフ \\(G = (V, E)\\) において：
{: #thm-8-1 }
∑_{v∈V} deg(v) = 2\\(\lvert E\rvert\\)

*証明*：各辺は両端点の次数にそれぞれ1ずつ寄与する。□

**系 8.1** 無向グラフにおいて、奇数次数の頂点数は偶数個。
{: #cor-8-1 }

**定理 8.2**（Eulerの公式）連結平面グラフ \\(G = (V, E, F)\\) において：
{: #thm-8-2 }
\\(\lvert V\rvert\\) − \\(\lvert E\rvert\\) + \\(\lvert F\rvert\\) = 2
（F は面の集合）

**系 8.2** 単純連結平面グラフ（\\(\lvert V\rvert\\) ≥ 3）において：\\(\lvert E\rvert\\) ≤ 3\\(\lvert V\rvert\\) − 6
{: #cor-8-2 }

### 8.1.3 グラフの走査

直観図：同一グラフに対する BFS と DFS の探索順・探索木の比較

![BFS と DFS の比較]({{ '/assets/images/diagrams/ch8_bfs_vs_dfs_compare.svg' | relative_url }})

#### 深さ優先探索（DFS）

```text
DFS(G, s):
    for each v ∈ V:
        color[v] = WHITE
        π[v] = NIL
    time = 0  // グローバル変数として時刻を管理
    DFS-Visit(s)

DFS-Visit(u):
    time = time + 1  // timeはグローバル変数
    d[u] = time      // 発見時刻を記録
    color[u] = GRAY
    for each v ∈ Adj[u]:
        if color[v] == WHITE:
            π[v] = u
            DFS-Visit(v)
    color[u] = BLACK
    time = time + 1  // timeはグローバル変数
    f[u] = time      // 終了時刻を記録
```

**性質**：
- 時間複雑度：\\(O(\lvert V\rvert + \lvert E\rvert)\\)
- DFS木を生成
- 開始時刻 d[v] と終了時刻 f[v] を記録

#### 幅優先探索（BFS）

```text
BFS(G, s):
    for each v ∈ V \ {s}:
        color[v] = WHITE
        d[v] = ∞
        π[v] = NIL
    color[s] = GRAY
    d[s] = 0
    π[s] = NIL
    Q = {s}
    while Q ≠ ∅:
        u = Dequeue(Q)
        for each v ∈ Adj[u]:
            if color[v] == WHITE:
                color[v] = GRAY
                d[v] = d[u] + 1
                π[v] = u
                Enqueue(Q, v)
        color[u] = BLACK
```

**定理 8.3** BFS は始点からの最短路（辺数）を正しく計算する。
{: #thm-8-3 }

### 8.1.4 連結性

**定義 8.2** 
{: #def-8-2 }
- 無向グラフが**連結**：任意の2頂点間に路が存在
- 有向グラフが**強連結**：任意の2頂点間に有向路が存在

**強連結成分**の検出（Kosarajuのアルゴリズム）：
1. G で DFS を実行し、終了時刻の降順を記録
2. G^T（転置グラフ）で、その順序で DFS を実行
3. 各 DFS木が強連結成分

時間複雑度：\\(O(\lvert V\rvert + \lvert E\rvert)\\)

**定理 8.4** 無向グラフ \\(G\\) が連結 \\(\Leftrightarrow\\) 任意の空でない真部分集合 \\(S \subset V\\) に対して、
{: #thm-8-4 }
S と V \ S を結ぶ辺が存在。

## 8.2 最短路問題

### 8.2.1 単一始点最短路

![Dijkstraアルゴリズムの実行例]({{ '/assets/images/diagrams/ch8_dijkstra_algorithm_execution.svg' | relative_url }})

#### Dijkstraのアルゴリズム

**前提**：非負の辺重み

```text
Dijkstra(G, w, s):
    for each v ∈ V:
        d[v] = ∞
        π[v] = NIL
    d[s] = 0
    S = ∅
    Q = V
    while Q ≠ ∅:
        u = Extract-Min(Q)
        S = S ∪ {u}
        for each v ∈ Adj[u]:
            if d[v] > d[u] + w(u,v):
                d[v] = d[u] + w(u,v)
                π[v] = u
```

**定理 8.5** Dijkstraのアルゴリズムは非負重みグラフで正しく最短路を計算する。
{: #thm-8-5 }

*証明*（不変条件）：S に追加される頂点の d 値は最短距離に等しい。
帰納法により証明。□

例示図：Dijkstra の逐次確定（確定集合と緩和の模式図）

![Dijkstra 法の逐次確定の例]({{ '/assets/images/diagrams/ch8_dijkstra_step_trace.svg' | relative_url }})

**時間複雑度**：
- 二分ヒープ：\\(O((\lvert V\rvert + \lvert E\rvert) \log \lvert V\rvert)\\)
- フィボナッチヒープ：\\(O(\lvert V\rvert \log \lvert V\rvert + \lvert E\rvert)\\)

【実務メモ（最短路）】
- 場合分け: 負辺→Bellman-Ford/Johnson、単位重み→BFS、0/1重み→0-1 BFS、一般重み→Dijkstra。
- 優先度キューの選択: 実装定数因子まで含めると二分ヒープがしばしば有利。超大規模・理論性能重視ならフィボナッチヒープ。
- 並列化: 大規模グラフではΔ-stepping等の近似並列Dijkstraが有効な場合がある。

【0/1 BFS の最小実装（\\(O(\lvert V\rvert + \lvert E\rvert)\\)）】
```text
ZeroOneBFS(G, w ∈ {0,1}, s):
    for v in V: d[v] = ∞
    d[s] = 0
    Deque Q = {s}
    while Q not empty:
        u = pop_front(Q)
        for (u,v) in Adj[u]:
            if d[v] > d[u] + w(u,v):
                d[v] = d[u] + w(u,v)
                if w(u,v) == 0: push_front(Q, v)
                else:            push_back(Q, v)
    return d
```

#### Bellman-Fordアルゴリズム

**利点**：負の重みを許容、負閉路を検出

```text
Bellman-Ford(G, w, s):
    for each v ∈ V:
        d[v] = ∞
        π[v] = NIL
    d[s] = 0
    for i = 1 to |V| - 1:
        for each edge (u,v) ∈ E:
            if d[v] > d[u] + w(u,v):
                d[v] = d[u] + w(u,v)
                π[v] = u
    // 負閉路の検出
    for each edge (u,v) ∈ E:
        if d[v] > d[u] + w(u,v):
            return "負閉路が存在"
    return d
```

時間複雑度：\\(O(\\lvert V\\rvert \\cdot \\lvert E\\rvert)\\)

### 8.2.2 全点対最短路

#### Floyd-Warshallアルゴリズム

動的計画法による解法：
d_ij^(k) = 頂点 {1, 2, ..., k} を中継点として使う場合の i から j への最短距離

```text
Floyd-Warshall(W):
    n = |V|
    D^(0) = W
    for k = 1 to n:
        for i = 1 to n:
            for j = 1 to n:
                d_ij^(k) = min(d_ij^(k-1), d_ik^(k-1) + d_kj^(k-1))
    return D^(n)
```

時間複雑度：\\(O(\\lvert V\\rvert^3)\\)
空間複雑度：\\(O(\\lvert V\\rvert^2)\\)（1つの行列を更新）

### 8.2.3 特殊なグラフでの最短路

**DAG（有向非巡回グラフ）での最短路**：
トポロジカル順序で緩和することで \\(O(\\lvert V\\rvert + \\lvert E\\rvert)\\) で解ける。

【グラフ実装の落とし穴】
- インデックスの基準（0/1始まり）を混在させない。入力→内部表現の変換で統一。
- 重みのスケール（int/long/double）とオーバーフロー/誤差に注意。距離の初期化∞は十分大きな値で。
- 無向グラフは両方向登録を忘れない（重複挿入の有無と総カウントに注意）。
- 隣接リストの反復中に構造を変更しない（並行変更バグ）。

**定理 8.6** 単位重み（すべての辺の重みが1）のグラフでは、
{: #thm-8-6 }
BFS が \\(O(\\lvert V\\rvert + \\lvert E\\rvert)\\) で最短路を求める。

## 8.3 最小全域木

### 8.3.1 最小全域木の性質

**定義 8.3** 連結無向グラフ \\(G = (V, E)\\) の**全域木**は、
{: #def-8-3 }
すべての頂点を含み、\\(\lvert V\rvert\\) − 1 本の辺を持つ部分グラフ。

**カット性質**：グラフの任意のカット (S, V \ S) を横切る最小重み辺は、
ある最小全域木に含まれる。

**サイクル性質**：グラフの任意のサイクル中の最大重み辺は、
すべての最小全域木に含まれない。

### 8.3.2 Kruskalのアルゴリズム

直観図：Kruskal法とUnion-Findの流れ

注: Union-Find（互いに素集合データ構造）は、集合を併合し代表元を素早く求める構造で、
経路圧縮とランク併合により実用上ほぼ定数時間（逆アッカーマン関数 α(n) で界）を達成する。

![Kruskal法とUnion-Findの流れ]({{ '/assets/images/diagrams/ch8_mst_kruskal_unionfind.svg' | relative_url }})

```text
Kruskal(G, w):
    A = ∅
    for each v ∈ V:
        Make-Set(v)
    辺を重みの昇順にソート
    for each edge (u,v) ∈ E (昇順):
        if Find-Set(u) ≠ Find-Set(v):
            A = A ∪ {(u,v)}
            Union(u, v)
    return A
```

時間複雑度：\\(O(\lvert E\rvert \log \lvert E\rvert)\\)

### 8.3.3 Primのアルゴリズム

```text
Prim(G, w, r):
    for each v ∈ V:
        key[v] = ∞
        π[v] = NIL
    key[r] = 0
    Q = V
    while Q ≠ ∅:
        u = Extract-Min(Q)
        for each v ∈ Adj[u]:
            if v ∈ Q and w(u,v) < key[v]:
                π[v] = u
                key[v] = w(u,v)
```

時間複雑度：
- 二分ヒープ：\\(O(\lvert E\rvert \log \lvert V\rvert)\\)
- フィボナッチヒープ：\\(O(\lvert E\rvert + \lvert V\rvert \log \lvert V\rvert)\\)

**定理 8.7** KruskalとPrimのアルゴリズムは正しく最小全域木を求める。
{: #thm-8-7 }

## 8.4 ネットワークフロー

### 8.4.1 最大フロー問題

**定義 8.4** **フローネットワーク** \\(G = (V, E)\\) は：
{: #def-8-4 }
- 容量関数 \\(c: V \\times V \\to \\mathbb{R}_{>0}\\)
- 始点 s、終点 t

**フロー** \\(f: V \\times V \\to \\mathbb{R}\\) は以下を満たす：
1. 容量制約：0 ≤ f(u,v) ≤ c(u,v)
2. 流量保存：∑_v f(v,u) = ∑_v f(u,v) （u ≠ s,t）

![最大フロー最小カットの例]({{ '/assets/images/diagrams/ch8_maximum_flow_minimum_cut.svg' | relative_url }})

### 8.4.2 Ford-Fulkerson法

```text
Ford-Fulkerson(G, s, t):
    for each edge (u,v) ∈ E:
        f(u,v) = 0
    while 残余グラフ G_f に s-t パスが存在:
        p = G_f における s-t パス
        c_f(p) = min{c_f(u,v) : (u,v) ∈ p}
        for each edge (u,v) ∈ p:
            if (u,v) ∈ E:
                f(u,v) = f(u,v) + c_f(p)
            else:
                f(v,u) = f(v,u) - c_f(p)
    return f
```

**定理 8.8**（最大フロー最小カット定理）
{: #thm-8-8 }
以下の条件は同値：
1. f は最大フロー
2. 残余グラフに増加路が存在しない
3. \\(\lvert f\rvert\\) = c(S,T) となるカット (S,T) が存在

### 8.4.3 効率的な実装

#### Edmonds-Karp法
増加路を BFS で見つける：\\(O(\\lvert V\\rvert \\cdot \\lvert E\\rvert^2)\\)

#### Dinicのアルゴリズム
レベルグラフを用いたブロッキングフロー：\\(O(\\lvert V\\rvert^2 \\cdot \\lvert E\\rvert)\\)

#### Push-Relabel法
```text
Push-Relabel(G, s, t):
    前処理で高さ関数とプレフローを初期化
    while 活性頂点が存在:
        v = 活性頂点
        if v から押し出し可能:
            Push(v)
        else:
            Relabel(v)
```

時間複雑度：\\(O(\\lvert V\\rvert^2 \\cdot \\lvert E\\rvert)\\)

### 8.4.4 応用

**最小費用最大フロー**：
各辺にコストを付加し、最大フロー中で総コスト最小のものを求める。

**多品種フロー**：
複数の始点・終点ペアのフローを同時に扱う。

## 8.5 マッチング理論

### 8.5.1 二部グラフのマッチング

**定義 8.5** グラフ \\(G = (V, E)\\) の**マッチング** \\(M \subseteq E\\) は、
{: #def-8-5 }
どの2辺も共通の端点を持たない辺集合。

![二部グラフのマッチング]({{ '/assets/images/diagrams/ch8_bipartite_graph_matching.svg' | relative_url }})

**定理 8.9**（Hallの結婚定理）
{: #thm-8-9 }
二部グラフ G = (X ∪ Y, E) が X を飽和するマッチングを持つ ⟺
∀S ⊆ X, \\(\lvert N(S)\rvert\\) ≥ \\(\lvert S\rvert\\)
（N(S) は S の隣接頂点集合）

**定理 8.10**（Kőnig-Egerváryの定理）
{: #thm-8-10 }
二部グラフにおいて：最大マッチングのサイズ = 最小頂点被覆のサイズ

### 8.5.2 最大マッチングアルゴリズム

#### 二部グラフの場合（Hungarian法）
最大フローへの帰着により \\(O(\lvert E\rvert \cdot \lvert V\rvert^{1/2})\\) で解ける。

#### 一般グラフの場合（Edmondsのアルゴリズム）
花（blossom）の縮約を用いる：\\(O(\\lvert V\\rvert^3)\\)

### 8.5.3 完全マッチング

**定理 8.11**（Tutteの定理）
{: #thm-8-11 }
グラフ G が完全マッチングを持つ ⟺
∀S ⊆ V, o(G - S) ≤ \\(\lvert S\rvert\\)
（o(G - S) は G - S の奇数サイズ連結成分数）

### 8.5.4 安定マッチング

**Gale-Shapleyアルゴリズム**：
```text
Gale-Shapley(男性の選好, 女性の選好):
    全員を未婚に初期化
    while 未婚の男性が存在:
        m = 未婚の男性
        w = m の選好リストの最上位の未プロポーズ女性
        if w が未婚:
            (m, w) を婚約
        else if w が現在の相手より m を選好:
            w の現在の相手を未婚に
            (m, w) を婚約
    return マッチング
```

時間複雑度：\\(O(n^2)\\)

**定理 8.12** Gale-Shapleyアルゴリズムは安定マッチングを生成し、
{: #thm-8-12 }
それは男性最適・女性最悪である。

## 8.6 グラフの彩色

### 8.6.1 頂点彩色

**定義 8.6** グラフ G の**彩色数** \\(\\chi(G)\\) は、
{: #def-8-6 }
隣接頂点が異なる色となるように頂点を彩色するのに必要な最小色数。

**定理 8.13**（Brooksの定理）
{: #thm-8-13 }
連結グラフ G が完全グラフでも奇サイクルでもなければ、
χ(G) ≤ Δ(G)（Δ(G) は最大次数）

### 8.6.2 辺彩色

**定理 8.14**（Vizingの定理）
{: #thm-8-14 }
単純グラフ G の辺彩色数 χ'(G) は：
\\(\\Delta(G) \\le \\chi^{\\prime}(G) \\le \\Delta(G) + 1\\)

### 8.6.3 平面グラフの彩色

**定理 8.15**（4色定理）
{: #thm-8-15 }
すべての平面グラフは4彩色可能。

**定理 8.16**（5色定理）
{: #thm-8-16 }
すべての平面グラフは5彩色可能。

*証明の概要*：最小次数が5以下であることと帰納法を用いる。□

### 8.6.4 彩色アルゴリズム

**貪欲彩色**：
頂点を任意の順序で処理し、使用可能な最小の色を割り当てる。

**定理 8.17** 適切な頂点順序により、貪欲彩色は \\(\\chi(G)\\) 色で彩色する。
{: #thm-8-17 }

## 8.7 特殊なグラフクラス

### 8.7.1 平面グラフ

**定理 8.18**（Kuratowskiの定理）
{: #thm-8-18 }
グラフが平面的 ⟺ \\(K_5\\) または \\(K_{3,3}\\) の細分を部分グラフとして含まない。

**平面性判定**：\\(O(\lvert V\rvert)\\) アルゴリズムが存在。

### 8.7.2 木構造

**定理 8.19** 以下は同値：
{: #thm-8-19 }
1. G は木
2. G は連結で \\(\lvert E\rvert\\) = \\(\lvert V\rvert\\) − 1
3. G は非巡回で \\(\lvert E\rvert\\) = \\(\lvert V\rvert\\) − 1
4. 任意の2頂点間に唯一のパスが存在

### 8.7.3 弦グラフ

**定義 8.7** グラフが**弦グラフ**（chordal graph）\\(\Leftrightarrow\\)
{: #def-8-7 }
長さ4以上のすべてのサイクルが弦を持つ。

**性質**：
- 完全消去順序が存在
- 多項式時間で多くの NP困難問題が解ける

## 8.8 ランダムグラフ

### 8.8.1 Erdős-Rényiモデル

**G(n,p)**：n 頂点で各辺が独立に確率 p で存在。

**定理 8.20** \\(p = (\log n + c)/n\\) のとき：
{: #thm-8-20 }
- c → -∞ ⟹ G(n,p) はほぼ確実に非連結
- c → +∞ ⟹ G(n,p) はほぼ確実に連結

### 8.8.2 小世界ネットワーク

**Watts-Strogatzモデル**：
規則的な格子から始めて、辺をランダムに繋ぎ変える。

**性質**：
- 小さい平均距離
- 高いクラスタリング係数

### 8.8.3 スケールフリーネットワーク

**Barabási-Albertモデル**：
優先的選択により成長。

**次数分布**：P(k) ∝ k^{-γ}（べき乗則）

## まとめ

- 表現の選択がアルゴリズムの計算量と実装の実効性能に直結する
- 最短路・最大流・マッチングは応用範囲が広く、適用条件の把握が鍵
- カット・フローの双対性や交換引数などで正当性と限界を理解する

## 章末問題

- 代表演習と詳細解答は [付録C（第8章）](../appendices/c/#ex-sol-ch8) を参照。

### 基礎問題

1. 以下のグラフアルゴリズムを実装し、時間複雑度を解析せよ：
   (a) トポロジカルソート
   (b) 2-SAT の多項式時間解法
   (c) 最長パス（DAG）

2. Dijkstraのアルゴリズムが負の重みで失敗する例を構成せよ。

3. 最小全域木がユニークとなる必要十分条件を示せ。

4. 二部グラフの最大マッチングを最大フロー問題に帰着せよ。

### 発展問題

5. プラナーグラフの双対グラフについて：
   (a) 双対グラフの定義と性質を述べよ
   (b) 最短路と最小カットの双対性を説明せよ

6. グラフの木幅（treewidth）について：
   (a) 定義と計算複雑性を述べよ
   (b) 有界木幅グラフで効率的に解ける問題を列挙せよ

7. 頂点彩色問題の近似アルゴリズムについて：
   (a) 貪欲法の近似比を証明せよ
   (b) より良い近似アルゴリズムを設計せよ

8. ネットワーク信頼性について：
   (a) 最小カットと辺連結度の関係を示せ
   (b) k-辺連結グラフの判定アルゴリズムを示せ

### 探究課題

9. ソーシャルネットワーク分析で使用されるグラフ指標（中心性、クラスタリング係数など）について調査し、
   計算アルゴリズムを設計せよ。

10. グラフニューラルネットワーク（GNN）の理論的基礎について調査し、
    表現力の限界を論ぜよ。

11. 量子アルゴリズムによるグラフ問題の高速化について調査し、
    古典アルゴリズムとの比較を行え。

12. 動的グラフアルゴリズム（頂点・辺の追加削除に対応）について調査し、
    静的アルゴリズムからの改善を論ぜよ。

### 実装課題

13. グラフアルゴリズムライブラリを実装せよ：
    ```python
    class GraphAlgorithms:
        def dijkstra(self, graph, source):
            """Dijkstraの最短路アルゴリズム"""
            pass
        
        def max_flow(self, graph, source, sink):
            """最大フローアルゴリズム（Ford-Fulkerson）"""
            pass
        
        def minimum_spanning_tree(self, graph, algorithm='kruskal'):
            """最小全域木（Kruskal or Prim）"""
            pass
        
        def strongly_connected_components(self, graph):
            """強連結成分分解（Tarjanのアルゴリズム）"""
            pass
    ```

14. ネットワーク分析ツールを実装せよ：
    ```python
    class NetworkAnalysis:
        def centrality_measures(self, graph):
            """中心性指標の計算（次数、媒介、固有ベクトル中心性）"""
            pass
        
        def community_detection(self, graph):
            """コミュニティ検出アルゴリズム"""
            pass
        
        def graph_visualization(self, graph, layout='spring'):
            """グラフの可視化"""
            pass
        
        def generate_random_graphs(self, model, parameters):
            """ランダムグラフの生成（Erdős-Rényi, Barabási-Albert等）"""
            pass
    ```

15. グラフ問題の性能比較：
    - 最短路アルゴリズムの比較（Dijkstra, Bellman-Ford, Floyd-Warshall）
    - 最大フローアルゴリズムの比較（Ford-Fulkerson, Dinic, Push-Relabel）
    - 実グラフでの性能測定と分析

---
