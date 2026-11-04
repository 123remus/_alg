# 狼羊甘藍菜過河問題 - 廣度優先搜尋 (BFS)
# 農夫要帶著狼、羊、甘藍菜從左岸到右岸。
# 小船一次只能載農夫和一樣東西（農夫也可以獨自過河）。
# 限制：
#   1. 農夫不在時，狼會吃羊。
#   2. 農夫不在時，羊會吃甘藍菜。
# 狀態表示法：(農夫, 狼, 羊, 甘藍菜)，0 = 左岸，1 = 右岸。

from collections import deque

START = (0, 0, 0, 0)
GOAL = (1, 1, 1, 1)
ITEM_NAMES = ["狼", "羊", "甘藍菜"]


def is_valid(state):
    farmer, wolf, goat, cabbage = state
    # 農夫不在狼和羊身邊，且狼和羊同岸 -> 狼吃羊
    if farmer != wolf and wolf == goat:
        return False
    # 農夫不在羊和甘藍菜身邊，且羊和甘藍菜同岸 -> 羊吃甘藍菜
    if farmer != goat and goat == cabbage:
        return False
    return True


def next_states(state):
    farmer = state[0]
    result = []

    # 農夫獨自過河
    new_state = list(state)
    new_state[0] = 1 - farmer
    result.append((tuple(new_state), "農夫獨自過河"))

    # 農夫帶一樣東西過河
    for i in range(1, 4):
        if state[i] == farmer:  # 這樣東西必須和農夫在同一岸
            new_state = list(state)
            new_state[0] = 1 - farmer
            new_state[i] = 1 - farmer
            result.append((tuple(new_state), "農夫帶" + ITEM_NAMES[i - 1] + "過河"))

    return result


def bfs(start, goal):
    queue = deque([start])
    visited = {start}
    parent = {start: None}
    action = {start: None}

    while queue:
        current = queue.popleft()
        if current == goal:
            break

        for nxt, move in next_states(current):
            if is_valid(nxt) and nxt not in visited:
                visited.add(nxt)
                parent[nxt] = current
                action[nxt] = move
                queue.append(nxt)

    if goal not in parent:
        return None, None, len(visited)

    # 回溯找出完整步驟
    path = []
    steps = []
    cur = goal
    while cur is not None:
        path.append(cur)
        steps.append(action[cur])
        cur = parent[cur]
    path.reverse()
    steps.reverse()

    return path, steps, len(visited)


def side_text(value):
    return "左岸" if value == 0 else "右岸"


def main():
    path, steps, visited_count = bfs(START, GOAL)

    print("=== 狼羊甘藍菜過河 (BFS) ===")
    print("狀態表示：(農夫, 狼, 羊, 甘藍菜)，0 = 左岸，1 = 右岸")
    print("BFS 拜訪狀態數：", visited_count)

    if path is None:
        print("無解！")
        return

    print("最少需要", len(path) - 1, "趟過河")
    print()
    for i in range(1, len(path)):
        print("第", i, "趟：", steps[i])
        print("        狀態：", path[i])
    print()
    print("全部狀態：", path)


if __name__ == "__main__":
    main()
