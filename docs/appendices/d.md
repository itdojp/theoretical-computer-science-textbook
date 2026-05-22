---
title: "付録D: 用語集・索引"
layout: book
---

# 付録D: 用語集・索引

理論計算機科学で使用される専門用語の日英対訳と詳細な説明です。
（主要トピックへの関連章リンクを併記しています）

## この付録の使い方

- **用語が分かっているとき**: 下の A-Z の並びから該当文字の節へ進み、用語の定義と関連章を確認してください。
- **概念から探したいとき**: 次の「概念別クイックナビ」から近い話題群を選び、主要語へ移動してください。
- **記号から探したいとき**: 本文末の「記号索引」を使って、論理・集合・複雑性・形式言語・関数・グラフの記号を引いてください。

## A-Z クイックナビ

- [A](#appendix-d-a) [B](#appendix-d-b) [C](#appendix-d-c) [D](#appendix-d-d) [E](#appendix-d-e) [F](#appendix-d-f) [G](#appendix-d-g) [H](#appendix-d-h) [I](#appendix-d-i) [J](#appendix-d-j) [K](#appendix-d-k) [L](#appendix-d-l) [M](#appendix-d-m)
- [N](#appendix-d-n) [O](#appendix-d-o) [P](#appendix-d-p) [Q](#appendix-d-q) [R](#appendix-d-r) [S](#appendix-d-s) [T](#appendix-d-t) [U](#appendix-d-u) [V](#appendix-d-v) [W](#appendix-d-w) [X](#appendix-d-x) [Y](#appendix-d-y) [Z](#appendix-d-z) [記号索引](#appendix-d-symbols)

## 概念別クイックナビ

- **数学的基礎と証明**: [空集合](#empty-set), [関数](#function), [背理法](#proof-by-contradiction)
- **計算モデル・形式言語**: [有限オートマトン](#finite-automaton), [文脈自由文法](#context-free-grammar), [チューリング機械](#turing-machine), [Church-Turing仮説](#church-turing-thesis)
- **計算可能性・複雑性**: [計算可能性](#computability), [決定可能性](#decidability), [複雑性クラス](#complexity-class), [停止問題](#halting-problem)
- **アルゴリズム・データ構造**: [アルゴリズム](#algorithm), [償却解析](#amortized-analysis), [B木](#b-tree), [ブルームフィルタ](#bloom-filter)
- **グラフ・ネットワーク**: [グラフ](#graph), [二部グラフ](#bipartite-graph), [増加路](#増加路-augmenting-path), [カット](#カット-st–t-cut)
- **論理・形式手法**: [計算木論理](#ctl), [線形時相論理](#ltl), [Hoare論理](#hoare-logic), [双模倣等価](#bisimulation-equivalence)
- **情報理論・符号**: [等確率分割性](#AEP-asymptotic-equipartition-property), [通信路容量](#通信路容量-channel-capacity), [誤り訂正符号](#error-correcting-code), [相互情報量](#相互情報量-mutual-information)
- **暗号**: [認証付き暗号](#authenticated-encryption), [準同型暗号](#homomorphic-encryption), [ハッシュ関数](#hash-function)
- **並行・分散**: [Compare-and-Swap](#cas), [ABA問題](#aba-problem), [合意問題](#consensus-problem), [ビザンチン故障](#byzantine-fault), [分散スナップショット](#distributed-snapshot), [公平性](#fairness), [線形化可能性](#linearizability), [ロックフリー](#lock-free)

## A {#appendix-d-a}

<a id="algorithm"></a>
**アルゴリズム (Algorithm)**
- 問題を解くための明確で有限な手順の集合
- 入力から出力への変換プロセス
- 正確性、有限性、効率性が要求される

**アクセプタ (Acceptor)**
- 入力文字列を受理または拒否する計算装置
- 有限オートマトン、プッシュダウンオートマトン等

**アルファベット (Alphabet)**
- 記号の有限集合（通常Σで表記）
- 例: Σ = {0, 1}, Σ = {a, b, c}

**AND（論理積, AND Operation）**
- 論理積、∧記号で表記
- P ∧ Q は P と Q が共に真のときのみ真

<a id="aba-problem"></a>
**ABA問題（ABA Problem）**
- lock-free データ構造で、共有値が A→B→A と変化すると、見かけ上は未変更に見えて誤判定を招く問題
- CAS を使う実装で典型的に現れ、タグ付けや hazard pointer などの対策と併せて議論される（→ [第12章: 並行計算の理論](../chapter-12/index.md)）

**アトミック操作（Atomic Operation）**
- 他のスレッドから途中状態が観測されない、不可分な 1 操作として実行される操作
- compare-and-swap や fetch-and-add などが代表例で、並行アルゴリズムの基本部品となる（→ [第12章: 並行計算の理論](../chapter-12/index.md)）

<a id="authenticated-encryption"></a>
**認証付き暗号（Authenticated Encryption）**
- 秘匿性だけでなく、改ざん検知の完全性も同時に提供する暗号方式
- GCM や ChaCha20-Poly1305 のように、現代の通信路保護で標準的に使われる（→ [第11章: 暗号理論の数学的基礎](../chapter-11/index.md)）

<a id="amortized-analysis"></a>
**償却解析（Amortized Analysis）**
- 操作列全体で平均化した 1 回あたりのコストを評価する解析手法
- push/pop や Union-Find のように、個々の最悪時間より列全体の保証が重要な場面で使う（→ [第6章: アルゴリズムの数学的解析](../chapter-6/index.md), [第7章: データ構造の理論](../chapter-7/index.md)）

<a id="AEP-asymptotic-equipartition-property"></a>
**等確率分割性（AEP, Asymptotic Equipartition Property）**
- 長い列の振る舞いが“ほぼ一様”な典型集合に集中するという情報源の性質
- 情報源符号化（データ圧縮）の理論的基盤（→ [第10章: 情報理論](../chapter-10/index.md)）

<a id="増加路-augmenting-path"></a>
**増加路 (Augmenting Path)**
- 残余グラフ G_f における s から t へのパスで、各辺に正の残余容量があるもの
- 見つかった場合、そのボトルネック残余容量だけフローを増やせる（→ [第8章: ネットワークフロー](../chapter-8/index.md)）

## B {#appendix-d-b}

**ビッグオー記法（Big-O Notation）**
- 関数の上界を表す漸近記法
- f(n) = O(g(n)): f(n)はg(n)の定数倍を漸近的に超えない
- 時間・空間複雑性の解析に使用

<a id="bisimulation-equivalence"></a>
**双模倣等価（Bisimulation Equivalence）**
- ラベル付き遷移系や過程代数で、互いの遷移を逐次模倣できるときに成り立つ等価性
- トレース等価より分岐構造に敏感で、CCS や並行計算モデルの振る舞い比較に使う（→ [第12章: 並行計算の理論](../chapter-12/index.md)）

<a id="bipartite-graph"></a>
**二部グラフ（Bipartite Graph）**
- 頂点集合を 2 つの部分に分割し、各辺が異なる部分集合どうしを結ぶグラフ
- マッチング、頂点被覆、ネットワークフローとの接続で重要（→ [第8章: グラフ理論とネットワーク](../chapter-8/index.md)）

<a id="byzantine-fault"></a>
**ビザンチン故障（Byzantine Fault）**
- ノードが停止するだけでなく、任意または悪意ある振る舞いを取りうる故障モデル
- 合意問題では `n > 3f` のような条件とともに現れる（→ [第12章: 並行計算の理論](../chapter-12/index.md)）

<a id="b-tree"></a>
**B木（B-Tree）**
- 多分木を用いて外部記憶アクセス回数を抑える平衡探索木
- データベースやファイルシステムで広く使われ、I/O 計算量解析の代表例となる（→ [第7章: データ構造の理論](../chapter-7/index.md)）

**二分探索 (Binary Search)**
- ソート済み配列に対する効率的な探索アルゴリズム
- 時間複雑性: O(log n)
- 分割統治法の典型例

<a id="bloom-filter"></a>
**ブルームフィルタ（Bloom Filter）**
- 集合への所属を近似判定する確率的データ構造
- 偽陽性はありうるが偽陰性はなく、キャッシュや重複検出で用いられる（→ [第7章: データ構造の理論](../chapter-7/index.md)）

<a id="proof-by-contradiction"></a>
**背理法 (Proof by Contradiction)**
- 証明したい命題の否定を仮定し、矛盾を導く証明技法
- 決定不可能性の証明によく使用される

## C {#appendix-d-c}

<a id="turing-machine"></a>
**チューリング機械 (Turing Machine)**
- 理論計算機科学の基本的計算モデル
- 無限テープ、ヘッド、状態集合から構成
- 計算可能性の定義に使用（→ [第2章: 計算理論の基礎](../chapter-2/index.md)）

<a id="church-turing-thesis"></a>
**Church-Turing仮説 (Church-Turing Thesis)**
- 直感的に計算可能な関数はチューリング機械で計算可能
- 計算可能性の基本仮説

<a id="complexity-class"></a>
**複雑性クラス (Complexity Class)**
- 同程度の計算資源で解ける問題の集合
- 代表例として P, NP, PSPACE, EXPTIME などがある（→ [第5章: 計算複雑性理論](../chapter-5/index.md)）
- `hard` / `complete` はクラスそのものではなく、クラスに対する困難さの位置づけを表す語

<a id="cas"></a>
**Compare-and-Swap（CAS）**
- メモリ位置の値が期待値に一致するときだけ新しい値へ更新する原子的操作
- lock-free アルゴリズムの基本プリミティブで、ABA 問題とも密接に関係する（→ [第12章: 並行計算の理論](../chapter-12/index.md)）

<a id="consensus-problem"></a>
**合意問題（Consensus Problem）**
- 複数プロセスが初期値から 1 つの共通決定値へ到達できるかを扱う問題
- 分散故障モデル、FLP 不可能性、ビザンチン合意などの中心概念（→ [第12章: 並行計算の理論](../chapter-12/index.md)）

<a id="context-free-grammar"></a>
**文脈自由文法 (Context-Free Grammar)**
- 型2文法、プッシュダウンオートマトンと対応
- A → α の形の生成規則（Aは非終端記号）（→ [第3章: 形式言語とオートマトン理論](../chapter-3/index.md)）

<a id="computability"></a>
**計算可能性 (Computability)**
- アルゴリズムによって解ける問題の性質
- チューリング機械による定式化（→ [第4章: 計算可能性理論](../chapter-4/index.md)）

<a id="ctl"></a>
**計算木論理（CTL, Computation Tree Logic）**
- 分岐する未来をもつ計算木上で性質を記述する時相論理
- `AX`, `EF`, `AG` などの演算子を用い、モデル検査で広く使われる（→ [第9章: 論理学と形式的手法](../chapter-9/index.md), [第12章: 並行計算の理論](../chapter-12/index.md)）

<a id="通信路容量-channel-capacity"></a>
**通信路容量（Channel Capacity）**
- ある通信路で任意に小さい誤り確率で伝送できる最大レート C。離散無記憶通信路では C = max_{P(X)} I(X;Y)
- 通信路符号化定理の中心概念（→ [第10章: 情報理論](../chapter-10/index.md)）

<a id="補有限-cofinite"></a>
**補有限 (Cofinite)**
- 補集合が有限である言語（\\(\\Sigma^{\\ast} \\setminus L\\) が有限）
- 例: L が「有限に多くの語を除いてすべてを含む」場合
- Rice の定理の例として登場（→ [第4章: 計算可能性理論](../chapter-4/index.md)）

<a id="カット-st–t-cut"></a>
**カット (s–t Cut)**
- フローネットワークの頂点分割 (S,T) で s∈S, t∈T を満たすもの
- カット容量 c(S,T) = ∑_{u∈S, v∈T} c(u,v)
- 最大フロー最小カット定理（→ [第8章: ネットワークフロー](../chapter-8/index.md)）

## D {#appendix-d-d}

<a id="decidability"></a>
**決定可能性（Decidability）**
- ある問題に対してyes/noの答えを常に出力するアルゴリズムが存在する性質
- 決定可能言語 = 再帰言語
- 半決定可能（認識可能）とは異なり、すべての入力で停止することが要求される
- 参考: 第4章「決定不能問題」「還元可能性」（→ [第4章: 計算可能性理論](../chapter-4/index.md)）

**決定性有限オートマトン（Deterministic Finite Automaton, DFA）**
- 各状態・入力記号の組に対して遷移先が一意に決まるFA
- 正規言語を認識する最も基本的な計算モデル（→ [正規言語とDFA](../chapter-3/index.md)）

**深さ優先探索（Depth-First Search, DFS）**
- グラフ探索アルゴリズムの一種
- スタックまたは再帰を使用
- 時間複雑性: O(V + E)

**分割統治法（Divide and Conquer）**
- 問題を小さな部分問題に分割し、解を統合する手法
- マージソート、クイックソート等で使用

**動的計画法（Dynamic Programming）**
- 最適部分構造を持つ問題に対する最適化手法
- メモ化により重複計算を避ける

<a id="distributed-snapshot"></a>
**分散スナップショット（Distributed Snapshot）**
- 分散システム全体の大域状態を、通常実行を停止せずに整合的に記録する手法
- Chandy–Lamport アルゴリズムが代表例で、検査点取得やデバッグに用いられる（→ [第12章: 並行計算の理論](../chapter-12/index.md)）

<a id="ブロッキングフロー-blocking-flow"></a>
**ブロッキングフロー (Blocking Flow)**
- レベルグラフにおいて、s→t のすべてのパスが少なくとも1本の飽和辺を含むまで押し上げたフロー
- Dinic の各フェーズで計算（→ [第8章: ネットワークフロー](../chapter-8/index.md)）
- この状態では当該レベルグラフに増加路は存在しない

**学習節（Learned Clause）**
- CDCLにおいて競合分析で導出される節。以後の探索で同じ失敗を避けるために追加される

**非年代戻り（Non-chronological Backtracking）**
- CDCLで、直前の分岐に限らず原因レベルまで戻るバックトラック戦略

## E {#appendix-d-e}

**空文字列（Empty String）**
- 長さ0の文字列、εまたはλで表記
- すべての言語の部分集合

<a id="empty-set"></a>
**空集合（Empty Set）**
- 要素を含まない集合、∅で表記
- すべての集合の部分集合

<a id="error-correcting-code"></a>
**誤り訂正符号（Error-Correcting Code）**
- 通信や記録で生じる誤りを検出・訂正できるよう冗長性を加えた符号
- ハミング符号、Reed–Solomon 符号、LDPC 符号などが代表例（→ [第10章: 情報理論](../chapter-10/index.md)）

**ユークリッドアルゴリズム（Euclidean Algorithm）**
- 最大公約数を求める効率的アルゴリズム
- 時間複雑性: O(log min(a,b))

**指数時間（Exponential Time）**
- 実行時間がO(2^n)等の指数関数となるアルゴリズム
- 多くのNP完全問題の既知最良解法

## F {#appendix-d-f}

<a id="finite-automaton"></a>
**有限オートマトン（Finite Automaton）**
- 有限個の状態を持つ計算装置
- DFA（決定性）とNFA（非決定性）がある

**形式言語（Formal Language）**
- ある言語が表現するパターンを数学的に定義したもの
- チョムスキー階層による分類

<a id="fairness"></a>
**公平性（Fairness）**
- 並行実行やモデル検査で、ある操作やプロセスが不当に永遠に後回しにされないという仮定
- 活性（liveness）の検証で必要となり、時相論理や検証アルゴリズムの前提条件として現れる（→ [第9章: 論理学と形式的手法](../chapter-9/index.md), [第12章: 並行計算の理論](../chapter-12/index.md)）

**フィボナッチヒープ（Fibonacci Heap）**
- 償却計算量の観点で merge や decrease-key を高速化したヒープ構造
- ダイクストラ法や Prim 法の理論計算量改善で登場する（→ [第7章: データ構造の理論](../chapter-7/index.md)）

<a id="function"></a>
**関数（Function）**
- 定義域の各要素を値域の要素に対応させる規則
- \\(f: A \\to B\\) で表記

## G {#appendix-d-g}

**文法（Grammar）**
- 言語を生成するための規則の集合
- G = (V, T, P, S)で定義（V: 非終端記号, T: 終端記号, P: 生成規則, S: 開始記号）

<a id="graph"></a>
**グラフ（Graph）**
- 頂点（V）と辺（E）の集合 G = (V, E)
- 有向グラフと無向グラフがある
- 応用と表現は第8章を参照（→ [第8章: グラフ理論とネットワーク](../chapter-8/index.md)）

**貪欲法（Greedy Algorithm）**
- 各段階で局所的に最適な選択をする手法
- 最短路問題（ダイクストラ法）等で使用

**最大公約数（Greatest Common Divisor, GCD）**
- 2つの整数の共通約数の最大値
- ユークリッドアルゴリズムで効率的に計算

## H {#appendix-d-h}

<a id="halting-problem"></a>
**停止問題（Halting Problem）**
- チューリング機械が与えられた入力で停止するかを判定する問題
- 決定不可能問題の代表例

<a id="hash-function"></a>
**ハッシュ関数（Hash Function）**
- 任意サイズのデータを固定サイズの値に写像する関数
- データ構造では分散配置のために、暗号では改ざん検知や指紋のために使われる
- 文脈により「一般ハッシュ」と「暗号学的ハッシュ関数」を区別する（→ [第7章: データ構造の理論](../chapter-7/index.md), [第11章: 暗号理論の数学的基礎](../chapter-11/index.md)）

**ハッシュ表（Hash Table）**
- キーをハッシュ値で配列スロットへ割り当てる辞書データ構造
- 期待 O(1) の探索・挿入・削除を目指すが、衝突処理とハッシュ仮定に依存する（→ [第7章: データ構造の理論](../chapter-7/index.md)）

**ハミルトン経路（Hamiltonian Path）**
- グラフのすべての頂点を正確に一度ずつ通る経路
- NP完全問題
- NP完全性の文脈は第5章を参照（→ [第5章: 計算複雑性理論](../chapter-5/index.md)）

<a id="hoare-logic"></a>
**Hoare論理（Hoare Logic）**
- `{P} C {Q}` の Hoare triple で、プログラム実行前後の性質を記述する体系
- 部分正当性・全正当性・ループ不変量の議論の基盤になる（→ [第9章: 論理学と形式的手法](../chapter-9/index.md)）

<a id="homomorphic-encryption"></a>
**準同型暗号（Homomorphic Encryption）**
- 暗号文のまま加算や乗算などの演算を行い、復号後に平文演算結果を得られる暗号方式
- 秘匿計算やクラウド委託計算で重要であり、完全準同型暗号が代表例（→ [第11章: 暗号理論の数学的基礎](../chapter-11/index.md)）

## I {#appendix-d-i}

**帰納法（Induction）**
- 数学的帰納法: P(1) ∧ ∀k(P(k) → P(k+1)) → ∀n P(n)
- 構造帰納法: データ構造に対する帰納的証明

**単射（Injection）**
- 異なる入力は異なる出力を持つ関数
- ∀x,y ∈ A, f(x) = f(y) → x = y

**共通部分（intersection）**
- 2つの集合の共通要素の集合
- \\(A \\cap B = \\{\\,x \\mid x \\in A \\land x \\in B\\,\\}\\)

<a id="相互情報量-mutual-information"></a>
**相互情報量（Mutual Information）**
- 確率変数 X と Y の情報共有量：\\(I(X;Y) = H(X) + H(Y) - H(X,Y) = H(X) - H(X \mid Y)\\)
- 情報源・通信路の依存関係や特徴量選択の評価に用いる（→ [第10章: 情報理論](../chapter-10/index.md)）

## J {#appendix-d-j}

**結合 (Join)**
- グラフ理論: 2つの頂点を結ぶ操作
- データベース: テーブル間の結合操作

## K {#appendix-d-k}

**Kleene閉包 (Kleene Closure)**
- 言語 L に対して \\(L^{\ast} = L^0 \\cup L^1 \\cup L^2 \\cup \\cdots\\)
- 0回以上の連接

<a id="クラフトの不等式-kraft-inequality"></a>
**クラフトの不等式（Kraft–McMillan Inequality）**
- 一意復号可能符号の符号長 \\(l_1, \\ldots, l_n\\) に対し \\(\\sum D^{-l_i} \\le 1\\)（\\(D\\) は符号アルファベットの基数）
- 逆に、この不等式を満たす長さの組から瞬時符号の構成が可能（→ [第10章: 情報理論](../chapter-10/index.md)）

## L {#appendix-d-l}

**言語 (Language)**
- アルファベット上の文字列の集合
- \\(L \\subseteq \\Sigma^{\\ast}\\)
- 本書では自然言語ではなく、形式言語としての「文字列集合」を指すことが多い（→ [第3章: 形式言語とオートマトン理論](../chapter-3/index.md)）

**線形符号（Linear Code）**
- 符号語集合が有限体上の線形部分空間をなす誤り訂正符号
- 生成行列・検査行列・最小距離で扱いやすく、符号理論の基本となる（→ [第10章: 情報理論](../chapter-10/index.md)）

<a id="linearizability"></a>
**線形化可能性（Linearizability）**
- 並行オブジェクトの各操作が、呼出しと応答の間のどこか 1 点で瞬間的に効いたように見える正当性条件
- 並行実装を逐次仕様へ還元して考えるための中心概念（→ [第12章: 並行計算の理論](../chapter-12/index.md)）

<a id="ltl"></a>
**線形時相論理（LTL, Linear Temporal Logic）**
- 1 本の実行系列に沿って「常に」「いつか」などの時間的性質を記述する時相論理
- モデル検査や反応システム仕様で使われ、CTL と並ぶ代表的形式体系である（→ [第9章: 論理学と形式的手法](../chapter-9/index.md), [第12章: 並行計算の理論](../chapter-12/index.md)）

<a id="lock-free"></a>
**ロックフリー（Lock-Free）**
- 常に少なくとも 1 つのスレッドが有限ステップで前進できる進行保証
- 並行データ構造で wait-free より弱く、blocking lock より強い保証として使われる（→ [第12章: 並行計算の理論](../chapter-12/index.md)）

**線形探索 (Linear Search)**
- 配列を先頭から順番に探索するアルゴリズム
- 時間複雑性: O(n)

**対数時間 (Logarithmic Time)**
- 実行時間がO(log n)のアルゴリズム
- 二分探索等で実現

**最長共通部分列 (Longest Common Subsequence, LCS)**
- 2つの列の最長の共通部分列を求める問題
- 動的計画法で O(mn) で解ける

<a id="レムペル-ジブ-符号-lempel-ziv"></a>
**Lempel–Ziv 符号（LZ 符号）**
- 辞書ベースの可逆圧縮（LZ77, LZ78）。定常エルゴード情報源で漸近的最適性（→ [第10章: 情報理論](../chapter-10/index.md)）

<a id="レベルグラフ-level-graph"></a>
**レベルグラフ (Level Graph)**
- 残余グラフ上で s からの BFS 距離で層を分け、距離が1増える辺のみを残したグラフ
- Dinic のアルゴリズムでブロッキングフローを見つけるために用いる（→ [第8章: ネットワークフロー](../chapter-8/index.md)）

## M {#appendix-d-m}

**Master定理 (Master Theorem)**
- 分割統治アルゴリズムの漸化式を解く定理
- T(n) = aT(n/b) + f(n) の形の式に適用

**マッチング (Matching)**
- グラフにおいて、端点を共有しない辺の集合
- 二部グラフの最大マッチング問題

**メモ化 (Memoization)**
- 計算結果を保存して重複計算を避ける技法
- 動的計画法の実装手法

**マルチパーティ計算（Multi-Party Computation）**
- 複数参加者が各自の秘密入力を明かさずに、所望の関数値だけを共同計算する枠組み
- 秘密分散や回路評価と結び付き、プライバシー保護計算の基盤となる（→ [第11章: 暗号理論の数学的基礎](../chapter-11/index.md)）

**モデル検査（Model Checking）**
- システムの状態遷移モデルと論理式を入力として、仕様が成り立つかを機械的に判定する手法
- CTL/LTL、状態爆発、抽象化などの概念と結び付く（→ [第9章: 論理学と形式的手法](../chapter-9/index.md), [第12章: 並行計算の理論](../chapter-12/index.md)）

**最小カット (Minimum Cut)**
- ある s–t カット (S,T) のうち、容量 c(S,T) が最小のもの
- 最大フロー最小カット定理により、最大フロー値と等しい（→ [第8章: ネットワークフロー](../chapter-8/index.md)）

**最大フロー最小カット定理（Max-Flow Min-Cut Theorem）**
- フローネットワークで、s から t への最大フロー値が最小 s–t カット容量に等しいという定理
- フロー問題を構造定理として理解する基礎であり、マッチングや割当てへも応用される（→ [第8章: グラフ理論とネットワーク](../chapter-8/index.md)）

**Myhill–Nerode 定理（Myhill–Nerode Theorem）**
- 言語が正規であることと、右合同関係の同値類が有限であることが同値だと述べる定理
- DFA 最小化や非正規性の証明で中心的に使われる（→ [第3章: 形式言語とオートマトン理論](../chapter-3/index.md)）

## N {#appendix-d-n}

**非決定性 (Nondeterminism)**
- 複数の計算経路が可能な計算モデル
- NFA、非決定性チューリング機械

**NP完全 (NP-Complete)**
- NPクラスに属し、NPの任意の問題から多項式時間還元可能な問題
- SAT、クリーク問題、巡回セールスマン問題の決定版等
- 定義と例は第5章を参照（→ [第5章: 計算複雑性理論](../chapter-5/index.md)）

**非決定性有限オートマトン (Nondeterministic Finite Automaton, NFA)**
- 各状態・入力記号の組に対して複数の遷移先を持てるFA
- DFAと同等の認識能力

## O {#appendix-d-o}

**オラクル (Oracle)**
- ある問題を1ステップで解ける仮想的装置
- 相対化による複雑性理論の研究

**一方向関数（One-Way Function）**
- 順方向は効率的に計算できるが、像から原像を求めるのは計算的に困難と期待される関数
- 公開鍵暗号や擬似乱数生成器の理論的基盤となる（→ [第11章: 暗号理論の数学的基礎](../chapter-11/index.md)）

**最適化問題 (Optimization Problem)**
- 制約の下で目的関数を最小化/最大化する問題
- 決定問題の対比概念

## P {#appendix-d-p}

**多項式時間 (Polynomial Time)**
- 実行時間がO(n^k)（kは定数）のアルゴリズム
- 効率的に解けるとみなされる

**P vs NP問題 (P vs NP Problem)**
- P = NP か否かを問うミレニアム問題の一つ
- 理論計算機科学の最重要未解決問題

**永続的データ構造（Persistent Data Structure）**
- 更新後も過去版へアクセスできるよう、版管理を内包したデータ構造
- 部分永続・完全永続などの区別があり、関数型データ構造とも親和性が高い（→ [第7章: データ構造の理論](../chapter-7/index.md)）

**Petri ネット（Petri Net）**
- プレース、トランジション、トークンで並行システムの状態と資源制約を表すモデル
- 到達可能性、保存性、活性（liveness）などを解析できる（→ [第12章: 並行計算の理論](../chapter-12/index.md)）

**π計算（Pi-Calculus）**
- 通信路そのものを送受信できる移動性付きプロセス計算
- 動的トポロジをもつ分散システムやセッション型の基礎理論として重要（→ [第12章: 並行計算の理論](../chapter-12/index.md)）

**プッシュダウンオートマトン (Pushdown Automaton, PDA)**
- スタックを持つ有限オートマトン
- 文脈自由言語を認識

**公開鍵暗号（Public-Key Cryptography）**
- 暗号化鍵と復号鍵を分離し、公開鍵だけを配布できる暗号方式
- 鍵配送問題の解決、署名、鍵共有プロトコルの基盤となる（→ [第11章: 暗号理論の数学的基礎](../chapter-11/index.md)）

**疑似乱数生成器（Pseudorandom Generator）**
- 短い真の乱数種から、計算的には乱数と見分けにくい長い列を生成する仕組み
- ストリーム暗号、鍵導出、暗号理論の安全性定義と結び付く（→ [第11章: 暗号理論の数学的基礎](../chapter-11/index.md)）

**ポンピング補題（Pumping Lemma）**
- 言語のクラスに属さないことを証明する技法
- 正規言語、文脈自由言語にそれぞれ存在

<a id="接頭語符号-prefix-code"></a>
**接頭語符号（Prefix Code, 瞬時符号）**
- どの符号語も他の符号語の接頭辞でない符号（瞬時復号可能）
- クラフト–マクミランの不等式を満たす長さから構成可能（→ [第10章: 情報理論](../chapter-10/index.md)）

## Q {#appendix-d-q}

**クイックソート (Quicksort)**
- 分割統治による効率的ソートアルゴリズム
- 平均時間複雑性: O(n log n)

**キュー (Queue)**
- FIFO（先入れ先出し）データ構造
- 幅優先探索で使用

## R {#appendix-d-r}

**還元 (Reduction)**
- ある問題を別の問題に変換すること
- 計算可能性、複雑性の研究で重要
- 形式と用例は第5章を参照（→ [第5章: 計算複雑性理論](../chapter-5/index.md)）

**正規言語 (Regular Language)**
- 有限オートマトンで認識可能な言語
- 正規表現で表現可能

**正規表現 (Regular Expression)**
- 正規言語を表現する記法
- 文字列パターンマッチングで使用

**再帰 (Recursion)**
- 自分自身を呼び出すアルゴリズム設計技法
- 数学的帰納法と密接な関係

<a id="rice-の定理-rices-theorem"></a>
**Rice の定理 (Rice's Theorem)**
- チューリング機械が受理する言語 L(M) に関する任意の「非自明な」意味的性質 P に対して、\\(\\{\\,\\langle M\\rangle \\mid L(M) \\text{ が } P \\text{ を満たす}\\,\\}\\) は決定不能
- 非自明: P を満たす言語と満たさない言語が少なくとも1つずつ存在
- 対象は意味的性質のみ（内部構造・状態数など構文的性質は対象外）
- 典型例: 空言語性、有限性、正規性、ある語を含むか 等（いずれも決定不能）
- 参考: 第4章「Rice の定理」（→ [第4章: 計算可能性理論](../chapter-4/index.md)）

<a id="残余グラフ-residual-graph"></a>
**残余グラフ (Residual Graph)**
- 現在のフロー f に対して、使用可能な追加容量（順方向）と巻き戻し容量（逆方向）を表すグラフ G_f
- 増加路（augmenting path）の探索は残余グラフ上で行う（→ [第8章: ネットワークフロー](../chapter-8/index.md)）

<a id="残余ネットワーク-residual-network"></a>
**残余ネットワーク (Residual Network)**
- 残余グラフと同義。文献によって network/graph を使い分ける
- 辺の残余容量 c_f(u,v) に基づくネットワーク（→ 残余グラフ）

<a id="逆向き辺-reverse-edge"></a>
**逆向き辺 (Reverse Edge)**
- 残余グラフにおける (v,u) の辺。現在のフロー f(u,v) を巻き戻す余地を表し、残余容量は c_f(v,u) = f(u,v)
- 増加後の調整や循環の解消に用いられる（→ 第8章: ネットワークフロー）

<a id="残余容量-residual-capacity"></a>
**残余容量 (Residual Capacity)**
- 残余グラフ G_f の辺 (u,v) における利用可能容量 c_f(u,v)
- 順方向は未使用の余地、逆方向は既存フローの巻き戻し余地を表す

## S {#appendix-d-s}

**SAT問題 (Satisfiability Problem)**
- 論理式が充足可能かを判定する問題
- 最初に証明されたNP完全問題（→ [第5章: NP完全性（Cook–Levin）](../chapter-5/index.md)）

**最短路（Shortest Path）**
- グラフ上で 2 頂点間の総重みが最小となる路を求める問題
- BFS、ダイクストラ法、Bellman–Ford 法、Floyd–Warshall 法などの中心概念（→ [第8章: グラフ理論とネットワーク](../chapter-8/index.md)）

**SMT（Satisfiability Modulo Theories）**
- SAT を、整数算術・配列・ビットベクトルなどの理論付き充足可能性へ拡張した枠組み
- プログラム解析や形式検証で Z3 などのソルバが用いられる（→ [第9章: 論理学と形式的手法](../chapter-9/index.md)）

**最小全域木（Minimum Spanning Tree, MST）**
- 重み付き連結無向グラフの全頂点を結ぶ木のうち、辺重み総和が最小のもの
- Kruskal 法や Prim 法で求められ、ネットワーク設計の基本問題である（→ [第8章: グラフ理論とネットワーク](../chapter-8/index.md)）

**秘密分散（Secret Sharing）**
- 秘密情報を複数の断片に分け、所定数以上がそろったときだけ復元できるようにする手法
- Shamir の秘密分散が代表例で、MPC や鍵管理の基盤となる（→ [第11章: 暗号理論の数学的基礎](../chapter-11/index.md)）

**スキップリスト（Skip List）**
- 複数レベルの前方ポインタを確率的に持たせて探索を高速化する辞書データ構造
- 平均 O(log n) の探索・挿入・削除を簡潔な実装で実現する（→ [第7章: データ構造の理論](../chapter-7/index.md)）

**分離論理（Separation Logic）**
- ヒープや可変共有資源を局所的に記述するための Hoare 論理拡張
- `*`（separating conjunction）によりエイリアシングを扱いやすくする（→ [第9章: 論理学と形式的手法](../chapter-9/index.md)）

**順序整合性（Sequential Consistency）**
- 並行実行の結果が、各スレッドのプログラム順を保ったまま、何らかの逐次実行順として説明できる一貫性条件
- 線形化可能性より弱く、メモリモデルや共有メモリ並行性の議論で重要（→ [第12章: 並行計算の理論](../chapter-12/index.md)）

**集合 (Set)**
- 異なる要素の集まり
- 数学の基本概念

**スタック (Stack)**
- LIFO（後入れ先出し）データ構造
- 深さ優先探索、再帰で使用

**全射 (Surjection)**
- 値域のすべての要素が像に含まれる関数
- ∀b ∈ B, ∃a ∈ A, f(a) = b

## T {#appendix-d-t}

**時間複雑性 (Time Complexity)**
- アルゴリズムの実行時間の解析
- 入力サイズnの関数として表現

**時相論理（Temporal Logic）**
- 「常に」「いつか」「次に」といった時間的性質を論理式で記述する枠組み
- LTL/CTL により並行システムや反応系の性質を記述する（→ [第9章: 論理学と形式的手法](../chapter-9/index.md), [第12章: 並行計算の理論](../chapter-12/index.md)）

**時間オートマトン（Timed Automaton）**
- 有限オートマトンに実数値クロック制約を加えた実時間システムのモデル
- 到達可能性解析や UPPAAL のようなツールの理論基盤となる（→ [第12章: 並行計算の理論](../chapter-12/index.md)）

**チューリング還元 (Turing Reduction)**
- オラクルを用いた還元
- many-one還元より一般的

**木 (Tree)**
- サイクルのない連結グラフ
- データ構造、探索アルゴリズムで重要

## U {#appendix-d-u}

**和集合 (Union)**
- 2つの集合のいずれかに属する要素の集合
- \\(A \\cup B = \\{\\,x \\mid x \\in A \\lor x \\in B\\,\\}\\)

**Union-Find（Disjoint Set Union）**
- 要素集合を互いに素な部分集合へ分割して管理するデータ構造
- union by rank と path compression により、償却的にほぼ定数時間で操作できる（→ [第7章: データ構造の理論](../chapter-7/index.md)）

**全単射 (Bijection)**
- 単射かつ全射の関数
- 一対一対応

## V {#appendix-d-v}

**検証器 (Verifier)**
- 解候補の正当性を確認するアルゴリズム
- NP問題の定義で使用（→ [第5章: NPの検証的特徴付け](../chapter-5/index.md)）

**頂点被覆 (Vertex Cover)**
- グラフのすべての辺を被覆する頂点集合
- NP完全問題

## W {#appendix-d-w}

**最悪時間複雑性 (Worst-Case Time Complexity)**
- すべての入力に対する実行時間の上界
- アルゴリズム解析の基本指標

**最弱事前条件（Weakest Precondition）**
- ある事後条件を保証するために、プログラム実行前に必要な最も弱い条件
- Dijkstra のプログラム意味論や検証条件生成で中心的な概念（→ [第9章: 論理学と形式的手法](../chapter-9/index.md)）

**ウェイトフリー（Wait-Free）**
- すべてのスレッドが有限ステップで自分の操作を完了できる進行保証
- lock-free より強い保証であり、高競合下でも starvation を避けたい設計で重要（→ [第12章: 並行計算の理論](../chapter-12/index.md)）

## X {#appendix-d-x}

**XOR演算 (XOR Operation)**
- 排他的論理和、⊕記号で表記
- P ⊕ Q は P と Q の真偽値が異なるときのみ真

## Y {#appendix-d-y}

**なし**

## Z {#appendix-d-z}

**ゼロ知識証明 (Zero-Knowledge Proof)**
- 知識を明かすことなく知識の保有を証明する手法
- 完全性・健全性・ゼロ知識性の 3 要件で整理される
- NIZK や zk-SNARK などの発展形がある（→ [第11章: ゼロ知識証明](../chapter-11/index.md)）

---

## 記号索引 {#appendix-d-symbols}

### 論理記号
- ∧ (AND): 論理積
- ∨ (OR): 論理和  
- ¬ (NOT): 否定
- → (IMPLIES): 含意
- ↔ (IFF): 同値
- ∀ (FOR ALL): 全称量詞
- ∃ (EXISTS): 存在量詞

### 集合記号
- ∈ (IN): 要素の所属
- ⊆ (SUBSET): 部分集合
- ∪ (UNION): 和集合
- ∩ (intersection): 共通部分
- ∅ (EMPTY): 空集合
- × (CARTESIAN): 直積

### 複雑性記号
- O (BIG-O): 上界
- Ω (BIG-OMEGA): 下界
- Θ (BIG-THETA): 厳密な界
- o (LITTLE-O): 真の上界
- ω (LITTLE-OMEGA): 真の下界

### 形式言語記号
- Σ (SIGMA): アルファベット
- \\(\\Sigma^{\\ast}\\) (SIGMA-STAR): 文字列全体
- ε (EPSILON): 空文字列
- \\(\lvert w\rvert\\) (LENGTH): 文字列の長さ

### 関数記号
- \\(f: A \\to B\\): AからBへの関数
- dom(f): 定義域
- ran(f): 値域
- \\(f^{-1}\\): 逆関数
- \\(g \\circ f\\): 合成関数

### グラフ記号
- G = (V,E): グラフ
- \\(\lvert V\rvert\\): 頂点数
- \\(\lvert E\rvert\\): 辺数
- deg(v): 頂点vの次数
- d(u,v): 頂点間距離

---

この用語集は理論計算機科学の学習において頻繁に参照されることを想定しており、各用語の正確な定義と関連概念を効率的に確認できるよう構成されています。
