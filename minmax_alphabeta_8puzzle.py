import copy

# Define the goal state
goal_state = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 0]
]

# Find blank position (0)
def find_blank(state):
    for i in range(3):
        for j in range(3):
            if state[i][j] == 0:
                return i, j

# Print puzzle neatly
def print_state(state):
    for row in state:
        print(row)
    print()

# Manhattan distance heuristic
def manhattan_distance(state):
    distance = 0
    for i in range(3):
        for j in range(3):
            value = state[i][j]
            if value != 0:
                goal_x = (value - 1) // 3
                goal_y = (value - 1) % 3
                distance += abs(goal_x - i) + abs(goal_y - j)
    return distance

# Get possible moves
def get_neighbors(state):
    neighbors = []
    i, j = find_blank(state)
    directions = [(-1,0), (1,0), (0,-1), (0,1)]
    for di, dj in directions:
        ni, nj = i + di, j + dj
        if 0 <= ni < 3 and 0 <= nj < 3:
            new_state = copy.deepcopy(state)
            new_state[i][j], new_state[ni][nj] = new_state[ni][nj], new_state[i][j]
            neighbors.append(new_state)
    return neighbors

# Minimax with Manhattan heuristic
def minimax(state, depth, is_maximizing):
    h = manhattan_distance(state)
    if h == 0:  # Goal state
        return 0
    if depth == 0:
        return h

    neighbors = get_neighbors(state)

    if is_maximizing:
        best = float('inf')
        for child in neighbors:
            val = minimax(child, depth - 1, False)
            best = min(best, val)  # minimize heuristic
        return best
    else:
        worst = float('-inf')
        for child in neighbors:
            val = minimax(child, depth - 1, True)
            worst = max(worst, val)  # simulate bad move
        return worst

# Choose best move for current state
def best_move(state, depth):
    moves = get_neighbors(state)
    best_state = None
    best_val = float('inf')

    for move in moves:
        val = minimax(move, depth - 1, False)
        if val < best_val:
            best_val = val
            best_state = move
    return best_state, best_val

# Play game step-by-step
def play_game(initial_state, depth=3):
    state = copy.deepcopy(initial_state)
    step = 1
    print("Initial State:")
    print_state(state)

    while state != goal_state and step <= 20:
        print(f"Step {step}:")
        next_state, heuristic = best_move(state, depth)
        print_state(next_state)
        state = next_state
        if state == goal_state:
            print("✅ Goal Reached!")
            break
        step += 1

# Example Start
initial_state = [
    [1, 2, 3],
    [7, 4, 6],
    [5, 0, 8]
]

play_game(initial_state, depth=3)
