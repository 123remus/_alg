# 老鼠走迷宮問題 - 深度優先搜尋 (DFS)
# 0 = 可走的路，1 = 牆壁
# 老鼠從左上角 (0,0) 出發，要走到右下角 (7,7)

MAZE = [
    [0, 1, 0, 0, 0, 0, 0, 0],
    [0, 1, 0, 1, 1, 1, 1, 0],
    [0, 0, 0, 1, 0, 0, 0, 0],
    [1, 1, 0, 1, 0, 1, 1, 0],
    [0, 0, 0, 1, 0, 0, 0, 0],
    [0, 1, 1, 1, 1, 0, 1, 0],
    [0, 0, 0, 0, 0, 0, 1, 0],
    [1, 1, 1, 1, 1, 0, 0, 0],
]

START = (0, 0)
GOAL = (7, 7)

# 四個方向：下、右、上、左
DIRECTIONS = [(1, 0), (0, 1), (-1, 0), (0, -1)]


def dfs_maze(maze, start, goal):
    rows, cols = len(maze), len(maze[0])
    visited = [[False] * cols for _ in range(rows)]
    path = []
    expanded = [0]

    def dfs(pos):
        r, c = pos
        if not (0 <= r < rows and 0 <= c < cols):
            return False
        if maze[r][c] == 1 or visited[r][c]:
            return False

        visited[r][c] = True
        expanded[0] += 1
        path.append(pos)

        if pos == goal:
            return True

        for dr, dc in DIRECTIONS:
            if dfs((r + dr, c + dc)):
                return True

        # 回溯：這條路走不通，把目前位置從路徑中移除
        path.pop()
        return False

    found = dfs(start)
    return (path if found else None), expanded[0]


def print_maze(maze, path):
    path_set = set(path) if path else set()
    for r in range(len(maze)):
        row = []
        for c in range(len(maze[0])):
            if (r, c) == START:
                row.append("S")
            elif (r, c) == GOAL:
                row.append("E")
            elif (r, c) in path_set:
                row.append("*")
            elif maze[r][c] == 1:
                row.append("#")
            else:
                row.append(".")
        print(" ".join(row))


def main():
    path, expanded = dfs_maze(MAZE, START, GOAL)

    print("=== 老鼠走迷宮 (DFS) ===")
    print("迷宮大小：8 x 8")
    print("起點 S = (0,0)，終點 E = (7,7)")
    print("DFS 展開節點數：", expanded)

    if path is None:
        print("找不到出口！")
        return

    print("找到路徑，長度（格子數）：", len(path))
    print("路徑：", path)
    print()
    print("路徑圖（* 代表老鼠走過的路）：")
    print_maze(MAZE, path)


if __name__ == "__main__":
    main()
