player, opponent = 'x', 'o'

def isMovesLeft(board):
    for i in range(3):
        for j in range(3):
            if board[i][j] == '_':
                return True
    return False

def evaluate(b):
    # Check rows
    for row in range(3):
        if b[row][0] == b[row][1] == b[row][2] != '_':
            return 10 if b[row][0] == player else -10

    # Check columns
    for col in range(3):
        if b[0][col] == b[1][col] == b[2][col] != '_':
            return 10 if b[0][col] == player else -10

    # Check diagonals
    if b[0][0] == b[1][1] == b[2][2] != '_':
        return 10 if b[0][0] == player else -10
    if b[0][2] == b[1][1] == b[2][0] != '_':
        return 10 if b[0][2] == player else -10

    return 0

def minimax(board, depth, isMax):
    score = evaluate(board)

    # Terminal states
    if score == 10 or score == -10:
        return score, None
    if not isMovesLeft(board):
        return 0, None

    if isMax:
        bestVal = -1000
        bestMove = None
        for i in range(3):
            for j in range(3):
                if board[i][j] == '_':
                    board[i][j] = player
                    val, _ = minimax(board, depth + 1, False)
                    board[i][j] = '_'
                    if val > bestVal:
                        bestVal = val
                        bestMove = (i, j)
        return bestVal, bestMove
    else:
        bestVal = 1000
        bestMove = None
        for i in range(3):
            for j in range(3):
                if board[i][j] == '_':
                    board[i][j] = opponent
                    val, _ = minimax(board, depth + 1, True)
                    board[i][j] = '_'
                    if val < bestVal:
                        bestVal = val
                        bestMove = (i, j)
        return bestVal, bestMove

def print_board(board):
    for row in board:
        print(' '.join(row))
    print()

def simulate_optimal_game(start_board, start_turn='x'):
    """
    Simulate full game from start_board assuming both players play optimally.
    start_turn: 'x' or 'o' (who moves next)
    """
    board = [row[:] for row in start_board]
    current = start_turn
    move_number = 1

    print("Initial board:")
    print_board(board)

    while True:
        score = evaluate(board)
        if score == 10:
            print("Result: 'x' (player) wins")
            return
        if score == -10:
            print("Result: 'o' (opponent) wins")
            return
        if not isMovesLeft(board):
            print("Result: Draw")
            return

        if current == player:
            val, move = minimax(board, 0, True)
            actor = "Player (x)"
        else:
            val, move = minimax(board, 0, False)
            actor = "Opponent (o)"

        if move is None:
            # No move possible (shouldn't happen because we checked moves left)
            print("No move returned by minimax; terminating.")
            return

        i, j = move
        board[i][j] = current
        print(f"Move {move_number}: {actor} plays at ({i}, {j}) → score estimate: {val}")
        print_board(board)

        # swap player
        current = opponent if current == player else player
        move_number += 1

# Example usage: start board from your previous input
if __name__ == "__main__":
    # Example starting board (same as your driver code)
    board = [
        ['x', '', 'o'],
        ['o', 'x', 'x'],
        ['o_', '_', '_']
    ]
    # If you want 'x' to move next:
    simulate_optimal_game(board, start_turn='x')

    # If you want to start from a different partial position, change `board` accordingly.
