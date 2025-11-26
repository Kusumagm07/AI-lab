import random

def calculate_conflicts(state):
    """Heuristic: count attacking queen pairs"""
    n = len(state)
    conflicts = 0
    for i in range(n):
        for j in range(i + 1, n):
            if state[i] == state[j] or abs(state[i] - state[j]) == abs(i - j):
                conflicts += 1
    return conflicts

def generate_initial_state(n):
    """Place one queen per column, random row"""
    return [random.randint(0, n - 1) for _ in range(n)]

def get_best_neighbor(state):
    """Find the best neighbor (with minimum conflicts)"""
    n = len(state)
    best_state = state[:]
    best_conflicts = calculate_conflicts(state)

    for col in range(n):
        original_row = state[col]
        for row in range(n):
            if row != original_row:
                neighbor = state[:]
                neighbor[col] = row
                conflicts = calculate_conflicts(neighbor)
                if conflicts < best_conflicts:
                    best_conflicts = conflicts
                    best_state = neighbor
    return best_state, best_conflicts

def hill_climbing(n, max_restarts=1000):
    for restart in range(max_restarts):
        current = generate_initial_state(n)
        current_conflicts = calculate_conflicts(current)

        while True:
            neighbor, neighbor_conflicts = get_best_neighbor(current)
            if neighbor_conflicts >= current_conflicts:
                break  # Local minimum (no improvement)
            current, current_conflicts = neighbor, neighbor_conflicts

        if current_conflicts == 0:
            print(f"✅ Solution found after {restart} restarts")
            return current

    print("❌ No solution found within restart limit")
    return None

def print_board(state):
    """Print the chessboard"""
    n = len(state)
    for row in range(n):
        line = ""
        for col in range(n):
            if state[col] == row:
                line += " Q "
            else:
                line += " . "
        print(line)
    print()

# -------------------
# Example Run
# -------------------
n = 4
solution = hill_climbing(n)

if solution:
    print("Solution:", solution)
    print_board(solution)
