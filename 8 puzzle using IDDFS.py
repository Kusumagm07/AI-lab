from copy import deepcopy

# Goal State
goal_state = [[1, 2, 3],
              [4, 5, 6],
              [7, 8, 0]]

# Moves: (dx, dy, move_name)
moves = [(-1, 0, "Up"), (1, 0, "Down"), (0, -1, "Left"), (0, 1, "Right")]

def is_goal(state):
    return state == goal_state

def find_blank(state):
    for i in range(3):
        for j in range(3):
            if state[i][j] == 0:
                return i, j

def get_neighbors(state):
    x, y = find_blank(state)
    neighbors = []
    for dx, dy, move in moves:
        nx, ny = x + dx, y + dy
        if 0 <= nx < 3 and 0 <= ny < 3:
            new_state = deepcopy(state)
            # Swap blank with neighbor
            new_state[x][y], new_state[nx][ny] = new_state[nx][ny], new_state[x][y]
            neighbors.append((new_state, move))
    return neighbors

def dls(state, limit, path, moves_taken):
    if is_goal(state):
        return path, moves_taken
    if limit == 0:
        return None
    for neighbor, move in get_neighbors(state):
        if neighbor not in path:  # avoid cycles
            result = dls(neighbor, limit - 1, path + [neighbor], moves_taken + [move])
            if result:
                return result
    return None

def iddfs_with_limit(start_state, max_depth):
    for depth in range(max_depth + 1):
        print(f"🔎 Trying with depth limit = {depth}")
        result = dls(start_state, depth, [start_state], [])
        if result:
            return result
    return None

def print_state(state):
    for row in state:
        print(" ".join(str(x) for x in row))
    print("------")

# -------------------
# Example Run
# -------------------
start_state = [[1, 2, 3],
               [0, 4, 6],
               [7, 5, 8]]

max_depth = 3# Change to test different limits

solution = iddfs_with_limit(start_state, max_depth)

if solution:
    path, moves_taken = solution
    print(f"\n✅ Solution found within depth {max_depth} in {len(path)-1} moves:\n")
    for step, state in enumerate(path):
        print(f"Step {step}:")
        print_state(state)
        if step > 0:
            print(f"Move taken: {moves_taken[step-1]}\n")
else:
    print(f"\n❌ No solution found within depth {max_depth}")
