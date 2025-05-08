import random
from collections import deque

class Jump:
    """
    Represents a jump (snake or ladder) on the board.
    """
    def __init__(self):
        self.start = 0
        self.end = 0

class Cell:
    """
    Represents a cell on the Snake and Ladder board.
    """
    def __init__(self):
        self.jump = None

class Dice:
    """
    Represents a dice or multiple dice in the game.
    """
    def __init__(self, dice_count):
        """
        Initialize the dice with a given count.
        
        Args:
            dice_count: The number of dice to use
        """
        self.dice_count = dice_count
        self.min = 1
        self.max = 6
    
    def roll_dice(self):
        """
        Roll the dice to get a random sum.
        
        Returns:
            The sum of all dice rolls
        """
        total_sum = 0
        dice_used = 0
        
        while dice_used < self.dice_count:
            total_sum += random.randint(self.min, self.max)
            dice_used += 1
        
        return total_sum

class Board:
    """
    Represents the game board for Snake and Ladder.
    """
    def __init__(self, board_size, number_of_snakes, number_of_ladders):
        """
        Initialize the board with a given size and number of snakes and ladders.
        
        Args:
            board_size: The size of the board (board will be board_size x board_size)
            number_of_snakes: The number of snakes to place on the board
            number_of_ladders: The number of ladders to place on the board
        """
        self.cells = None
        self.initialize_cells(board_size)
        self.add_snakes_ladders(self.cells, number_of_snakes, number_of_ladders)
    
    def initialize_cells(self, board_size):
        """
        Initialize the cells of the board.
        
        Args:
            board_size: The size of the board
        """
        self.cells = [[Cell() for _ in range(board_size)] for _ in range(board_size)]
    
    def add_snakes_ladders(self, cells, number_of_snakes, number_of_ladders):
        """
        Add snakes and ladders to the board.
        
        Args:
            cells: The cells of the board
            number_of_snakes: The number of snakes to add
            number_of_ladders: The number of ladders to add
        """
        # Add snakes
        while number_of_snakes > 0:
            snake_head = random.randint(1, len(cells) * len(cells) - 2)
            snake_tail = random.randint(1, len(cells) * len(cells) - 2)
            
            if snake_tail >= snake_head:
                continue
            
            snake_obj = Jump()
            snake_obj.start = snake_head
            snake_obj.end = snake_tail
            
            cell = self.get_cell(snake_head)
            cell.jump = snake_obj
            
            number_of_snakes -= 1
        
        # Add ladders
        while number_of_ladders > 0:
            ladder_start = random.randint(1, len(cells) * len(cells) - 2)
            ladder_end = random.randint(1, len(cells) * len(cells) - 2)
            
            if ladder_start >= ladder_end:
                continue
            
            ladder_obj = Jump()
            ladder_obj.start = ladder_start
            ladder_obj.end = ladder_end
            
            cell = self.get_cell(ladder_start)
            cell.jump = ladder_obj
            
            number_of_ladders -= 1
    
    def get_cell(self, player_position):
        """
        Get the cell at the given player position.
        
        Args:
            player_position: The position of the player
            
        Returns:
            The cell at the player's position
        """
        board_row = player_position // len(self.cells)
        board_column = player_position % len(self.cells)
        return self.cells[board_row][board_column]

class Player:
    """
    Represents a player in the game.
    """
    def __init__(self, player_id, current_position):
        """
        Initialize a player with an ID and starting position.
        
        Args:
            player_id: The ID of the player
            current_position: The starting position of the player
        """
        self.id = player_id
        self.current_position = current_position

class Game:
    """
    Represents the Snake and Ladder game.
    """
    def __init__(self):
        """
        Initialize the game.
        """
        self.board = None
        self.dice = None
        self.players_list = deque()
        self.winner = None
        
        self.initialize_game()
    
    def initialize_game(self):
        """
        Initialize the game with a board, dice, and players.
        """
        self.board = Board(10, 5, 4)
        self.dice = Dice(1)
        self.winner = None
        self.add_players()
    
    def add_players(self):
        """
        Add players to the game.
        """
        player1 = Player("p1", 0)
        player2 = Player("p2", 0)
        self.players_list.append(player1)
        self.players_list.append(player2)
    
    def start_game(self):
        """
        Start and play the game until a winner is found.
        """
        while self.winner is None:
            # Check whose turn now
            player_turn = self.find_player_turn()
            print(f"player turn is: {player_turn.id}, current position is: {player_turn.current_position}")
            
            # Roll the dice
            dice_number = self.dice.roll_dice()
            print(f"Rolled a {dice_number}")
            
            # Get the new position
            player_new_position = player_turn.current_position + dice_number
            player_new_position = self.jump_check(player_new_position)
            player_turn.current_position = player_new_position
            
            print(f"player turn is: {player_turn.id}, new Position is: {player_new_position}")
            
            # Check for winning condition
            if player_new_position >= len(self.board.cells) * len(self.board.cells) - 1:
                self.winner = player_turn
        
        print(f"WINNER IS: {self.winner.id}")
    
    def find_player_turn(self):
        """
        Find the player whose turn it is.
        
        Returns:
            The player whose turn it is
        """
        player_turns = self.players_list.popleft()
        self.players_list.append(player_turns)
        return player_turns
    
    def jump_check(self, player_new_position):
        """
        Check if the player lands on a snake or ladder and update the position accordingly.
        
        Args:
            player_new_position: The new position of the player after rolling the dice
            
        Returns:
            The updated position after applying any jumps
        """
        if player_new_position > len(self.board.cells) * len(self.board.cells) - 1:
            return player_new_position
        
        cell = self.board.get_cell(player_new_position)
        if cell.jump is not None and cell.jump.start == player_new_position:
            jump_by = "ladder" if cell.jump.start < cell.jump.end else "snake"
            print(f"jump done by: {jump_by}")
            return cell.jump.end
        
        return player_new_position

def main():
    """
    Main function to run the Snake and Ladder game.
    """
    game = Game()
    game.start_game()

if __name__ == "__main__":
    main()