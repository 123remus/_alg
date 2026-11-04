# 八皇后問題 - 深度優先搜尋 (DFS) + 回溯法
# 在 8 x 8 的棋盤上放置 8 個皇后，
# 使任兩個皇后都不在同一列、同一行、同一條對角線上。

N = 8


def solve_n_queens(n):
    solutions = []
    queens = []          # queens[row] = col
    used_cols = set()
    used_diag1 = set()   # row - col
    used_diag2 = set()   # row + col
    nodes = [0]

    def dfs(row):
        nodes[0] += 1
        if row == n:
            solutions.append(queens[:])
            return

        for col in range(n):
            if col in used_cols:
                continue
            if (row - col) in used_diag1:
                continue
            if (row + col) in used_diag2:
                continue

            # 放置皇后
            queens.append(col)
            used_cols.add(col)
            used_diag1.add(row - col)
            used_diag2.add(row + col)

            dfs(row + 1)

            # 回溯：拿走皇后，嘗試下一個位置
            queens.pop()
            used_cols.remove(col)
            used_diag1.remove(row - col)
            used_diag2.remove(row + col)

    dfs(0)
    return solutions, nodes[0]


def print_board(solution):
    n = len(solution)
    for row in range(n):
        line = []
        for col in range(n):
            line.append("Q" if solution[row] == col else ".")
        print(" ".join(line))


def main():
    solutions, nodes = solve_n_queens(N)

    print("=== 八皇后問題 (DFS + 回溯) ===")
    print("棋盤大小：", N, "x", N)
    print("DFS 遞迴呼叫次數：", nodes)
    print("總解答數：", len(solutions))
    print()
    print("第一個解答：")
    print_board(solutions[0])
    print()
    print("第一個解答的皇后位置（第 row 列的皇后在 col 行）：")
    print(solutions[0])


if __name__ == "__main__":
    main()
