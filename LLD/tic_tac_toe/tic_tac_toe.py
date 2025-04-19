from enum import Enum
from typing import List, Optional


class Symbol(Enum):
    X = "X"
    O = "O"


class Cell:
    def __init__(self, row: int, col: int):
        self.row = row
        self.col = col
        self.player_symbol: Optional[Symbol] = None

    def is_empty(self) -> bool:
        return self.player_symbol is None

    def __str__(self):
        return self.player_symbol.value if self.player_symbol else "-"


class Player:
    def __init__(self, name: str, symbol: Symbol):
        self.name = name
        self.symbol = symbol


class Board:
    def __init__(self, size: int):
        self.size = size
        self.grid: List[List[Cell]] = [[Cell(i, j) for j in range(size)] for i in range(size)]

    def print_board(self):
        for row in self.grid:
            print(" | ".join(str(cell) for cell in row))
        print()

    def is_full(self) -> bool:
        return all(cell.player_symbol is not None for row in self.grid for cell in row)


class Game:
    def __init__(self, player1: Player, player2: Player, size: int = 3):
        self.board = Board(size)
        self.players = [player1, player2]
        self.current_player_index = 0
        self.winner: Optional[Player] = None

    def switch_turn(self):
        self.current_player_index = 1 - self.current_player_index

    def play_move(self, row: int, col: int) -> bool:
        cell = self.board.grid[row][col]
        if not cell.is_empty():
            print("Cell already taken. Try again.")
            return False
        cell.player_symbol = self.current_player().symbol
        if self.check_winner(row, col):
            self.winner = self.current_player()
        self.switch_turn()
        return True

    def current_player(self) -> Player:
        return self.players[self.current_player_index]

    def check_winner(self, row: int, col: int) -> bool:
        symbol = self.board.grid[row][col].player_symbol
        size = self.board.size

        # Check row
        if all(self.board.grid[row][j].player_symbol == symbol for j in range(size)):
            return True
        # Check column
        if all(self.board.grid[i][col].player_symbol == symbol for i in range(size)):
            return True
        # Check main diagonal
        if row == col and all(self.board.grid[i][i].player_symbol == symbol for i in range(size)):
            return True
        # Check anti-diagonal
        if row + col == size - 1 and all(self.board.grid[i][size - 1 - i].player_symbol == symbol for i in range(size)):
            return True
        return False

    def start(self):
        print("Starting the game!")
        while not self.board.is_full() and not self.winner:
            self.board.print_board()
            player = self.current_player()
            print(f"{player.name}'s turn ({player.symbol.value}):")
            try:
                row = int(input("Enter row: "))
                col = int(input("Enter col: "))
            except ValueError:
                print("Invalid input.")
                continue

            if 0 <= row < self.board.size and 0 <= col < self.board.size:
                if not self.play_move(row, col):
                    continue
            else:
                print("Invalid position.")
        self.board.print_board()
        if self.winner:
            print(f"{self.winner.name} wins!")
        else:
            print("It's a draw!")


if __name__ == "__main__":
    p1 = Player("Akshay", Symbol.X)
    p2 = Player("Anjali", Symbol.O)
    game = Game(p1, p2)
    game.start()