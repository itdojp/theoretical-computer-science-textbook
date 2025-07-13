# 付録B: アルゴリズム実装例

本書で学習する理論的アルゴリズムのPython実装例と複雑性解析を示します。

## 第1章: 数学的基礎

### 1.1 最大公約数（ユークリッドアルゴリズム）

```python
def gcd(a, b):
    """
    ユークリッドアルゴリズムによる最大公約数の計算
    
    時間複雑性: O(log(min(a, b)))
    空間複雑性: O(log(min(a, b))) (再帰による)
    """
    if b == 0:
        return a
    return gcd(b, a % b)

def gcd_iterative(a, b):
    """
    反復版ユークリッドアルゴリズム
    
    時間複雑性: O(log(min(a, b)))
    空間複雑性: O(1)
    """
    while b != 0:
        a, b = b, a % b
    return a

# 使用例
print(f"gcd(48, 18) = {gcd(48, 18)}")  # 6
print(f"gcd_iterative(48, 18) = {gcd_iterative(48, 18)}")  # 6
```

### 1.2 拡張ユークリッドアルゴリズム

```python
def extended_gcd(a, b):
    """
    拡張ユークリッドアルゴリズム
    ax + by = gcd(a, b) を満たす x, y を求める
    
    返り値: (gcd, x, y)
    時間複雑性: O(log(min(a, b)))
    """
    if b == 0:
        return a, 1, 0
    
    gcd_val, x1, y1 = extended_gcd(b, a % b)
    x = y1
    y = x1 - (a // b) * y1
    
    return gcd_val, x, y

# 使用例
gcd_val, x, y = extended_gcd(48, 18)
print(f"gcd(48, 18) = {gcd_val}")
print(f"48 * {x} + 18 * {y} = {gcd_val}")  # 48 * (-1) + 18 * 3 = 6
```

### 1.3 べき乗計算（高速べき乗）

```python
def fast_power(base, exp, mod=None):
    """
    高速べき乗アルゴリズム
    
    時間複雑性: O(log exp)
    空間複雑性: O(1)
    """
    result = 1
    base = base % mod if mod else base
    
    while exp > 0:
        if exp & 1:  # expが奇数の場合
            result = (result * base) % mod if mod else result * base
        exp >>= 1  # exp = exp // 2
        base = (base * base) % mod if mod else base * base
    
    return result

# 使用例
print(f"2^10 = {fast_power(2, 10)}")  # 1024
print(f"2^10 mod 1000 = {fast_power(2, 10, 1000)}")  # 24
```

## 第3章: 形式言語とオートマトン理論

### 3.1 有限オートマトンシミュレーター

```python
class FiniteAutomaton:
    """
    決定性有限オートマトン（DFA）のシミュレーター
    """
    
    def __init__(self, states, alphabet, transitions, start_state, accept_states):
        self.states = set(states)
        self.alphabet = set(alphabet)
        self.transitions = transitions  # {(state, symbol): next_state}
        self.start_state = start_state
        self.accept_states = set(accept_states)
    
    def process_string(self, input_string):
        """
        文字列を処理して受理するかどうかを判定
        
        時間複雑性: O(|input_string|)
        空間複雑性: O(1)
        """
        current_state = self.start_state
        
        for symbol in input_string:
            if symbol not in self.alphabet:
                return False
            
            if (current_state, symbol) not in self.transitions:
                return False
            
            current_state = self.transitions[(current_state, symbol)]
        
        return current_state in self.accept_states

# 使用例: (ab)*を受理するDFA
dfa = FiniteAutomaton(
    states=['q0', 'q1'],
    alphabet=['a', 'b'],
    transitions={
        ('q0', 'a'): 'q1',
        ('q1', 'b'): 'q0'
    },
    start_state='q0',
    accept_states=['q0']
)

test_strings = ['', 'ab', 'abab', 'aba', 'ba']
for s in test_strings:
    result = dfa.process_string(s)
    print(f"'{s}': {'Accepted' if result else 'Rejected'}")
```

### 3.2 非決定性有限オートマトン（NFA）

```python
class NonDeterministicFiniteAutomaton:
    """
    非決定性有限オートマトン（NFA）のシミュレーター
    """
    
    def __init__(self, states, alphabet, transitions, start_state, accept_states):
        self.states = set(states)
        self.alphabet = set(alphabet)
        self.transitions = transitions  # {(state, symbol): [next_states]}
        self.start_state = start_state
        self.accept_states = set(accept_states)
    
    def epsilon_closure(self, states):
        """
        ε遷移の閉包を計算
        
        時間複雑性: O(|states|^2)
        """
        closure = set(states)
        stack = list(states)
        
        while stack:
            state = stack.pop()
            if (state, '') in self.transitions:  # ε遷移
                for next_state in self.transitions[(state, '')]:
                    if next_state not in closure:
                        closure.add(next_state)
                        stack.append(next_state)
        
        return closure
    
    def process_string(self, input_string):
        """
        文字列を処理して受理するかどうかを判定
        
        時間複雑性: O(|input_string| * |states|^2)
        空間複雑性: O(|states|)
        """
        current_states = self.epsilon_closure({self.start_state})
        
        for symbol in input_string:
            if symbol not in self.alphabet:
                return False
            
            next_states = set()
            for state in current_states:
                if (state, symbol) in self.transitions:
                    next_states.update(self.transitions[(state, symbol)])
            
            current_states = self.epsilon_closure(next_states)
        
        return bool(current_states & self.accept_states)
```

## 第5章: 計算複雑性理論

### 5.1 サブセット和問題（NP完全問題の例）

```python
def subset_sum_brute_force(numbers, target):
    """
    サブセット和問題の総当たり解法
    
    時間複雑性: O(2^n)
    空間複雑性: O(n)
    """
    n = len(numbers)
    
    # すべての部分集合を生成
    for mask in range(1 << n):  # 2^n通り
        subset_sum = 0
        subset = []
        
        for i in range(n):
            if mask & (1 << i):
                subset_sum += numbers[i]
                subset.append(numbers[i])
        
        if subset_sum == target:
            return True, subset
    
    return False, []

def subset_sum_dp(numbers, target):
    """
    サブセット和問題の動的計画法による解法
    
    時間複雑性: O(n * target)
    空間複雑性: O(n * target)
    """
    n = len(numbers)
    # dp[i][j] = i番目までの数で和jが作れるか
    dp = [[False] * (target + 1) for _ in range(n + 1)]
    
    # 和0は常に作れる（空集合）
    for i in range(n + 1):
        dp[i][0] = True
    
    for i in range(1, n + 1):
        for j in range(target + 1):
            # i番目の数を使わない場合
            dp[i][j] = dp[i-1][j]
            
            # i番目の数を使う場合
            if j >= numbers[i-1]:
                dp[i][j] = dp[i][j] or dp[i-1][j - numbers[i-1]]
    
    return dp[n][target]

# 使用例
numbers = [3, 34, 4, 12, 5, 2]
target = 9

result, subset = subset_sum_brute_force(numbers, target)
print(f"Brute force: {result}, subset: {subset}")

result_dp = subset_sum_dp(numbers, target)
print(f"Dynamic programming: {result_dp}")
```

### 5.2 3-SAT問題（NP完全問題）

```python
def evaluate_3sat_clause(clause, assignment):
    """
    3-SAT節の評価
    clause: [(variable, negated), ...]
    assignment: {variable: boolean}
    """
    for var, negated in clause:
        value = assignment.get(var, False)
        if negated:
            value = not value
        if value:  # 節が真になる
            return True
    return False

def solve_3sat_brute_force(clauses, variables):
    """
    3-SAT問題の総当たり解法
    
    時間複雑性: O(2^n * m) where n=|variables|, m=|clauses|
    空間複雑性: O(n)
    """
    n = len(variables)
    
    # すべての真偽値割当を試す
    for mask in range(1 << n):
        assignment = {}
        for i, var in enumerate(variables):
            assignment[var] = bool(mask & (1 << i))
        
        # すべての節が満足されるかチェック
        all_satisfied = True
        for clause in clauses:
            if not evaluate_3sat_clause(clause, assignment):
                all_satisfied = False
                break
        
        if all_satisfied:
            return True, assignment
    
    return False, {}

# 使用例: (x1 ∨ ¬x2 ∨ x3) ∧ (¬x1 ∨ x2 ∨ ¬x3) ∧ (x1 ∨ x2 ∨ x3)
clauses = [
    [('x1', False), ('x2', True), ('x3', False)],   # x1 ∨ ¬x2 ∨ x3
    [('x1', True), ('x2', False), ('x3', True)],    # ¬x1 ∨ x2 ∨ ¬x3
    [('x1', False), ('x2', False), ('x3', False)]   # x1 ∨ x2 ∨ x3
]
variables = ['x1', 'x2', 'x3']

satisfiable, assignment = solve_3sat_brute_force(clauses, variables)
print(f"3-SAT satisfiable: {satisfiable}")
if satisfiable:
    print(f"Assignment: {assignment}")
```

## 第6章: アルゴリズムの数学的解析

### 6.1 マージソート

```python
def merge_sort(arr):
    """
    マージソート
    
    時間複雑性: O(n log n)
    空間複雑性: O(n)
    """
    if len(arr) <= 1:
        return arr
    
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    
    return merge(left, right)

def merge(left, right):
    """
    ソート済み配列のマージ
    
    時間複雑性: O(n)
    """
    result = []
    i = j = 0
    
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    
    result.extend(left[i:])
    result.extend(right[j:])
    
    return result

# 使用例
arr = [64, 34, 25, 12, 22, 11, 90]
sorted_arr = merge_sort(arr)
print(f"Original: {arr}")
print(f"Sorted: {sorted_arr}")
```

### 6.2 クイックソート

```python
import random

def quicksort(arr, low=0, high=None):
    """
    クイックソート
    
    時間複雑性: 平均 O(n log n), 最悪 O(n^2)
    空間複雑性: 平均 O(log n), 最悪 O(n)
    """
    if high is None:
        high = len(arr) - 1
    
    if low < high:
        pivot_index = randomized_partition(arr, low, high)
        quicksort(arr, low, pivot_index - 1)
        quicksort(arr, pivot_index + 1, high)

def randomized_partition(arr, low, high):
    """
    ランダム化分割
    最悪ケースの確率を下げる
    """
    random_index = random.randint(low, high)
    arr[random_index], arr[high] = arr[high], arr[random_index]
    return partition(arr, low, high)

def partition(arr, low, high):
    """
    分割操作
    """
    pivot = arr[high]
    i = low - 1
    
    for j in range(low, high):
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1

# 使用例
arr = [64, 34, 25, 12, 22, 11, 90]
print(f"Original: {arr}")
quicksort(arr)
print(f"Sorted: {arr}")
```

### 6.3 動的計画法：最長共通部分列（LCS）

```python
def lcs_length(X, Y):
    """
    最長共通部分列の長さを求める
    
    時間複雑性: O(mn)
    空間複雑性: O(mn)
    """
    m, n = len(X), len(Y)
    
    # dp[i][j] = X[0:i]とY[0:j]のLCSの長さ
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if X[i-1] == Y[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])
    
    return dp[m][n]

def lcs_sequence(X, Y):
    """
    最長共通部分列を構築
    
    時間複雑性: O(mn)
    空間複雑性: O(mn)
    """
    m, n = len(X), len(Y)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    # DPテーブルを構築
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if X[i-1] == Y[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])
    
    # LCSを再構築
    lcs = []
    i, j = m, n
    while i > 0 and j > 0:
        if X[i-1] == Y[j-1]:
            lcs.append(X[i-1])
            i -= 1
            j -= 1
        elif dp[i-1][j] > dp[i][j-1]:
            i -= 1
        else:
            j -= 1
    
    return ''.join(reversed(lcs))

# 使用例
X = "ABCDGH"
Y = "AEDFHR"
print(f"X: {X}")
print(f"Y: {Y}")
print(f"LCS length: {lcs_length(X, Y)}")
print(f"LCS: {lcs_sequence(X, Y)}")
```

## 第8章: グラフ理論とネットワーク

### 8.1 深さ優先探索（DFS）

```python
from collections import defaultdict

class Graph:
    def __init__(self, directed=False):
        self.graph = defaultdict(list)
        self.directed = directed
    
    def add_edge(self, u, v):
        self.graph[u].append(v)
        if not self.directed:
            self.graph[v].append(u)
    
    def dfs(self, start, visited=None):
        """
        深さ優先探索
        
        時間複雑性: O(V + E)
        空間複雑性: O(V)
        """
        if visited is None:
            visited = set()
        
        visited.add(start)
        print(start, end=' ')
        
        for neighbor in self.graph[start]:
            if neighbor not in visited:
                self.dfs(neighbor, visited)
    
    def dfs_iterative(self, start):
        """
        反復版深さ優先探索
        
        時間複雑性: O(V + E)
        空間複雑性: O(V)
        """
        visited = set()
        stack = [start]
        
        while stack:
            vertex = stack.pop()
            if vertex not in visited:
                visited.add(vertex)
                print(vertex, end=' ')
                
                # 隣接頂点を逆順でスタックに追加
                for neighbor in reversed(self.graph[vertex]):
                    if neighbor not in visited:
                        stack.append(neighbor)

# 使用例
g = Graph()
g.add_edge(0, 1)
g.add_edge(0, 2)
g.add_edge(1, 2)
g.add_edge(2, 0)
g.add_edge(2, 3)
g.add_edge(3, 3)

print("DFS (recursive):")
g.dfs(2)
print()

print("DFS (iterative):")
g.dfs_iterative(2)
print()
```

### 8.2 幅優先探索（BFS）

```python
from collections import deque

class Graph:
    def __init__(self, directed=False):
        self.graph = defaultdict(list)
        self.directed = directed
    
    def add_edge(self, u, v):
        self.graph[u].append(v)
        if not self.directed:
            self.graph[v].append(u)
    
    def bfs(self, start):
        """
        幅優先探索
        
        時間複雑性: O(V + E)
        空間複雑性: O(V)
        """
        visited = set()
        queue = deque([start])
        visited.add(start)
        
        while queue:
            vertex = queue.popleft()
            print(vertex, end=' ')
            
            for neighbor in self.graph[vertex]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
    
    def shortest_path(self, start, end):
        """
        最短経路（重みなしグラフ）
        
        時間複雑性: O(V + E)
        空間複雑性: O(V)
        """
        if start == end:
            return [start]
        
        visited = set()
        queue = deque([(start, [start])])
        visited.add(start)
        
        while queue:
            vertex, path = queue.popleft()
            
            for neighbor in self.graph[vertex]:
                if neighbor == end:
                    return path + [neighbor]
                
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        
        return None  # パスが存在しない

# 使用例
g = Graph()
g.add_edge(0, 1)
g.add_edge(0, 2)
g.add_edge(1, 2)
g.add_edge(2, 0)
g.add_edge(2, 3)
g.add_edge(3, 3)

print("BFS:")
g.bfs(2)
print()

path = g.shortest_path(0, 3)
print(f"Shortest path from 0 to 3: {path}")
```

### 8.3 ダイクストラ法

```python
import heapq
from collections import defaultdict
import sys

class WeightedGraph:
    def __init__(self, directed=True):
        self.graph = defaultdict(list)
        self.directed = directed
    
    def add_edge(self, u, v, weight):
        self.graph[u].append((v, weight))
        if not self.directed:
            self.graph[v].append((u, weight))
    
    def dijkstra(self, start):
        """
        ダイクストラ法による単一始点最短経路
        
        時間複雑性: O((V + E) log V)
        空間複雑性: O(V)
        """
        distances = defaultdict(lambda: sys.maxsize)
        distances[start] = 0
        predecessor = {}
        visited = set()
        
        # 優先度付きキュー（最小ヒープ）
        pq = [(0, start)]
        
        while pq:
            current_distance, current_vertex = heapq.heappop(pq)
            
            if current_vertex in visited:
                continue
            
            visited.add(current_vertex)
            
            for neighbor, weight in self.graph[current_vertex]:
                distance = current_distance + weight
                
                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    predecessor[neighbor] = current_vertex
                    heapq.heappush(pq, (distance, neighbor))
        
        return dict(distances), predecessor
    
    def get_path(self, predecessor, start, end):
        """
        最短経路を再構築
        """
        path = []
        current = end
        
        while current != start:
            if current not in predecessor:
                return None  # パスが存在しない
            path.append(current)
            current = predecessor[current]
        
        path.append(start)
        return list(reversed(path))

# 使用例
g = WeightedGraph()
g.add_edge('A', 'B', 4)
g.add_edge('A', 'C', 2)
g.add_edge('B', 'C', 1)
g.add_edge('B', 'D', 5)
g.add_edge('C', 'D', 8)
g.add_edge('C', 'E', 10)
g.add_edge('D', 'E', 2)

distances, predecessor = g.dijkstra('A')
print("Shortest distances from A:")
for vertex, distance in sorted(distances.items()):
    print(f"  {vertex}: {distance}")

print("\\nShortest paths from A:")
for vertex in sorted(distances.keys()):
    if vertex != 'A':
        path = g.get_path(predecessor, 'A', vertex)
        print(f"  A to {vertex}: {' -> '.join(path)} (distance: {distances[vertex]})")
```

## 実行時間測定とベンチマーク

```python
import time
import random
import matplotlib.pyplot as plt

def benchmark_sorting_algorithms():
    """
    ソートアルゴリズムのベンチマーク
    """
    sizes = [100, 500, 1000, 2000, 5000]
    merge_times = []
    quick_times = []
    
    for size in sizes:
        # ランダムデータ生成
        data = [random.randint(1, 1000) for _ in range(size)]
        
        # マージソート
        data_copy = data.copy()
        start_time = time.time()
        merge_sort(data_copy)
        merge_times.append(time.time() - start_time)
        
        # クイックソート
        data_copy = data.copy()
        start_time = time.time()
        quicksort(data_copy)
        quick_times.append(time.time() - start_time)
    
    return sizes, merge_times, quick_times

# ベンチマーク実行（実際の実装では matplotlib が必要）
# sizes, merge_times, quick_times = benchmark_sorting_algorithms()
# print("Sorting algorithm benchmark completed")
```

このように、理論で学習したアルゴリズムを実際に実装することで、理論と実践の橋渡しができます。各実装には時間・空間複雑性も明記しており、理論的解析と実装の関係を理解できるようになっています。