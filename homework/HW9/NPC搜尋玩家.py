# NPC 搜尋玩家問題 - A* 搜尋演算法
# 在格子地圖中，NPC (N) 要找到玩家 (P)。
# '.' = 可走，'#' = 障礙物
# A* 使用曼哈頓距離作為啟發函數 (heuristic)。

import heapq

MAP = [
    "..........",
    ".####.###.",
    "..........",
    "###.#####.",
    "..........",
    ".####.###.",
    "..........",
    ".###.####.",
    "..........",
    "..........",
]

START = (0, 0)    # NPC 位置
GOAL = (9, 9)     # 玩家位置
DIRECTIONS = [(-1, 0), (1, 0), (0, -1), (0, 1)]


def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def is_walkable(grid, pos):
    r, c = pos
    return 0 <= r < len(grid) and 0 <= c < len(grid[0]) and grid[r][c] == "."


def neighbors(grid, pos):
    r, c = pos
    for dr, dc in DIRECTIONS:
        nxt = (r + dr, c + dc)
        if is_walkable(grid, nxt):
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


def a_star(grid, start, goal):
    # heap 元素：(f = g + h, g, 位置)
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

        for nxt in neighbors(grid, current):
            new_g = g + 1
            if nxt not in g_score or new_g < g_score[nxt]:
                g_score[nxt] = new_g
                parent[nxt] = current
                new_f = new_g + manhattan(nxt, goal)
                heapq.heappush(open_heap, (new_f, new_g, nxt))

    return None, len(closed)


def print_map(grid, path):
    path_set = set(path) if path else set()
    for r in range(len(grid)):
        line = []
        for c in range(len(grid[0])):
            pos = (r, c)
            if pos == START:
                line.append("N")
            elif pos == GOAL:
                line.append("P")
            elif pos in path_set:
                line.append("*")
            elif grid[r][c] == "#":
                line.append("#")
            else:
                line.append(".")
        print(" ".join(line))


def main():
    path, expanded = a_star(MAP, START, GOAL)

    print("=== NPC 搜尋玩家 (A*) ===")
    print("地圖大小：", len(MAP), "x", len(MAP[0]))
    print("NPC N =", START, "，玩家 P =", GOAL)
    print("啟發函數：曼哈頓距離")
    print("A* 展開節點數：", expanded)

    if path is None:
        print("NPC 找不到玩家！")
        return

    print("找到路徑，步數：", len(path) - 1)
    print("路徑：", path)
    print()
    print("路徑圖（* 代表 NPC 的移動路線）：")
    print_map(MAP, path)


if __name__ == "__main__":
    main()
