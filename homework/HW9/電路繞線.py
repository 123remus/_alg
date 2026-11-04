# IC 設計中的電路繞線問題
# 在格子狀的繞線通道中，把一條線（net）從起點連到終點，且不能穿過障礙物。
# 本程式比較三種搜尋方法：
#   1. Lee 演算法（BFS 波浪擴散）：保證最短穿線路徑
#   2. A*：使用曼哈頓距離啟發函數，通常展開較少節點
#   3. 貪婪最佳優先搜尋 (Greedy Best-First Search)：只看 heuristic，速度快但不保證最短
# 另外示範多條 net 的循序繞線 (sequential routing)。

import heapq
from collections import deque

# '.' = 可繞線區域，'#' = 障礙物（其他元件或已使用的區域）
CIRCUIT = [
    "............",
    "..####......",
    "..####......",
    "............",
    "......####..",
    "......####..",
    "............",
    "..####......",
    "..####......",
    "............",
    ".........###",
    "............",
]

START = (0, 0)
GOAL = (11, 11)
DIRECTIONS = [(-1, 0), (1, 0), (0, -1), (0, 1)]


def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def is_walkable(grid, pos, blocked=None):
    r, c = pos
    if not (0 <= r < len(grid) and 0 <= c < len(grid[0])):
        return False
    if grid[r][c] == "#":
        return False
    if blocked is not None and pos in blocked:
        return False
    return True


def neighbors(grid, pos, blocked=None):
    r, c = pos
    for dr, dc in DIRECTIONS:
        nxt = (r + dr, c + dc)
        if is_walkable(grid, nxt, blocked):
            yield nxt


def reconstruct(parent, start, goal):
    if goal not in parent:
        return None
    path = [goal]
    cur = goal
    while cur != start:
        cur = parent[cur]
        path.append(cur)
    path.reverse()
    return path


# ---------- 方法 1：Lee 演算法 (BFS) ----------
def lee_algorithm(grid, start, goal):
    queue = deque([start])
    visited = {start}
    parent = {start: None}

    while queue:
        current = queue.popleft()
        if current == goal:
            return reconstruct(parent, start, goal), len(visited)

        for nxt in neighbors(grid, current):
            if nxt not in visited:
                visited.add(nxt)
                parent[nxt] = current
                queue.append(nxt)

    return None, len(visited)


# ---------- 方法 2：A* ----------
def a_star(grid, start, goal, blocked=None):
    open_heap = [(manhattan(start, goal), 0, start)]
    g_score = {start: 0}
    parent = {start: None}
    closed = set()

    while open_heap:
        f, g, current = heapq.heappop(open_heap)

        if current in closed:
            continue
        closed.add(current)

        if current == goal:
            return reconstruct(parent, start, goal), len(closed)

        for nxt in neighbors(grid, current, blocked):
            new_g = g + 1
            if nxt not in g_score or new_g < g_score[nxt]:
                g_score[nxt] = new_g
                parent[nxt] = current
                heapq.heappush(open_heap, (new_g + manhattan(nxt, goal), new_g, nxt))

    return None, len(closed)


# ---------- 方法 3：貪婪最佳優先搜尋 ----------
def greedy_best_first(grid, start, goal, blocked=None):
    open_heap = [(manhattan(start, goal), start)]
    parent = {start: None}
    closed = set()

    while open_heap:
        h, current = heapq.heappop(open_heap)

        if current in closed:
            continue
        closed.add(current)

        if current == goal:
            return reconstruct(parent, start, goal), len(closed)

        for nxt in neighbors(grid, current, blocked):
            if nxt not in parent:
                parent[nxt] = current
                heapq.heappush(open_heap, (manhattan(nxt, goal), nxt))

    return None, len(closed)


def print_path_map(grid, path, start, goal):
    path_set = set(path) if path else set()
    for r in range(len(grid)):
        line = []
        for c in range(len(grid[0])):
            pos = (r, c)
            if pos == start:
                line.append("S")
            elif pos == goal:
                line.append("T")
            elif pos in path_set:
                line.append("*")
            elif grid[r][c] == "#":
                line.append("#")
            else:
                line.append(".")
        print(" ".join(line))


def compare_methods():
    print("=== IC 電路繞線：單一 net 方法比較 ===")
    print("繞線區域：", len(CIRCUIT), "x", len(CIRCUIT[0]))
    print("起點 S =", START, "，終點 T =", GOAL)
    print()

    methods = [
        ("Lee (BFS)", lee_algorithm),
        ("A*", a_star),
        ("Greedy Best-First", greedy_best_first),
    ]

    results = {}
    for name, func in methods:
        path, expanded = func(CIRCUIT, START, GOAL)
        results[name] = (path, expanded)
        if path is None:
            print(name, "：找不到路徑")
        else:
            print(name, "：路徑長度 =", len(path) - 1, "步，展開節點數 =", expanded)

    print()
    print("A* 找到的路徑圖：")
    print_path_map(CIRCUIT, results["A*"][0], START, GOAL)
    return results


def sequential_routing():
    print()
    print("=== 多條 net 循序繞線 (Sequential Routing, 使用 A*) ===")
    print("先繞第一條 net，再把已使用的格子設為障礙，接著繞第二條 net。")
    print("為了避免佔用到其他 net 的接腳，繞線時會保留其他 net 的端點。")
    print()

    open_grid = ["." * 12 for _ in range(12)]
    nets = [
        ((1, 1), (10, 10)),
        ((1, 10), (10, 1)),
    ]

    occupied = set()
    all_paths = []

    for i, (start, goal) in enumerate(nets):
        other_terminals = set()
        for j, (s, g) in enumerate(nets):
            if j != i:
                other_terminals.add(s)
                other_terminals.add(g)

        blocked = occupied | other_terminals
        path, expanded = a_star(open_grid, start, goal, blocked)

        if path is None:
            print("net", i + 1, start, "->", goal, "：繞線失敗")
        else:
            print("net", i + 1, start, "->", goal,
                  "：路徑長度 =", len(path) - 1, "步，展開節點數 =", expanded)
            occupied.update(path)
            all_paths.append(path)

    print()
    print("循序繞線結果（1 = net1，2 = net2，S/T = 端點）：")
    display = [list(row) for row in open_grid]
    for idx, path in enumerate(all_paths, start=1):
        for r, c in path:
            display[r][c] = str(idx)
    for (s, g) in nets:
        display[s[0]][s[1]] = "S"
        display[g[0]][g[1]] = "T"
    for row in display:
        print(" ".join(row))


def main():
    compare_methods()
    sequential_routing()


if __name__ == "__main__":
    main()
