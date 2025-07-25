---
title: "第3章 形式言語とオートマトン理論"
subtitle: "正規言語から文脈自由言語まで"
description: "形式言語の階層と対応するオートマトンを学習"
chapter: 3
---

# 第3章 形式言語とオートマトン理論

## はじめに

形式言語理論は、プログラミング言語の構文解析、コンパイラ設計、文字列処理アルゴリズムなど、コンピュータサイエンスの多くの分野で基礎となる理論です。本章では、言語を認識する計算モデルであるオートマトンを、その計算能力に応じて階層的に学びます。

有限オートマトンから始まり、より強力なプッシュダウンオートマトンへと進むことで、計算モデルの能力と限界を体系的に理解します。各モデルが認識できる言語クラス（正規言語、文脈自由言語）の性質を詳しく調べ、実用的な応用への橋渡しをします。

## 3.1 形式言語

```mermaid
graph TD
    subgraph "形式言語の基本概念"
        subgraph "言語の構成要素"
            Alphabet["アルファベット Σ<br/>・記号の有限集合<br/>・例: {0,1}, {a,b,c}, {漢字}"]
            
            String["文字列 w<br/>・記号の有限列<br/>・長さ |w|<br/>・空文字列 ε"]
            
            Language["言語 L<br/>・文字列の集合<br/>・L ⊆ Σ*<br/>・無限集合も可能"]
        end
        
        subgraph "文字列の演算"
            Concatenation["連結 xy<br/>x の後に y を続ける<br/>|xy| = |x| + |y|<br/>単位元: ε"]
            
            Power["べき乗 wⁿ<br/>w⁰ = ε<br/>wⁿ⁺¹ = wⁿ w<br/>例: abc³ = abcabcabc"]
            
            Reverse["逆転 wᴿ<br/>w = a₁a₂...aₙ<br/>wᴿ = aₙ...a₂a₁<br/>例: abcᴿ = cba"]
        end
        
        subgraph "言語の演算"
            Union["L₁ ∪ L₂<br/>・和集合<br/>・「または」"]
            
            Concat2["L₁ L₂<br/>・連結<br/>・{xy | x ∈ L₁, y ∈ L₂}"]
            
            Kleene["L*<br/>・クリーネ閉包<br/>・0回以上の連結<br/>・L* = ⋃ₙ Lⁿ"]
            
            Plus["L⁺<br/>・正閉包<br/>・1回以上の連結<br/>・L⁺ = ⋃ₙ≥₁ Lⁿ"]
        end
        
        subgraph "例: L = {0, 11}"
            Examples["演算例<br/>L² = {00, 011, 110, 1111}<br/>L* = {ε, 0, 11, 00, 011, 110, ...}<br/>L⁺ = {0, 11, 00, 011, 110, ...}"]
        end
    end
    
    style Alphabet fill:#e3f2fd
    style String fill:#fff3e0
    style Language fill:#e8f5e8
    style Kleene fill:#f3e5f5
    style Examples fill:#ffe0b2
```

### 3.1.1 基本定義

**定義 3.1** **アルファベット**（alphabet）Σ は、記号の空でない有限集合である。

例：
- Σ₁ = {0, 1}（2進アルファベット）
- Σ₂ = {a, b, c, ..., z}（英小文字）
- Σ₃ = {0, 1, ..., 9, +, -, ×, ÷, (, )}（算術式の記号）

**定義 3.2** Σ 上の**文字列**（string）は、Σ の要素の有限列である。長さ 0 の文字列を**空文字列**（empty string）と呼び、ε で表す。

**記法**：
- |w|：文字列 w の長さ
- wᵢ：w の i 番目の文字（1 ≤ i ≤ |w|）
- Σ*：Σ 上のすべての文字列の集合
- Σ⁺：Σ 上の空でない文字列の集合（Σ⁺ = Σ* \ {ε}）
- Σⁿ：長さ n の文字列の集合

**定義 3.3** Σ 上の**言語**（language）は、Σ* の部分集合である。

### 3.1.2 文字列の演算

**定義 3.4** 文字列の基本演算：

1. **連結**（concatenation）：文字列 x, y の連結 xy は、x の後に y を続けた文字列
   - 性質：|xy| = |x| + |y|
   - 単位元：xε = εx = x

2. **冪乗**：wⁿ = ww...w（n 個の w の連結）
   - w⁰ = ε
   - wⁿ⁺¹ = wⁿw

3. **逆転**（reversal）：w = a₁a₂...aₙ の逆転 wᴿ = aₙ...a₂a₁
   - εᴿ = ε
   - (xy)ᴿ = yᴿxᴿ

4. **部分文字列**：v が w の部分文字列 ⟺ ∃x, y ∈ Σ*, w = xvy
   - **接頭辞**（prefix）：w = xv となる x
   - **接尾辞**（suffix）：w = vx となる x

### 3.1.3 言語の演算

**定義 3.5** 言語 L₁, L₂ ⊆ Σ* に対する演算：

1. **和集合**：L₁ ∪ L₂ = {w | w ∈ L₁ ∨ w ∈ L₂}
2. **積集合**：L₁ ∩ L₂ = {w | w ∈ L₁ ∧ w ∈ L₂}
3. **補集合**：L̄ = Σ* \ L
4. **連結**：L₁L₂ = {xy | x ∈ L₁ ∧ y ∈ L₂}
5. **冪乗**：
   - L⁰ = {ε}
   - Lⁿ⁺¹ = LⁿL
6. **クリーネ閉包**：L* = ⋃ₙ₌₀^∞ Lⁿ
7. **正閉包**：L⁺ = ⋃ₙ₌₁^∞ Lⁿ

**例 3.1** L = {0, 11} のとき：
- L² = {00, 011, 110, 1111}
- L* = {ε, 0, 11, 00, 011, 110, 1111, ...}

### 3.1.4 形式言語の実用的応用

**計算機科学における形式言語の応用**：

1. **プログラミング言語の設計**：
   - **字句解析**：正規表現によるトークン識別
   - **構文解析**：文脈自由文法による構文構造の解析
   - **意味解析**：属性文法による型検査と意味規則

2. **文字列処理と検索**：
   - **正規表現エンジン**：パターンマッチングとテキスト処理
   - **データベース検索**：クエリ言語の解析
   - **バイオインフォマティクス**：DNA配列のパターン検索

3. **ネットワークとセキュリティ**：
   - **プロトコル仕様**：通信プロトコルの状態遷移
   - **ファイアウォール**：パケットフィルタリングルール
   - **ウイルス検出**：マルウェアの署名パターン

**具体例：メールアドレスの検証**
```python
# 正規表現による形式検証
import re

def validate_email(email):
    # 簡略化されたメールアドレスのパターン
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

# 対応する形式言語
# L_email = {文字列 w | w は有効なメールアドレス形式}
# 
# この言語は以下の形式で表現できる：
# L_email = L_local @ L_domain . L_tld
# 
# ここで：
# - L_local: ローカル部分の文字列集合
# - L_domain: ドメイン部分の文字列集合  
# - L_tld: トップレベルドメインの文字列集合
```

**プログラミング言語での字句解析例**：
```python
# Python風の字句解析器の概念
class Token:
    def __init__(self, type, value, line, column):
        self.type = type
        self.value = value
        self.line = line
        self.column = column

# 各トークンに対応する正規表現
token_patterns = {
    'NUMBER': r'\d+(\.\d+)?',           # 数値
    'IDENTIFIER': r'[a-zA-Z_][a-zA-Z0-9_]*',  # 識別子
    'KEYWORD': r'(if|else|while|for|def|return)',  # キーワード
    'OPERATOR': r'[+\-*/=<>!]+',        # 演算子
    'DELIMITER': r'[(){}[\],;:]',       # 区切り文字
    'WHITESPACE': r'\s+',               # 空白
    'COMMENT': r'#.*',                  # コメント
}

# 対応する形式言語
# L_program = (L_number ∪ L_identifier ∪ L_keyword ∪ L_operator ∪ L_delimiter ∪ L_whitespace ∪ L_comment)*
```

## 3.2 有限オートマトン

```mermaid
graph TD
    subgraph "有限オートマトンの種類と特徴"
        subgraph "DFA（決定性有限オートマトン）"
            DFA_Def["M = (Q, Σ, δ, q₀, F)<br/>・Q: 状態集合<br/>・Σ: 入力アルファベット<br/>・δ: Q × Σ → Q<br/>・q₀: 初期状態<br/>・F: 受理状態集合"]
            
            DFA_Features["特徴<br/>・各状態で各入力に対し<br/>て唯一の遷移先<br/>・決定的な計算<br/>・効率的な実装"]
            
            DFA_Example["例: 0の個数が偶数<br/>q₀: 偶数個(受理)<br/>q₁: 奇数個<br/>δ(q₀,0)=q₁, δ(q₀,1)=q₀<br/>δ(q₁,0)=q₀, δ(q₁,1)=q₁"]
        end
        
        subgraph "NFA（非決定性有限オートマトン）"
            NFA_Def["M = (Q, Σ, δ, q₀, F)<br/>・δ: Q × Σ → P(Q)<br/>・非決定的選択<br/>・並行計算パス"]
            
            NFA_Features["特徴<br/>・複数の遷移先可能<br/>・推測による計算<br/>・コンパクトな表現"]
            
            NFA_Example["例: 末尾から3番目が1<br/>・推測: 今の1が末尾から3番目<br/>・3文字先の文字列終端で受理"]
        end
        
        subgraph "ε-NFA"
            EpsilonNFA["ε-遷移付きNFA<br/>・空文字列での遷移<br/>・δ: Q × (Σ ∪ {ε}) → P(Q)<br/>・ECLOSE(ε閉包)で処理"]
            
            EpsilonFeatures["使用例<br/>・正規表現からの変換<br/>・複数のオートマトンの結合<br/>・構成的な設計"]
        end
        
        subgraph "等価性と変換"
            Equivalence["計算能力の等価性<br/>DFA ≡ NFA ≡ ε-NFA<br/>・部分集合構成法<br/>・状態爆発の可能性"]
            
            Conversion["変換アルゴリズム<br/>NFA → DFA: 部分集合構成<br/>ε-NFA → NFA: ε閉包計算<br/>DFA 最小化: 等価状態結合"]
        end
    end
    
    style DFA_Def fill:#e3f2fd
    style NFA_Def fill:#fff3e0
    style EpsilonNFA fill:#f3e5f5
    style Equivalence fill:#e8f5e8
    style DFA_Example fill:#ffe0b2
```

### 3.2.1 決定性有限オートマトン（DFA）

**定義 3.6** **決定性有限オートマトン**（Deterministic Finite Automaton, DFA）は5つ組 M = (Q, Σ, δ, q₀, F) である。ここで：
- Q：状態の有限集合
- Σ：入力アルファベット
- δ: Q × Σ → Q：遷移関数
- q₀ ∈ Q：初期状態
- F ⊆ Q：受理状態の集合

**定義 3.7** DFA M の**拡張遷移関数** δ̂: Q × Σ* → Q を帰納的に定義：
- δ̂(q, ε) = q
- δ̂(q, wa) = δ(δ̂(q, w), a)（w ∈ Σ*, a ∈ Σ）

**定義 3.8** DFA M が文字列 w を**受理する**とは、δ̂(q₀, w) ∈ F であること。
M が認識する言語：L(M) = {w ∈ Σ* | δ̂(q₀, w) ∈ F}

**例 3.2** 0 の個数が偶数である2進文字列を認識する DFA

M = ({q₀, q₁}, {0, 1}, δ, q₀, {q₀}) where:
- δ(q₀, 0) = q₁, δ(q₀, 1) = q₀
- δ(q₁, 0) = q₀, δ(q₁, 1) = q₁

![偶数個の0を認識するDFA](../../assets/images/diagrams/ch3_even_zeros_automaton.svg)

状態の意味：
- q₀：これまでに読んだ0の個数が偶数（受理状態）
- q₁：これまでに読んだ0の個数が奇数

### 3.2.2 非決定性有限オートマトン（NFA）

**定義 3.9** **非決定性有限オートマトン**（Nondeterministic Finite Automaton, NFA）は5つ組 M = (Q, Σ, δ, q₀, F) である。ここで：
- Q, Σ, q₀, F は DFA と同じ
- δ: Q × Σ → P(Q)：遷移関数（P(Q) は Q の冪集合）

**定義 3.10** NFA M の拡張遷移関数 δ̂: Q × Σ* → P(Q)：
- δ̂(q, ε) = {q}
- δ̂(q, wa) = ⋃ᵣ∈δ̂(q,w) δ(r, a)

状態集合への拡張：δ̂(R, w) = ⋃q∈R δ̂(q, w)（R ⊆ Q）

**定義 3.11** NFA M が w を受理 ⟺ δ̂(q₀, w) ∩ F ≠ ∅

**例 3.3** 末尾から3番目の文字が1である2進文字列を認識する NFA

直観的に、「今読んでいる文字が末尾から3番目の1である」と「推測」する。

M = ({q₀, q₁, q₂, q₃}, {0, 1}, δ, q₀, {q₃}) where:
- δ(q₀, 0) = {q₀}, δ(q₀, 1) = {q₀, q₁}
- δ(q₁, 0) = {q₂}, δ(q₁, 1) = {q₂}
- δ(q₂, 0) = {q₃}, δ(q₂, 1) = {q₃}
- δ(q₃, 0) = ∅, δ(q₃, 1) = ∅

### 3.2.3 ε-NFA

**定義 3.12** **ε-NFA** は、空文字列 ε での遷移を許す NFA である。
遷移関数：δ: Q × (Σ ∪ {ε}) → P(Q)

**定義 3.13** 状態 q の**ε-閉包** ECLOSE(q)：
ECLOSE(q) = {p | q から p へ ε 遷移のみで到達可能}

集合への拡張：ECLOSE(R) = ⋃q∈R ECLOSE(q)

**例 3.4** ε-NFA から通常の NFA への変換

ε-NFA の遷移関数 δ から、等価な NFA の遷移関数 δ' を構成：
δ'(q, a) = ECLOSE(⋃ᵣ∈ECLOSE(q) δ(r, a))

### 3.2.4 DFAとNFAの等価性

**定理 3.1** すべての NFA に対して、同じ言語を認識する DFA が存在する。

*証明*（部分集合構成法）：
NFA N = (Qₙ, Σ, δₙ, q₀, Fₙ) から DFA D = (Qᴅ, Σ, δᴅ, q₀ᴅ, Fᴅ) を構成：
- Qᴅ = P(Qₙ)（N の状態集合の冪集合）
- q₀ᴅ = {q₀}
- Fᴅ = {R ⊆ Qₙ | R ∩ Fₙ ≠ ∅}
- δᴅ(R, a) = ⋃q∈R δₙ(q, a)

帰納法により、δ̂ᴅ({q₀}, w) = δ̂ₙ(q₀, w) が示される。
したがって、L(D) = L(N)。□

**注意**：状態数は最悪の場合指数的に増加する（|Qᴅ| ≤ 2^|Qₙ|）。

## 3.3 正規言語

```mermaid
graph TD
    subgraph "正規言語と正規表現"
        subgraph "正規表現の構成"
            Basics["基本要素<br/>・∅: 空言語<br/>・ε: 空文字列<br/>・a: 単一記号"]
            
            Operations["演算<br/>・R₁ + R₂: 和集合<br/>・R₁R₂: 連結<br/>・R*: クリーネ閉包"]
            
            Priority["優先順位<br/>1. * (閉包)<br/>2. 連結<br/>3. + (和)"]
            
            Extensions["拡張記法<br/>・R+: 正閉包 (RR*)<br/>・R?: オプション (R + ε)<br/>・[abc]: 文字クラス"]
        end
        
        subgraph "正規表現の例"
            Examples1["基本例<br/>(0+1)*: 全て2進文字列<br/>0*10*: ちょうど1つの1<br/>(0+1)*11(0+1)*: 11を含む"]
            
            Examples2["実用例<br/>[a-z]+: 英小文字<br/>[0-9]+: 数字<br/>a*b+c?: a後にb、任意c"]
        end
        
        subgraph "Kleeneの定理"
            Kleene["等価性の定理<br/>正規表現 ≡ DFA ≡ NFA"]
            
            Direction1["正規表現 → NFA<br/>・Thompsonの構成法<br/>・帰納的にオートマトン構築<br/>・ε-遷移を使用"]
            
            Direction2["DFA → 正規表現<br/>・状態消去法<br/>・Ardenの補題<br/>・連立方程式解法"]
        end
        
        subgraph "正規言語の性質"
            Closure["閉包性<br/>・和集合 ∪<br/>・積集合 ∩<br/>・補集合 ¯<br/>・連結 ・<br/>・クリーネ閉包 *"]
            
            Decidable["決定可能問題<br/>・所属問題: w ∈ L?<br/>・空問題: L = ∅?<br/>・有限性: Lは有限?<br/>・等価性: L₁ = L₂?"]
            
            Pumping["正規言語の限界<br/>Pumping補題<br/>・十分長い文字列にループ<br/>・繰り返し可能な部分"]
        end
    end
    
    style Basics fill:#e3f2fd
    style Examples1 fill:#fff3e0
    style Kleene fill:#e8f5e8
    style Closure fill:#f3e5f5
    style Pumping fill:#ffebee
```

### 3.3.1 正規表現

**定義 3.14** アルファベット Σ 上の**正規表現**（regular expression）を帰納的に定義：
1. ∅ は正規表現（言語 ∅ を表す）
2. ε は正規表現（言語 {ε} を表す）
3. a ∈ Σ に対して、a は正規表現（言語 {a} を表す）
4. R₁, R₂ が正規表現なら、以下も正規表現：
   - (R₁ + R₂)：和集合 L(R₁) ∪ L(R₂) を表す
   - (R₁R₂)：連結 L(R₁)L(R₂) を表す
   - (R₁)*：クリーネ閉包 L(R₁)* を表す

**記法の簡略化**：
- 括弧の省略：優先順位は * > 連結 > +
- R⁺ = RR*
- R? = R + ε（0回または1回）

**例 3.5** 正規表現と言語：
- (0+1)*：すべての2進文字列
- 0*10*：ちょうど1つの1を含む2進文字列
- (0+1)*11(0+1)*：部分文字列として11を含む
- ((0+1)(0+1))*：偶数長の2進文字列

### 3.3.2 正規言語の特徴付け

**定理 3.2**（Kleeneの定理）言語 L について、以下は同値：
1. L は正規表現で表される
2. L は DFA で認識される
3. L は NFA で認識される

*証明の概要*：
(1)→(3)：正規表現から NFA を帰納的に構成
- 基底：∅, ε, a に対する NFA は自明
- 帰納：和集合、連結、クリーネ閉包に対する構成法

(3)→(2)：定理3.1（部分集合構成法）

(2)→(1)：状態消去法またはArdenの補題を使用□

### 3.3.3 正規言語の閉包性

**定理 3.3** 正規言語は以下の演算に関して閉じている：
1. 和集合
2. 積集合
3. 補集合
4. 連結
5. クリーネ閉包
6. 差集合
7. 対称差

*証明*（積集合の場合）：
L₁ を認識する DFA M₁ = (Q₁, Σ, δ₁, q₁, F₁)
L₂ を認識する DFA M₂ = (Q₂, Σ, δ₂, q₂, F₂)

積オートマトン M = (Q₁ × Q₂, Σ, δ, (q₁, q₂), F₁ × F₂) を構成：
δ((p, q), a) = (δ₁(p, a), δ₂(q, a))

帰納法により、δ̂((q₁, q₂), w) = (δ̂₁(q₁, w), δ̂₂(q₂, w)) が示される。
したがって、L(M) = L₁ ∩ L₂。□

### 3.3.4 正規言語の判定問題

**定理 3.4** 正規言語に対する以下の問題は決定可能：
1. **所属問題**：w ∈ L?
2. **空問題**：L = ∅?
3. **有限性問題**：L は有限？
4. **等価性問題**：L₁ = L₂?

*証明*（等価性問題）：
L₁ = L₂ ⟺ (L₁ \ L₂) ∪ (L₂ \ L₁) = ∅
正規言語の閉包性より (L₁ \ L₂) ∪ (L₂ \ L₁) も正規言語。
空問題が決定可能なので、等価性も決定可能。□

## 3.4 正規言語の限界

```mermaid
graph TD
    subgraph "正規言語のPumping補題と限界"
        subgraph "Pumping補題の内容"
            Statement["正規言語Lに対し<br/>pumping length pが存在<br/>|s| ≥ pなs ∈ Lに対し<br/>s = xyzと分解可能"]
            
            Conditions["条件<br/>1. |xy| ≤ p<br/>2. |y| > 0<br/>3. ∀i ≥ 0, xyⁱz ∈ L"]
            
            Intuition["直観的理解<br/>・長い文字列にはループが存在<br/>・ループ部分は繰り返し可能<br/>・鳩の巣原理の応用"]
        end
        
        subgraph "証明の概略"
            DFABased["正規言語→DFAが存在<br/>状態数をpとする<br/>|s| ≥ pなら状態重複必発"]
            
            StateSequence["状態列 r₀, r₁, ..., rₚ<br/>鳩の巣原理でrⱼ = rₖ<br/>0 ≤ j < k ≤ p"]
            
            Decomposition["分解の構成<br/>x = a₁...aⱼ<br/>y = aⱼ₊₁...aₖ<br/>z = aₖ₊₁...aₙ"]
            
            Loop["ループの特徴<br/>y部分は状態ループを形成<br/>任意回数繰り返し可能"]
        end
        
        subgraph "非正規言語の例"
            Example1["{0ⁿ1ⁿ | n ≥ 0}<br/>証明: s = 0ᵖ 1ᵖ<br/>yは0のみから構成<br/>xy²zで個数が不一致"]
            
            Example2["{ww | w ∈ {0,1}*}<br/>証明: 前半部でpumping<br/>後半部と不一致"]
            
            Example3["{0ⁿ² | n ≥ 0}<br/>証明: 平方数の間隔<br/>等差数列ではない"]
        end
        
        subgraph "Myhill-Nerodeの定理"
            MN_Theorem["正規言語の特徴付け<br/>Lが正規 ⇔ 右同値類が有限"]
            
            RightCongruence["右同値関係<br/>x ≡ₗ y ⇔ ∀z, xz ∈ L ⇔ yz ∈ L<br/>「区別不可能」な文字列"]
            
            Applications["応用<br/>・最小状態数の下界<br/>・DFA最小化の理論<br/>・正規性の判定"]
        end
    end
    
    style Statement fill:#fff3e0
    style Conditions fill:#e3f2fd
    style Example1 fill:#ffebee
    style MN_Theorem fill:#e8f5e8
    style Applications fill:#f3e5f5
```

### 3.4.1 Pumping補題

**定理 3.5**（正規言語のPumping補題）
L が正規言語ならば、ある正整数 p（pumping length）が存在して、
|s| ≥ p なる任意の s ∈ L は以下を満たす分解 s = xyz を持つ：
1. |xy| ≤ p
2. |y| > 0
3. すべての i ≥ 0 に対して xyⁱz ∈ L

*証明*：L を認識する DFA を M = (Q, Σ, δ, q₀, F) とし、p = |Q| とする。
|s| ≥ p なる s ∈ L を考える。s = a₁a₂...aₙ（n ≥ p）とする。

状態列 r₀, r₁, ..., rₙ を以下のように定義：
- r₀ = q₀
- rᵢ₊₁ = δ(rᵢ, aᵢ₊₁)

鳩の巣原理より、r₀, r₁, ..., rₚ の中に同じ状態が存在。
rⱼ = rₖ（0 ≤ j < k ≤ p）とすると、s = xyz と分解できる：
- x = a₁...aⱼ
- y = aⱼ₊₁...aₖ  
- z = aₖ₊₁...aₙ

このとき：
1. |xy| = k ≤ p
2. |y| = k - j > 0  
3. δ̂(q₀, x) = rⱼ = rₖ = δ̂(q₀, xy) なので、y の部分はループを形成し、任意の i ≥ 0 に対して δ̂(q₀, xyⁱz) ∈ F となる。したがって xyⁱz ∈ L。□

### 3.4.2 非正規言語の例

**例 3.6** L = {0ⁿ1ⁿ | n ≥ 0} は正規言語でない。

*証明*（Pumping補題の対偶を使用）：
L が正規言語と仮定し、pumping length を p とする。
s = 0ᵖ1ᵖ を考える。|s| = 2p ≥ p なので、s = xyz と分解できる。

条件 |xy| ≤ p より、y は 0 のみからなる。y = 0ᵏ（k > 0）とする。
すると xy²z = 0ᵖ⁺ᵏ1ᵖ ∉ L となり、矛盾。□

**例 3.7** 以下の言語も非正規：
1. {ww | w ∈ {0,1}*}
2. {0ⁿ² | n ≥ 0}
3. {w ∈ {0,1}* | w は回文}

### 3.4.3 Myhill-Nerodの定理

**定義 3.15** 言語 L に対して、文字列 x, y の**識別可能性**：
x ≡ₗ y ⟺ ∀z ∈ Σ*, (xz ∈ L ⟺ yz ∈ L)

≡ₗ は同値関係であり、その同値類を L の**右同値類**という。

**定理 3.6**（Myhill-Nerodの定理）
言語 L が正規言語 ⟺ ≡ₗ の同値類の個数が有限

*証明*（⇒）：L を認識する DFA M = (Q, Σ, δ, q₀, F) が存在。
x ≡ₘ y ⟺ δ̂(q₀, x) = δ̂(q₀, y) と定義すると、≡ₘ は有限個の同値類を持つ。
x ≡ₘ y ならば x ≡ₗ y が示せるので、≡ₗ も有限個の同値類を持つ。

（⇐）：≡ₗ の同値類を状態とする DFA を構成できる。□

## 3.5 文脈自由言語

```mermaid
graph TD
    subgraph "文脈自由言語と文法"
        subgraph "文脈自由文法(CFG)"
            CFG_Def["G = (V, Σ, R, S)<br/>・V: 変数(非終端記号)<br/>・Σ: 終端記号<br/>・R: 生成規則 A → α<br/>・S: 開始記号"]
            
            Production["生成規則の例<br/>S → 0S1 | ε<br/>・0ⁿ1ⁿを生成<br/>・再帰的構造"]
            
            Derivation["導出過程<br/>直接導出: uAv ⇒ uαv<br/>導出: ⇒*の反射推移閉包<br/>左導出、右導出"]
        end
        
        subgraph "導出木と曖昧性"
            ParseTree["導出木の構造<br/>・根: 開始記号<br/>・内部ノード: 変数<br/>・葉: 終端記号またはε"]
            
            Ambiguity["曖昧性の問題<br/>同じ文字列に複数の導出木<br/>例: a+a×aの解釈<br/>優先順位で解決"]
            
            LeftmostRightmost["導出の種類<br/>左導出: 最左の変数を展開<br/>右導出: 最右の変数を展開<br/>構文解析で重要"]
        end
        
        subgraph "標準形"
            CNF["Chomsky標準形(CNF)<br/>A → BC (変数→2個)<br/>A → a (終端記号)<br/>S → ε (特別な場合)"]
            
            GNF["Greibach標準形(GNF)<br/>A → aα<br/>終端記号で始まる<br/>左再帰の除去"]
            
            Conversion["変換アルゴリズム<br/>1. ε-規則の除去<br/>2. 単位規則の除去<br/>3. 無用記号の除去<br/>4. 規則の分解"]
        end
        
        subgraph "CFGのPumping補題"
            CFL_Pumping["文脈自由言語のPumping補題<br/>十分長いs ∈ Lに対し<br/>s = uvxyzと分解<br/>uvⁱxyⁱz ∈ L (∀i ≥ 0)"]
            
            CFL_Conditions["条件<br/>1. |vxy| ≤ p<br/>2. |vy| > 0<br/>3. vとyを同時にpumping"]
            
            CFL_Example["非文脈自由言語<br/>{aⁿbⁿcⁿ | n ≥ 0}<br/>3種類の文字の個数が等しい<br/>2種類しかpumping不可"]
        end
    end
    
    style CFG_Def fill:#e3f2fd
    style ParseTree fill:#fff3e0
    style CNF fill:#e8f5e8
    style CFL_Pumping fill:#f3e5f5
    style CFL_Example fill:#ffebee
```

### 3.5.1 文脈自由文法

**定義 3.16** **文脈自由文法**（Context-Free Grammar, CFG）は4つ組 G = (V, Σ, R, S) である：
- V：変数（非終端記号）の有限集合
- Σ：終端記号の有限集合（V ∩ Σ = ∅）
- R：生成規則の有限集合。各規則は A → α の形（A ∈ V, α ∈ (V ∪ Σ)*）
- S ∈ V：開始記号

**定義 3.17** **導出**（derivation）：
- 直接導出：uAv ⇒ uαv if A → α ∈ R
- 導出：⇒* は ⇒ の反射推移閉包
- 左導出：常に最左の変数を展開
- 右導出：常に最右の変数を展開

**定義 3.18** CFG G が生成する言語：
L(G) = {w ∈ Σ* | S ⇒* w}

**例 3.8** 言語 {0ⁿ1ⁿ | n ≥ 0} を生成する CFG：
G = ({S}, {0, 1}, {S → 0S1, S → ε}, S)

導出例：S ⇒ 0S1 ⇒ 00S11 ⇒ 000S111 ⇒ 000111

### 3.5.2 導出木と曖昧性

**定義 3.19** CFG G の**導出木**（derivation tree）は以下を満たす順序木：
1. 各内部節点は変数でラベル付け
2. 各葉は終端記号または ε でラベル付け
3. 根は開始記号でラベル付け
4. 内部節点 A の子が B₁, ..., Bₖ なら A → B₁...Bₖ ∈ R

**定義 3.20** CFG G が**曖昧**（ambiguous）⟺ 
ある w ∈ L(G) に対して複数の導出木が存在

**例 3.9** 曖昧な文法：
G: E → E + E | E × E | (E) | a

文字列 "a + a × a" に対する2つの導出木：
1. E → E + E → a + E → a + E × E → a + a × a
2. E → E × E → E + E × E → a + E × E → a + a × E → a + a × a

### 3.5.3 文脈自由言語の標準形

**定義 3.21** **Chomsky標準形**（CNF）：すべての生成規則が以下の形：
- A → BC（A, B, C ∈ V）
- A → a（A ∈ V, a ∈ Σ）
- S → ε（S が右辺に現れない場合のみ）

**定理 3.7** すべての CFG は等価な CNF に変換できる。

*変換アルゴリズム*：
1. ε-規則の除去（S → ε 以外）
2. 単位規則（A → B）の除去
3. 無用な記号の除去
4. 長い規則の分解
5. 終端記号の分離

**定義 3.22** **Greibach標準形**（GNF）：すべての生成規則が以下の形：
A → aα（A ∈ V, a ∈ Σ, α ∈ V*）

### 3.5.4 CFGのPumping補題

**定理 3.8**（文脈自由言語のPumping補題）
L が文脈自由言語ならば、ある正整数 p が存在して、
|s| ≥ p なる任意の s ∈ L は以下を満たす分解 s = uvxyz を持つ：
1. |vxy| ≤ p
2. |vy| > 0
3. すべての i ≥ 0 に対して uvⁱxyⁱz ∈ L

*証明の概要*：CNF の文法を考え、十分長い文字列の導出木は深くなる。
鳩の巣原理により、ある変数が経路上に2回現れる。
その部分木の構造から、pumping が可能であることが示される。□

**例 3.10** L = {aⁿbⁿcⁿ | n ≥ 0} は文脈自由言語でない。

*証明*：pumping length を p とし、s = aᵖbᵖcᵖ を考える。
s = uvxyz と分解したとき、|vxy| ≤ p より、vxy は高々2種類の文字を含む。
したがって、uv²xy²z では3種類の文字の個数が等しくならない。□

## 3.6 プッシュダウンオートマトン

```mermaid
graph TD
    subgraph "プッシュダウンオートマトンの構造と機能"
        subgraph "PDAの基本構造"
            PDA_Def["P = (Q, Σ, Γ, δ, q₀, Z₀, F)<br/>・Q: 状態集合<br/>・Σ: 入力アルファベット<br/>・Γ: スタックアルファベット<br/>・δ: Q×(Σ∪{ε})×Γ → P_finite(Q×Γ*)<br/>・q₀: 初期状態<br/>・Z₀: 初期スタック記号<br/>・F: 受理状態集合"]
            
            Components["構成要素<br/>・有限制御部(状態)<br/>・入力テープ(読み取り専用)<br/>・スタック(無限記憶域)"]
            
            StackOps["スタック操作<br/>・push: データを積む<br/>・pop: データを取り出す<br/>・LIFO(Last In, First Out)"]
        end
        
        subgraph "瞬時記述と遷移"
            ID["瞬時記述(ID)<br/>(q, w, α) ∈ Q × Σ* × Γ*<br/>・q: 現在状態<br/>・w: 未読入力<br/>・α: スタック内容"]
            
            Transition["遷移関係 ⊢<br/>(q, aw, Zα) ⊢ (p, w, βα)<br/>if (p, β) ∈ δ(q, a, Z)<br/>・Zをポップしてβをプッシュ"]
            
            Nondeterminism["非決定性<br/>・複数の選択肢可能<br/>・ε-遷移可能<br/>・推測による計算"]
        end
        
        subgraph "受理方式"
            FinalState["最終状態による受理<br/>L(P) = {w | (q₀,w,Z₀) ⊢* (q,ε,α), q ∈ F}<br/>・入力を全て読み終えた時に<br/>受理状態にいる"]
            
            EmptyStack["空スタックによる受理<br/>N(P) = {w | (q₀,w,Z₀) ⊢* (q,ε,ε)}<br/>・入力を全て読み終えた時に<br/>スタックが空"]
            
            Equivalence["受理方式の等価性<br/>最終状態受理 ≡ 空スタック受理<br/>相互変換アルゴリズムが存在"]
        end
        
        subgraph "CFGとPDAの等価性"
            Theorem["基本定理<br/>文脈自由言語 ≡ PDAで受理される言語"]
            
            CFG_to_PDA["CFG → PDA<br/>スタックで左導出をシミュレート<br/>1. 初期記号をプッシュ<br/>2. 変数を生成規則で展開<br/>3. 終端記号をマッチング"]
            
            PDA_to_CFG["PDA → CFG<br/>変数[q,A,p]で表現<br/>・状態qでスタックトップAから<br/>状態pでAを除去する過程"]
        end
    end
    
    style PDA_Def fill:#e3f2fd
    style Components fill:#fff3e0
    style ID fill:#e8f5e8
    style FinalState fill:#f3e5f5
    style Theorem fill:#ffe0b2
```

### 3.6.1 PDAの定義

**定義 3.23** **プッシュダウンオートマトン**（PDA）は7つ組 P = (Q, Σ, Γ, δ, q₀, Z₀, F)：
- Q：状態の有限集合
- Σ：入力アルファベット
- Γ：スタックアルファベット
- δ: Q × (Σ ∪ {ε}) × Γ → P(Q × Γ*)：遷移関数（Pは冪集合、有限部分集合のみを返す）
- q₀ ∈ Q：初期状態
- Z₀ ∈ Γ：初期スタック記号
- F ⊆ Q：受理状態の集合

**定義 3.24** PDA の**瞬時記述**（ID）：(q, w, α) ∈ Q × Σ* × Γ*
- q：現在の状態
- w：未読の入力
- α：スタックの内容（左端がトップ）

**定義 3.25** 1ステップ遷移 ⊢：
(q, aw, Zα) ⊢ (p, w, βα) if (p, β) ∈ δ(q, a, Z)

### 3.6.2 PDAの受理方式

**定義 3.26** PDAの2つの受理方式：
1. **最終状態による受理**：L(P) = {w | (q₀, w, Z₀) ⊢* (q, ε, α), q ∈ F}
2. **空スタックによる受理**：N(P) = {w | (q₀, w, Z₀) ⊢* (q, ε, ε)}

**定理 3.9** 最終状態受理と空スタック受理は等価である。

### 3.6.3 CFGとPDAの等価性

**定理 3.10** 言語 L について、以下は同値：
1. L は文脈自由言語
2. L は PDA で受理される

*証明の概要*：
(1)→(2)：CFG から PDA を構成。スタックを使って左導出をシミュレート。

(2)→(1)：PDA から CFG を構成。変数 [q, A, p] は「状態 q でスタックトップ A から始めて、スタックトップを取り除いて状態 p に至る」ことを表す。□

## 3.7 文脈自由言語の性質

```mermaid
graph TD
    subgraph "文脈自由言語の性質と限界"
        subgraph "閉包性"
            Closed["閉じている演算<br/>・和集合 ∪<br/>・連結 ・<br/>・クリーネ閉包 *<br/>・正規言語との積集合 ∩"]
            
            NotClosed["閉じていない演算<br/>・積集合 ∩<br/>・補集合 ¯<br/>・差集合 \\"]
            
            CounterExample["反例<br/>L₁ = {aⁿbⁿcᵐ | n,m ≥ 0}<br/>L₂ = {aᵐbⁿcⁿ | n,m ≥ 0}<br/>L₁, L₂は文脈自由だが<br/>L₁ ∩ L₂ = {aⁿbⁿcⁿ | n ≥ 0}は非文脈自由"]
        end
        
        subgraph "決定問題"
            Decidable["決定可能問題<br/>・所属問題: w ∈ L?<br/>　CYKアルゴリズム O(n³|G|)<br/>・空問題: L = ∅?<br/>・有限性問題: Lは有限?"]
            
            Undecidable["決定不能問題<br/>・等価性問題: L₁ = L₂?<br/>・包含問題: L₁ ⊆ L₂?<br/>・曖昧性問題: CFGは曖昧?"]
            
            CYK["構文解析アルゴリズム<br/>CYK(Cocke-Younger-Kasami)<br/>・CNFを使用<br/>・動的計画法<br/>・O(n³)時間"]
        end
        
        subgraph "決定性文脈自由言語"
            DPDA["決定性PDA(DPDA)<br/>・各構成で高々一つの遷移<br/>・受理条件の制約<br/>・LR(k)文法と関連"]
            
            DCFL["決定性文脈自由言語(DCFL)<br/>・DPDAで受理される言語<br/>・DCFL ⊂ CFL(真部分集合)<br/>・補集合に関して閉じている"]
            
            Applications["実用的応用<br/>・プログラミング言語<br/>・LRパーサ<br/>・コンパイラ設計"]
        end
        
        subgraph "言語クラスの階層"
            Hierarchy["チョムスキーの階層<br/>正規言語 ⊂ DCFL ⊂ 文脈自由言語<br/>⊂ 文脈依存言語 ⊂ 再帰的可算言語"]
            
            Recognition["認識機械<br/>・Type 3: 有限オートマトン<br/>・Type 2: プッシュダウンオートマトン<br/>・Type 1: 線形拘束オートマトン<br/>・Type 0: チューリング機械"]
            
            Practical["実用的重要性<br/>・正規: テキスト処理<br/>・文脈自由: プログラム構文<br/>・文脈依存: 型システム<br/>・再帰的可算: 一般計算"]
        end
    end
    
    style Closed fill:#e8f5e8
    style NotClosed fill:#ffebee
    style Decidable fill:#e3f2fd
    style Undecidable fill:#ffebee
    style DCFL fill:#fff3e0
    style Hierarchy fill:#f3e5f5
```

### 3.7.1 閉包性

**定理 3.11** 文脈自由言語は以下に関して閉じている：
1. 和集合
2. 連結
3. クリーネ閉包
4. 正規言語との積集合

文脈自由言語は積集合、補集合に関して閉じていない。

**例 3.11** L₁ = {aⁿbⁿcᵐ | n, m ≥ 0} と L₂ = {aᵐbⁿcⁿ | n, m ≥ 0} は文脈自由言語だが、L₁ ∩ L₂ = {aⁿbⁿcⁿ | n ≥ 0} は文脈自由言語でない。

### 3.7.2 決定問題

**定理 3.12** 文脈自由言語に対する以下の問題は決定可能：
1. **所属問題**：w ∈ L?（CYKアルゴリズム：O(n³|G|)）
2. **空問題**：L = ∅?
3. **有限性問題**：L は有限？

以下は決定不能：
- **等価性問題**：L₁ = L₂?
- **包含問題**：L₁ ⊆ L₂?
- **曖昧性問題**：CFG は曖昧？

### 3.7.3 決定性文脈自由言語

**定義 3.27** **決定性PDA**（DPDA）：各構成で高々1つの遷移が可能

**定義 3.28** **決定性文脈自由言語**（DCFL）：DPDA で受理される言語

**性質**：
- すべての正規言語は DCFL
- DCFL ⊊ CFL（真部分集合）
- DCFL は補集合に関して閉じている

## 章末問題

### 基礎問題

1. 以下の言語を認識する DFA を構成せよ：
   (a) {w ∈ {0,1}* | w は 00 を部分文字列として含まない}
   (b) {w ∈ {a,b}* | w 中の a の個数は 3 の倍数}
   (c) {w ∈ {0,1}* | w を2進数と見たとき 3 で割り切れる}

2. 以下の言語を表す正規表現を示せ：
   (a) {w ∈ {a,b}* | w は aa も bb も含まない}
   (b) {w ∈ {0,1}* | w のすべての 0 のブロックの長さは偶数}

3. 以下の言語が正規言語でないことを証明せよ：
   (a) {0ⁿ1ᵐ | n ≠ m}
   (b) {w ∈ {0,1}* | w は同数の 0 と 1 を含む}

4. 以下の言語を生成する CFG を構成せよ：
   (a) {aⁱbʲcᵏ | i = j または j = k}
   (b) {w ∈ {a,b}* | w = wᴿ}（回文）

5. PDA を用いて、バランスの取れた括弧列を認識する方法を示せ。

### 発展問題

6. DFA の最小化アルゴリズムを説明し、その正当性を証明せよ。

7. 正規表現から ε-NFA への変換アルゴリズムを詳述せよ。

8. L₁ が正規言語、L₂ が文脈自由言語のとき、L₁ ∩ L₂ が文脈自由言語であることを証明せよ。

9. CYK アルゴリズムを説明し、その時間計算量を解析せよ。

10. 以下の言語が文脈自由言語か決定せよ：
    (a) {aⁿbⁿcⁿdⁿ | n ≥ 0}
    (b) {ww | w ∈ {0,1}*}
    (c) {aⁱbʲcᵏ | i < j < k}

### 探究課題

11. オートマトン理論の実用的応用（コンパイラ、正規表現エンジン、XMLパーサなど）について調査し、理論と実装のギャップについて論ぜよ。

12. 文脈自由言語を超える言語クラス（文脈依存言語、帰納的可算言語など）について調査し、Chomskyの階層との関係を説明せよ。

### 実装課題

#### 1. DFAとNFAのシミュレータを実装せよ

```python
class DFA:
    def __init__(self, states, alphabet, transitions, start, accept_states):
        # DFAの初期化
    
    def accepts(self, string):
        # 文字列を受理するか判定
        
class NFA:
    def __init__(self, states, alphabet, transitions, start, accept_states):
        # NFAの初期化（ε遷移も含む）
    
    def to_dfa(self):
        # 部分集合構成法によりDFAに変換
```

#### 2. 文脈自由文法のCYK構文解析アルゴリズムを実装せよ

- CNF（Chomsky標準形）の文法を入力として受け取る
- 動的計画法により、与えられた文字列が導出可能か判定
- 可能な場合は導出木も構成する