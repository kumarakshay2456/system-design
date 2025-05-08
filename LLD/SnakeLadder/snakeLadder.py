import random
from collections import deque


class Snake:
    def __init__(self, head, tail):
        self.head = head
        self.tail = tail


class Ladder:
    def __init__(self, start, end):
        self.start = start
        self.end = end


class Player:
    def __init__(self, name):
        self.name = name
        self.position = 0


class Dice:
    def roll(self):
        return random.randint(1, 6)


class Board:
    def __init__(self, size, snakes, ladders):
        self.size = size
        self.snakes = {snake.head: snake.tail for snake in snakes}
        self.ladders = {ladder.start: ladder.end for ladder in ladders}


class Game:
    def __init__(self, board, players):
        self.board = board
        self.players = deque(players)
        self.dice = Dice()

    def move_player(self, player, value):
        initial = player.position
        new_pos = player.position + value

        if new_pos > self.board.size:
            return

        # Apply snake or ladder
        while new_pos in self.board.snakes or new_pos in self.board.ladders:
            if new_pos in self.board.snakes:
                print(f"{player.name} got bitten by snake from {new_pos} to {self.board.snakes[new_pos]}")
                new_pos = self.board.snakes[new_pos]
            elif new_pos in self.board.ladders:
                print(f"{player.name} climbed ladder from {new_pos} to {self.board.ladders[new_pos]}")
                new_pos = self.board.ladders[new_pos]

        player.position = new_pos
        print(f"{player.name} moved from {initial} to {new_pos}")

    def play(self):
        while True:
            player = self.players.popleft()
            input(f"{player.name}'s turn. Press enter to roll dice.")
            roll = self.dice.roll()
            print(f"{player.name} rolled a {roll}")
            self.move_player(player, roll)

            if player.position == self.board.size:
                print(f"{player.name} wins!")
                break

            self.players.append(player)



if __name__ == "__main__":
    snakes = [Snake(99, 1), Snake(92, 45), Snake(62, 22)]
    ladders = [Ladder(3, 38), Ladder(15, 44), Ladder(50, 90)]

    board = Board(100, snakes, ladders)
    players = [Player("Akshay"), Player("Rahul")]
    game = Game(board, players)

    game.play()