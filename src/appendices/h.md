---
title: "付録H: 図版ガイドと図一覧"
layout: book
---

# 付録H: 図版ガイドと図一覧

この付録は、本書の図版を**見返す入口**として使うための読者向けガイドです。
本文の途中で見た図を後から探し直したいとき、章をまたいで似た図を比較したいとき、図の役割を確認したいときに参照してください。

## この付録の使い方

- **最初に読む場所ではありません**。本文を読んでいて図に助けられた箇所を、後から戻るための一覧です。
- **本文の節リンク** と **SVG 直接リンク** を併記しています。前者は文脈確認用、後者は図だけを拡大して見たいときに使ってください。
- **章内の位置** は「節」で示しています。厳密な図番号ではなく、読者が再訪しやすい再参照導線を優先しています。

## 図ラベルの読み方

- **直観図**: 定義や証明を置き換えるものではなく、何が本質かを先に掴むための図です。
- **例示図**: アルゴリズムの逐次実行、状態変化、構成の具体例を追うための図です。
- **図版**: 本文に明示ラベルがない図です。節名と alt テキストで文脈を補っています。

## 図版サマリー

- 総図版数: 72
- Part I: 数学的基礎: 24 図
- Part II: 計算理論: 16 図
- Part III: 高度なトピック: 15 図
- Part IV: 応用理論: 17 図

## 図一覧

### Part I: 数学的基礎

#### 第1章 数学的基礎（4 図）
- **図版**: [理論計算機科学の体系と相互関連]({{ '/chapter-1/#理論計算機科学の全体像' | relative_url }}) — 節: 「理論計算機科学の全体像」 / [SVG]({{ '/assets/images/diagrams/ch1_theoretical_cs_overview.svg' | relative_url }})
- **図版**: [集合演算の視覚化]({{ '/chapter-1/#112-集合演算' | relative_url }}) — 節: 「1.1.2 集合演算」 / [SVG]({{ '/assets/images/diagrams/ch1_set_operations_detailed.svg' | relative_url }})
- **図版**: [有理数の可算性の証明]({{ '/chapter-1/#113-集合の濃度-可算と非可算' | relative_url }}) — 節: 「1.1.3 集合の濃度 (可算と非可算)」 / [SVG]({{ '/assets/images/diagrams/ch1_rational_enumeration_cantor.svg' | relative_url }})
- **図版**: [グラフ理論の基本例]({{ '/chapter-1/#151-グラフの定義' | relative_url }}) — 節: 「1.5.1 グラフの定義」 / [SVG]({{ '/assets/images/diagrams/ch1_graph_examples_comprehensive.svg' | relative_url }})

#### 第2章 計算理論の基礎（8 図）
- **図版**: [チューリング機械の構成要素]({{ '/chapter-2/#212-チューリング機械の形式的定義' | relative_url }}) — 節: 「2.1.2 チューリング機械の形式的定義」 / [SVG]({{ '/assets/images/diagrams/ch2_turing_machine_components.svg' | relative_url }})
- **図版**: [チューリング機械の構成]({{ '/chapter-2/#213-チューリング機械の構成と計算' | relative_url }}) — 節: 「2.1.3 チューリング機械の構成と計算」 / [SVG]({{ '/assets/images/diagrams/ch2_turing_machine_configuration.svg' | relative_url }})
- **図版**: [計算可能性の概念と階層]({{ '/chapter-2/#22-計算可能性' | relative_url }}) — 節: 「2.2 計算可能性」 / [SVG]({{ '/assets/images/diagrams/ch2_computability_hierarchy.svg' | relative_url }})
- **図版**: [等価な計算モデル（1930年代）]({{ '/chapter-2/#223-church-turingの提唱' | relative_url }}) — 節: 「2.2.3 Church-Turingの提唱」 / [SVG]({{ '/assets/images/diagrams/ch2_equivalent_computation_models_1930s.svg' | relative_url }})
- **図版**: [決定可能性の階層構造]({{ '/chapter-2/#23-決定可能性' | relative_url }}) — 節: 「2.3 決定可能性」 / [SVG]({{ '/assets/images/diagrams/ch2_decidability_hierarchy.svg' | relative_url }})
- **図版**: [チューリング機械の変種と等価性]({{ '/chapter-2/#24-チューリング機械の変種' | relative_url }}) — 節: 「2.4 チューリング機械の変種」 / [SVG]({{ '/assets/images/diagrams/ch2_turing_machine_variants.svg' | relative_url }})
- **図版**: [万能チューリング機械の構成と意義]({{ '/chapter-2/#25-万能チューリング機械' | relative_url }}) — 節: 「2.5 万能チューリング機械」 / [SVG]({{ '/assets/images/diagrams/ch2_universal_turing_machine.svg' | relative_url }})
- **図版**: [対角化論法と決定不能性]({{ '/chapter-2/#26-計算可能性の基本定理' | relative_url }}) — 節: 「2.6 計算可能性の基本定理」 / [SVG]({{ '/assets/images/diagrams/ch2_diagonalization_undecidability.svg' | relative_url }})

#### 第3章 形式言語とオートマトン理論（12 図）
- **図版**: [形式言語の基本概念]({{ '/chapter-3/#31-形式言語' | relative_url }}) — 節: 「3.1 形式言語」 / [SVG]({{ '/assets/images/diagrams/ch3_formal_language_concepts.svg' | relative_url }})
- **図版**: [有限オートマトンの種類と特徴]({{ '/chapter-3/#32-有限オートマトン' | relative_url }}) — 節: 「3.2 有限オートマトン」 / [SVG]({{ '/assets/images/diagrams/ch3_finite_automata_overview.svg' | relative_url }})
- **図版**: [偶数個の0を認識するDFA]({{ '/chapter-3/#321-決定性有限オートマトンdfa' | relative_url }}) — 節: 「3.2.1 決定性有限オートマトン（DFA）」 / [SVG]({{ '/assets/images/diagrams/ch3_even_zeros_automaton.svg' | relative_url }})
- **図版**: [正規言語と正規表現]({{ '/chapter-3/#33-正規言語' | relative_url }}) — 節: 「3.3 正規言語」 / [SVG]({{ '/assets/images/diagrams/ch3_regular_languages_expressions.svg' | relative_url }})
- **直観図**: [Thompson 構成法：段階図]({{ '/chapter-3/#332-正規表現からnfaへの変換プロセス' | relative_url }}) — 節: 「3.3.2 正規表現からNFAへの変換プロセス」 / [SVG]({{ '/assets/images/diagrams/ch3_regex_to_nfa_thompson_steps.svg' | relative_url }}) / 本文ラベル: 「Thompson 構成の各規則（リテラル・連結・和・クリーネ閉包）」
- **図版**: [ポンピング補題（Pumping Lemma）と限界]({{ '/chapter-3/#34-正規言語の限界' | relative_url }}) — 節: 「3.4 正規言語の限界」 / [SVG]({{ '/assets/images/diagrams/ch3_pumping_lemma_limitations.svg' | relative_url }})
- **図版**: [Myhill–Nerode: 接頭辞で区別できる右コンテキスト]({{ '/chapter-3/#最小dfaとの関係実務的な見方' | relative_url }}) — 節: 「最小DFAとの関係（実務的な見方）」 / [SVG]({{ '/assets/images/diagrams/ch3_myhill_nerode_prefix_distinguish.svg' | relative_url }})
- **図版**: [文脈自由言語と文法]({{ '/chapter-3/#35-文脈自由言語' | relative_url }}) — 節: 「3.5 文脈自由言語」 / [SVG]({{ '/assets/images/diagrams/ch3_context_free_languages_grammars.svg' | relative_url }})
- **図版**: [プッシュダウンオートマトンの構造と機能]({{ '/chapter-3/#36-プッシュダウンオートマトン' | relative_url }}) — 節: 「3.6 プッシュダウンオートマトン」 / [SVG]({{ '/assets/images/diagrams/ch3_pushdown_automata_structure.svg' | relative_url }})
- **直観図**: [PDA のスタック操作（括弧整合）]({{ '/chapter-3/#36-プッシュダウンオートマトン' | relative_url }}) — 節: 「3.6 プッシュダウンオートマトン」 / [SVG]({{ '/assets/images/diagrams/ch3_pda_stack_operation.svg' | relative_url }}) / 本文ラベル: 「括弧整合を受理する PDA のスタック操作例」
- **直観図**: [PDAの受理方式]({{ '/chapter-3/#362-pdaの受理方式' | relative_url }}) — 節: 「3.6.2 PDAの受理方式」 / [SVG]({{ '/assets/images/diagrams/ch3_pda_acceptance_modes.svg' | relative_url }}) / 本文ラベル: 「最終状態受理 vs 空スタック受理」
- **図版**: [文脈自由言語の性質と限界]({{ '/chapter-3/#37-文脈自由言語の性質' | relative_url }}) — 節: 「3.7 文脈自由言語の性質」 / [SVG]({{ '/assets/images/diagrams/ch3_context_free_language_properties.svg' | relative_url }})

### Part II: 計算理論

#### 第4章 計算可能性理論（5 図）
- **図版**: [停止問題の対角化論法]({{ '/chapter-4/#411-停止問題' | relative_url }}) — 節: 「4.1.1 停止問題」 / [SVG]({{ '/assets/images/diagrams/ch4_halting_problem_diagonalization.svg' | relative_url }})
- **図版**: [多対一還元の仕組み]({{ '/chapter-4/#421-多対一還元' | relative_url }}) — 節: 「4.2.1 多対一還元」 / [SVG]({{ '/assets/images/diagrams/ch4_many_one_reduction.svg' | relative_url }})
- **図版**: [言語クラスの階層構造]({{ '/chapter-4/#431-言語クラスの包含関係' | relative_url }}) — 節: 「4.3.1 言語クラスの包含関係」 / [SVG]({{ '/assets/images/diagrams/ch4_language_class_hierarchy.svg' | relative_url }})
- **図版**: [Rice の定理の還元スキーマ（A_{TM} から R_P への還元）]({{ '/chapter-4/#442-riceの定理の主張と証明' | relative_url }}) — 節: 「4.4.2 Riceの定理の主張と証明」 / [SVG]({{ '/assets/images/diagrams/ch4_rice_theorem_reduction.svg' | relative_url }})
- **図版**: [部分再帰関数の構成]({{ '/chapter-4/#451-部分再帰関数' | relative_url }}) — 節: 「4.5.1 部分再帰関数」 / [SVG]({{ '/assets/images/diagrams/ch4_partial_recursive_functions.svg' | relative_url }})

#### 第5章 計算複雑性理論（7 図）
- **直観図**: [Big-O 成長率の比較]({{ '/chapter-5/#512-漸近記法' | relative_url }}) — 節: 「5.1.2 漸近記法」 / [SVG]({{ '/assets/images/diagrams/ch5_big_o_growth_curves.svg' | relative_url }}) / 本文ラベル: 「代表的な計算量の増加の比較（\\(O(1)\\), \\(O(\\log n)\\), \\(O(n)\\), \\(O(n\\log n)\\), \\(O(n^2)\\)）」
- **図版**: [計算複雑性の階層構造]({{ '/chapter-5/#513-時間複雑性クラス' | relative_url }}) — 節: 「5.1.3 時間複雑性クラス」 / [SVG]({{ '/assets/images/diagrams/ch5_complexity_time_hierarchy.svg' | relative_url }})
- **図版**: [P vs NP 問題の構造]({{ '/chapter-5/#531-問題の定式化' | relative_url }}) — 節: 「5.3.1 問題の定式化」 / [SVG]({{ '/assets/images/diagrams/ch5_p_vs_np_structure.svg' | relative_url }})
- **直観図**: [Cook–Levin の直観図（テープ×時間とCNF）]({{ '/chapter-5/#533-cooklevin-の定理' | relative_url }}) — 節: 「5.3.3 Cook–Levin の定理」 / [SVG]({{ '/assets/images/diagrams/ch5_cook_levin_grid.svg' | relative_url }}) / 本文ラベル: 「テープ×時間の格子から CNF への局所制約」
- **図版**: [NP完全性と還元の連鎖]({{ '/chapter-5/#534-np完全問題の連鎖と還元の気持ち' | relative_url }}) — 節: 「5.3.4 NP完全問題の連鎖と還元の「気持ち」」 / [SVG]({{ '/assets/images/diagrams/ch5_np_completeness_reduction_chain.svg' | relative_url }})
- **図版**: [計算複雑性クラスの包含関係]({{ '/chapter-5/#543-空間と時間の関係' | relative_url }}) — 節: 「5.4.3 空間と時間の関係」 / [SVG]({{ '/assets/images/diagrams/ch5_complexity_class_inclusions.svg' | relative_url }})
- **直観図**: [3-SAT → 頂点被覆 ガジェット例]({{ '/chapter-5/#実装課題' | relative_url }}) — 節: 「実装課題」 / [SVG]({{ '/assets/images/diagrams/ch5_reduction_sat_to_vertex_cover_gadget.svg' | relative_url }}) / 本文ラベル: 「変数/節ガジェットの最小例（3-SAT → 頂点被覆）」

#### 第6章 アルゴリズムの数学的解析（4 図）
- **図版**: [主要な時間複雑度クラス]({{ '/chapter-6/#611-最悪時間解析' | relative_url }}) — 節: 「6.1.1 最悪時間解析」 / [SVG]({{ '/assets/images/diagrams/ch6_complexity_classes.svg' | relative_url }})
- **図版**: [マスター定理の適用]({{ '/chapter-6/#622-マスター定理' | relative_url }}) — 節: 「6.2.2 マスター定理」 / [SVG]({{ '/assets/images/diagrams/ch6_master_theorem.svg' | relative_url }})
- **図版**: [動的計画法の適用条件]({{ '/chapter-6/#631-最適部分構造' | relative_url }}) — 節: 「6.3.1 最適部分構造」 / [SVG]({{ '/assets/images/diagrams/ch6_dynamic_programming_conditions.svg' | relative_url }})
- **図版**: [アルゴリズム設計パラダイムの比較]({{ '/chapter-6/#641-貪欲選択性' | relative_url }}) — 節: 「6.4.1 貪欲選択性」 / [SVG]({{ '/assets/images/diagrams/ch6_algorithm_paradigms.svg' | relative_url }})

### Part III: 高度なトピック

#### 第7章 データ構造の理論（4 図）
- **図版**: [基本データ構造の比較]({{ '/chapter-7/#721-配列とリスト' | relative_url }}) — 節: 「7.2.1 配列とリスト」 / [SVG]({{ '/assets/images/diagrams/ch7_basic_data_structures.svg' | relative_url }})
- **図版**: [AVL木の回転操作]({{ '/chapter-7/#731-avl木' | relative_url }}) — 節: 「7.3.1 AVL木」 / [SVG]({{ '/assets/images/diagrams/ch7_avl_tree_rotations.svg' | relative_url }})
- **図版**: [Union-Findの最適化技法]({{ '/chapter-7/#742-union-find構造' | relative_url }}) — 節: 「7.4.2 Union-Find構造」 / [SVG]({{ '/assets/images/diagrams/ch7_union_find_optimization.svg' | relative_url }})
- **図版**: [スキップリストの構造]({{ '/chapter-7/#761-スキップリスト' | relative_url }}) — 節: 「7.6.1 スキップリスト」 / [SVG]({{ '/assets/images/diagrams/ch7_skip_list_structure.svg' | relative_url }})

#### 第8章 グラフ理論とネットワーク（6 図）
- **直観図**: [BFS と DFS の比較]({{ '/chapter-8/#813-グラフの走査' | relative_url }}) — 節: 「8.1.3 グラフの走査」 / [SVG]({{ '/assets/images/diagrams/ch8_bfs_vs_dfs_compare.svg' | relative_url }}) / 本文ラベル: 「同一グラフに対する BFS と DFS の探索順・探索木の比較」
- **図版**: [Dijkstraアルゴリズムの実行例]({{ '/chapter-8/#821-単一始点最短路' | relative_url }}) — 節: 「8.2.1 単一始点最短路」 / [SVG]({{ '/assets/images/diagrams/ch8_dijkstra_algorithm_execution.svg' | relative_url }})
- **例示図**: [Dijkstra 法の逐次確定の例]({{ '/chapter-8/#dijkstraのアルゴリズム' | relative_url }}) — 節: 「Dijkstraのアルゴリズム」 / [SVG]({{ '/assets/images/diagrams/ch8_dijkstra_step_trace.svg' | relative_url }}) / 本文ラベル: 「Dijkstra の逐次確定（確定集合と緩和の模式図）」
- **図版**: [Kruskal法とUnion-Findの流れ]({{ '/chapter-8/#832-kruskalのアルゴリズム' | relative_url }}) — 節: 「8.3.2 Kruskalのアルゴリズム」 / [SVG]({{ '/assets/images/diagrams/ch8_mst_kruskal_unionfind.svg' | relative_url }})
- **図版**: [最大フロー最小カットの例]({{ '/chapter-8/#841-最大フロー問題' | relative_url }}) — 節: 「8.4.1 最大フロー問題」 / [SVG]({{ '/assets/images/diagrams/ch8_maximum_flow_minimum_cut.svg' | relative_url }})
- **図版**: [二部グラフのマッチング]({{ '/chapter-8/#851-二部グラフのマッチング' | relative_url }}) — 節: 「8.5.1 二部グラフのマッチング」 / [SVG]({{ '/assets/images/diagrams/ch8_bipartite_graph_matching.svg' | relative_url }})

#### 第9章 論理学と形式的手法（5 図）
- **図版**: [命題論理の決定手続きの比較]({{ '/chapter-9/#914-命題論理の決定手続き' | relative_url }}) — 節: 「9.1.4 命題論理の決定手続き」 / [SVG]({{ '/assets/images/diagrams/ch9_propositional_logic_decision_procedures.svg' | relative_url }})
- **直観図**: [DPLL と CDCL の対比]({{ '/chapter-9/#914-命題論理の決定手続き' | relative_url }}) — 節: 「9.1.4 命題論理の決定手続き」 / [SVG]({{ '/assets/images/diagrams/ch9_dpll_cdcl_side_by_side.svg' | relative_url }}) / 本文ラベル: 「DPLL と CDCL の対比（学習・非年代戻り・VSIDS）」
- **図版**: [時相論理とモデル検査]({{ '/chapter-9/#933-モデル検査' | relative_url }}) — 節: 「9.3.3 モデル検査」 / [SVG]({{ '/assets/images/diagrams/ch9_temporal_logic_model_checking.svg' | relative_url }})
- **図版**: [Hoare論理の推論規則体系]({{ '/chapter-9/#942-推論規則' | relative_url }}) — 節: 「9.4.2 推論規則」 / [SVG]({{ '/assets/images/diagrams/ch9_hoare_logic_inference_system.svg' | relative_url }})
- **図版**: [定理証明支援系の分類と特徴]({{ '/chapter-9/#961-対話型定理証明' | relative_url }}) — 節: 「9.6.1 対話型定理証明」 / [SVG]({{ '/assets/images/diagrams/ch9_theorem_proving_systems.svg' | relative_url }})

### Part IV: 応用理論

#### 第10章 情報理論（6 図）
- **図版**: [情報量とエントロピーの概念]({{ '/chapter-10/#1012-shannon-エントロピー' | relative_url }}) — 節: 「10.1.2 Shannon エントロピー」 / [SVG]({{ '/assets/images/diagrams/ch10_information_entropy_concepts.svg' | relative_url }})
- **直観図**: [二値エントロピー関数 h(p) の曲線]({{ '/chapter-10/#1012-shannon-エントロピー' | relative_url }}) — 節: 「10.1.2 Shannon エントロピー」 / [SVG]({{ '/assets/images/diagrams/ch10_binary_entropy_curve.svg' | relative_url }}) / 本文ラベル: 「二値エントロピー h(p) の曲線（底は \\(\\log_2\\)）」
- **図版**: [Huffman符号の構成例]({{ '/chapter-10/#huffman-符号' | relative_url }}) — 節: 「Huffman 符号」 / [SVG]({{ '/assets/images/diagrams/ch10_huffman_coding_construction.svg' | relative_url }})
- **図版**: [通信路モデルと容量]({{ '/chapter-10/#1031-通信路モデル' | relative_url }}) — 節: 「10.3.1 通信路モデル」 / [SVG]({{ '/assets/images/diagrams/ch10_channel_models_capacity.svg' | relative_url }})
- **直観図**: [AWGN 容量曲線]({{ '/chapter-10/#1054-帯域制限通信路' | relative_url }}) — 節: 「10.5.4 帯域制限通信路」 / [SVG]({{ '/assets/images/diagrams/ch10_awgn_capacity_curve.svg' | relative_url }}) / 本文ラベル: 「AWGN 容量 \\(C = \\frac{1}{2} \\log_2(1+\\mathrm{SNR})\\) の曲線」
- **図版**: [情報理論の応用分野]({{ '/chapter-10/#1061-データ圧縮への応用' | relative_url }}) — 節: 「10.6.1 データ圧縮への応用」 / [SVG]({{ '/assets/images/diagrams/ch10_information_theory_applications.svg' | relative_url }})

#### 第11章 暗号理論の数学的基礎（5 図）
- **図版**: [暗号システムの基本構造]({{ '/chapter-11/#1111-暗号システムの定義' | relative_url }}) — 節: 「11.1.1 暗号システムの定義」 / [SVG]({{ '/assets/images/diagrams/ch11_cryptography_basics.svg' | relative_url }})
- **直観図**: [ECB でパターンが露呈する例]({{ '/chapter-11/#1123-暗号利用モード' | relative_url }}) — 節: 「11.2.3 暗号利用モード」 / [SVG]({{ '/assets/images/diagrams/ch11_ecb_pattern_leak_example.svg' | relative_url }}) / 本文ラベル: 「模様が暗号文に残る（ECBの例）」
- **直観図**: [AEAD の処理フロー]({{ '/chapter-11/#1124-認証付き暗号' | relative_url }}) — 節: 「11.2.4 認証付き暗号」 / [SVG]({{ '/assets/images/diagrams/ch11_aead_flow_overview.svg' | relative_url }}) / 本文ラベル: 「AEAD の処理フロー（鍵/ノンス/AD/平文から暗号文+タグへの変換、検証）」
- **図版**: [RSA暗号の仕組み]({{ '/chapter-11/#1131-rsa-暗号' | relative_url }}) — 節: 「11.3.1 RSA 暗号」 / [SVG]({{ '/assets/images/diagrams/ch11_rsa_cryptosystem.svg' | relative_url }})
- **図版**: [ゼロ知識証明の概念と応用]({{ '/chapter-11/#1162-ゼロ知識性' | relative_url }}) — 節: 「11.6.2 ゼロ知識性」 / [SVG]({{ '/assets/images/diagrams/ch11_zero_knowledge_proofs.svg' | relative_url }})

#### 第12章 並行計算の理論（6 図）
- **図版**: [並行計算の基本概念]({{ '/chapter-12/#1211-並行性の基本概念' | relative_url }}) — 節: 「12.1.1 並行性の基本概念」 / [SVG]({{ '/assets/images/diagrams/ch12_concurrent_computing_models.svg' | relative_url }})
- **直観図**: [HB 関係のタイムライン]({{ '/chapter-12/#1212-共有メモリモデル' | relative_url }}) — 節: 「12.1.2 共有メモリモデル」 / [SVG]({{ '/assets/images/diagrams/ch12_hb_relations_timeline.svg' | relative_url }}) / 本文ラベル: 「happens-before（HB）関係のタイムライン」
- **図版**: [Petriネットによる並行システムモデリング]({{ '/chapter-12/#1231-基本定義' | relative_url }}) — 節: 「12.3.1 基本定義」 / [SVG]({{ '/assets/images/diagrams/ch12_petri_nets_modeling.svg' | relative_url }})
- **直観図**: [デッドロックのCoffmanの4条件]({{ '/chapter-12/#1243-モデル検査アルゴリズム' | relative_url }}) — 節: 「12.4.3 モデル検査アルゴリズム」 / [SVG]({{ '/assets/images/diagrams/ch12_deadlock_coffman_conditions.svg' | relative_url }}) / 本文ラベル: 「Coffman の4条件と資源割当グラフ（デッドロック例）」
- **図版**: [並行データ構造の設計手法]({{ '/chapter-12/#1262-ロックフリーアルゴリズム' | relative_url }}) — 節: 「12.6.2 ロックフリーアルゴリズム」 / [SVG]({{ '/assets/images/diagrams/ch12_lock_free_algorithms.svg' | relative_url }})
- **直観図**: [ABA問題の概念図]({{ '/chapter-12/#1262-ロックフリーアルゴリズム' | relative_url }}) — 節: 「12.6.2 ロックフリーアルゴリズム」 / [SVG]({{ '/assets/images/diagrams/ch12_aba_problem_diagram.svg' | relative_url }}) / 本文ラベル: 「ABA問題の概念図と緩和策の示唆」

## 補足

- 図版の追加・差し替えに合わせてこの付録を更新する場合は、`python3 scripts/generate_figure_guide.py` を実行してください。
- 本文側の図ラベルを増やす場合でも、ここでは読者が探し直しやすい最小限の情報を優先してください。
