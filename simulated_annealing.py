from datetime import datetime
import random, math
import decimal

class Board:
    def __init__(self, queen_count=4):  # Changed to 4 queens
        self.queen_count = queen_count
        self.reset()

    def reset(self):
        self.queens = [-1 for i in range(self.queen_count)]
        for i in range(self.queen_count):
            self.queens[i] = random.randint(0, self.queen_count - 1)

    def calculateCost(self):
        threat = 0
        for queen in range(self.queen_count):
            for next_queen in range(queen + 1, self.queen_count):
                if (self.queens[queen] == self.queens[next_queen] or
                        abs(queen - next_queen) == abs(self.queens[queen] - self.queens[next_queen])):
                    threat += 1
        return threat

    @staticmethod
    def calculateCostWithQueens(queens):
        threat = 0
        queen_count = len(queens)
        for queen in range(queen_count):
            for next_queen in range(queen + 1, queen_count):
                if (queens[queen] == queens[next_queen] or
                        abs(queen - next_queen) == abs(queens[queen] - queens[next_queen])):
                    threat += 1
        return threat

    @staticmethod
    def toString(queens):
        return "\n".join(f"({row}, {col})" for row, col in enumerate(queens))

    @staticmethod
    def printBoard(queens):
        size = len(queens)
        for row in range(size):
            line = ""
            for col in range(size):
                if queens[row] == col:
                    line += " Q "
                else:
                    line += " . "
            print(line)
        print("\n")


class SimulatedAnnealing:
    def __init__(self, board):
        self.elapsedTime = 0
        self.board = board
        self.temperature = 4000
        self.sch = 0.99
        self.startTime = datetime.now()

    def run(self):
        board = self.board
        board_queens = self.board.queens[:]
        solutionFound = False

        for k in range(170000):
            self.temperature *= self.sch
            board.reset()
            successor_queens = board.queens[:]

            dw = (Board.calculateCostWithQueens(successor_queens) -
                  Board.calculateCostWithQueens(board_queens))

            exp = decimal.Decimal(math.e) ** (decimal.Decimal(-dw) * decimal.Decimal(self.temperature))

            if dw > 0 or random.uniform(0, 1) < exp:
                board_queens = successor_queens[:]

            if Board.calculateCostWithQueens(board_queens) == 0:
                print("✅ Solution Found!")
                print(Board.toString(board_queens))
                print("\nChessboard:\n")
                Board.printBoard(board_queens)
                self.elapsedTime = self.getElapsedTime()
                print("Success, Elapsed Time: %sms" % str(self.elapsedTime))
                solutionFound = True
                break

        if not solutionFound:
            self.elapsedTime = self.getElapsedTime()
            print("❌ No solution found, Elapsed Time: %sms" % str(self.elapsedTime))

        return self.elapsedTime

    def getElapsedTime(self):
        endTime = datetime.now()
        elapsedTime = (endTime - self.startTime).microseconds / 1000
        return elapsedTime


if __name__ == '__main__':
    board = Board(queen_count=4)  # Initialize for 4 queens
    print("Initial Board (random):")
    Board.printBoard(board.queens)
    SimulatedAnnealing(board).run()
