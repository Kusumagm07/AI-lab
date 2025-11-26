import random

class TicTacToe:
    def __init__(self):
        self.board = [' ' for _ in range(9)] # 3x3 board as a list
        self.current_winner = None # Track the winner
       
    def print_board(self):
        # Print the current board state
        for row in [self.board[i*3:(i+1)*3] for i in range(3)]:
            print('| ' + ' | '.join(row) + ' |')
           
    @staticmethod
    def print_board_nums():
        # Show which numbers correspond to which positions
        number_board = [[str(i) for i in range(j*3, (j+1)*3)] for j in range(3)]
        for row in number_board:
            print('| ' + ' | '.join(row) + ' |')
           
    def available_moves(self):
        # Return list of available moves (empty squares)
        return [i for i, spot in enumerate(self.board) if spot == ' ']
   
    def empty_squares(self):
        return ' ' in self.board
   
    def num_empty_squares(self):
        return self.board.count(' ')
   
    def make_move(self, square, letter):
        # Make a move if valid, return True if valid
        if self.board[square] == ' ':
            self.board[square] = letter
            if self.winner(square, letter):
                self.current_winner = letter
            return True
        return False
   
    def winner(self, square, letter):
        # Check if the latest move resulted in a win
        row_ind = square // 3
        row = self.board[row_ind*3 : (row_ind+1)*3]
        if all([spot == letter for spot in row]):
            return True
       
        col_ind = square % 3
        column = [self.board[col_ind+i*3] for i in range(3)]
        if all([spot == letter for spot in column]):
            return True
       
        # Check diagonals
        if square % 2 == 0: # only diagonal positions are even (0, 2, 4, 6, 8)
            diagonal1 = [self.board[i] for i in [0, 4, 8]] # top-left to bottom-right
            if all([spot == letter for spot in diagonal1]):
                return True
            diagonal2 = [self.board[i] for i in [2, 4, 6]] # top-right to bottom-left
            if all([spot == letter for spot in diagonal2]):
                return True
       
        return False

def play(game, x_player, o_player, print_game=True):
    # Main game function
    if print_game:
        game.print_board_nums()
       
    letter = 'X' # Starting letter
   
    while game.empty_squares():
        # Get move from appropriate player
        if letter == 'O':
            square = o_player.get_move(game)
        else:
            square = x_player.get_move(game)
           
        if game.make_move(square, letter):
            if print_game:
                print(letter + f' makes a move to square {square}')
                game.print_board()
                print('') # Empty line
               
            if game.current_winner:
                if print_game:
                    print(letter + ' wins!')
                return letter
               
            # Switch players
            letter = 'O' if letter == 'X' else 'X'
           
    if print_game:
        print('It\'s a tie!')
       
class HumanPlayer:
    def __init__(self, letter):
        self.letter = letter
       
    def get_move(self, game):
        valid_square = False
        val = None
        while not valid_square:
            square = input(self.letter + '\'s turn. Input move (0-8): ')
            try:
                val = int(square)
                if val not in game.available_moves():
                    raise ValueError
                valid_square = True
            except ValueError:
                print('Invalid square. Try again.')
        return val

class AIPlayer:
    def __init__(self, letter):
        self.letter = letter
       
    def get_move(self, game):
        if len(game.available_moves()) == 9:
            square = random.choice(game.available_moves()) # Random move if first move
        else:
            # Get the best move using minimax algorithm
            square = self.minimax(game, self.letter)['position']
        return square
   
    def minimax(self, state, player):
        max_player = self.letter # Yourself
        other_player = 'O' if player == 'X' else 'X'
       
        # First check if the previous move is a winner
        if state.current_winner == other_player:
            return {'position': None, 'score': 1 * (state.num_empty_squares() + 1) if other_player == max_player else -1 * (state.num_empty_squares() + 1)}
        elif not state.empty_squares():
            return {'position': None, 'score': 0}
           
        if player == max_player:
            best = {'position': None, 'score': -float('inf')} # Maximize
        else:
            best = {'position': None, 'score': float('inf')} # Minimize
           
        for possible_move in state.available_moves():
            # Step 1: Make a move
            state.make_move(possible_move, player)
           
            # Step 2: Recurse with minimax to simulate game after that move
            sim_score = self.minimax(state, other_player)
           
            # Step 3: Undo the move
            state.board[possible_move] = ' '
            state.current_winner = None
            sim_score['position'] = possible_move
           
            # Step 4: Update the dictionary
            if player == max_player: # Maximizing player
                if sim_score['score'] > best['score']:
                    best = sim_score
            else: # Minimizing player
                if sim_score['score'] < best['score']:
                    best = sim_score
                   
        return best

if __name__ == '__main__':
    # Play against AI
    x_player = HumanPlayer('X')
    o_player = AIPlayer('O')
    t = TicTacToe()
    play(t, x_player, o_player, print_game=True)
