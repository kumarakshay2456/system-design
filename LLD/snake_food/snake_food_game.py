import random
import time
import curses
from enum import Enum

class Direction(Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4

class Position:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y


class SnakeNode:
    def __init__(self, position):
        self.position = position
        self.next = None


class Snake:
    def __init__(self, start_position):
        self.head = SnakeNode(start_position)
        self.tail = self.head
        self.direction = Direction.RIGHT
        self.length = 1
    
    def change_direction(self, new_direction):
        # Prevent 180-degree turns
        if (self.direction == Direction.UP and new_direction == Direction.DOWN) or \
           (self.direction == Direction.DOWN and new_direction == Direction.UP) or \
           (self.direction == Direction.LEFT and new_direction == Direction.RIGHT) or \
           (self.direction == Direction.RIGHT and new_direction == Direction.LEFT):
            return
        self.direction = new_direction
    
    def move(self, grow=False):
        new_position = self._get_next_position()
        
        # Create a new node for the head
        new_head = SnakeNode(new_position)
        new_head.next = self.head
        self.head = new_head
        
        # Remove tail if not growing
        if not grow:
            current = self.head
            while current.next != self.tail:
                current = current.next
            current.next = None
            self.tail = current
        else:
            self.length += 1
    
    def _get_next_position(self):
        head_pos = self.head.position
        if self.direction == Direction.UP:
            return Position(head_pos.x, head_pos.y - 1)
        elif self.direction == Direction.DOWN:
            return Position(head_pos.x, head_pos.y + 1)
        elif self.direction == Direction.LEFT:
            return Position(head_pos.x - 1, head_pos.y)
        elif self.direction == Direction.RIGHT:
            return Position(head_pos.x + 1, head_pos.y)
    
    def get_all_positions(self):
        positions = []
        current = self.head
        while current:
            positions.append(current.position)
            current = current.next
        return positions
    
    def is_position_on_snake(self, position):
        current = self.head
        while current:
            if current.position == position:
                return True
            current = current.next
        return False


class Food:
    def __init__(self, position):
        self.position = position


class GameBoard:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.snake = Snake(Position(width // 2, height // 2))
        self.food = self._generate_food()
        self.score = 0
        self.game_over = False
    
    def _generate_food(self):
        while True:
            x = random.randint(1, self.width - 2)
            y = random.randint(1, self.height - 2)
            position = Position(x, y)
            
            # Make sure food doesn't appear on the snake
            if not self.snake.is_position_on_snake(position):
                return Food(position)
    
    def update(self):
        if self.game_over:
            return
        
        # Check if snake will eat food
        next_pos = self.snake._get_next_position()
        will_eat = (next_pos == self.food.position)
        
        # Move the snake
        self.snake.move(grow=will_eat)
        
        # Check collision with walls
        head_pos = self.snake.head.position
        if (head_pos.x <= 0 or head_pos.x >= self.width - 1 or 
            head_pos.y <= 0 or head_pos.y >= self.height - 1):
            self.game_over = True
            return
        
        # Check collision with self
        snake_positions = self.snake.get_all_positions()
        for i in range(1, len(snake_positions)):
            if head_pos == snake_positions[i]:
                self.game_over = True
                return
        
        # Handle food consumption
        if will_eat:
            self.score += 10
            self.food = self._generate_food()


class GameEngine:
    def __init__(self, width, height):
        self.board = GameBoard(width, height)
        self.frame_delay = 0.1  # seconds between frames
    
    def process_input(self, key):
        if key == curses.KEY_UP:
            self.board.snake.change_direction(Direction.UP)
        elif key == curses.KEY_DOWN:
            self.board.snake.change_direction(Direction.DOWN)
        elif key == curses.KEY_LEFT:
            self.board.snake.change_direction(Direction.LEFT)
        elif key == curses.KEY_RIGHT:
            self.board.snake.change_direction(Direction.RIGHT)
    
    def update(self):
        self.board.update()
    
    def is_game_over(self):
        return self.board.game_over
    
    def get_score(self):
        return self.board.score


def main(stdscr):
    # Initialize curses
    curses.curs_set(0)
    stdscr.nodelay(1)
    stdscr.timeout(100)
    
    # Get screen dimensions
    height, width = stdscr.getmaxyx()
    
    # Initialize game
    engine = GameEngine(width, height)
    
    # Game loop
    while not engine.is_game_over():
        # Process input
        try:
            key = stdscr.getch()
            if key != -1:
                engine.process_input(key)
        except Exception:
            pass
        
        # Update game state
        engine.update()
        
        # Render
        stdscr.clear()
        
        # Draw borders
        for x in range(width):
            stdscr.addch(0, x, '#')
            stdscr.addch(height-1, x, '#')
        for y in range(height):
            stdscr.addch(y, 0, '#')
            stdscr.addch(y, width-1, '#')
        
        # Draw snake
        snake_positions = engine.board.snake.get_all_positions()
        for pos in snake_positions:
            try:
                if pos == snake_positions[0]:  # Head
                    stdscr.addch(pos.y, pos.x, '@')
                else:  # Body
                    stdscr.addch(pos.y, pos.x, 'O')
            except curses.error:
                pass
        
        # Draw food
        food_pos = engine.board.food.position
        try:
            stdscr.addch(food_pos.y, food_pos.x, '*')
        except curses.error:
            pass
        
        # Draw score
        score_text = f"Score: {engine.get_score()}"
        try:
            stdscr.addstr(0, width - len(score_text) - 1, score_text)
        except curses.error:
            pass
        
        stdscr.refresh()
        time.sleep(engine.frame_delay)
    
    # Game over
    stdscr.nodelay(0)
    stdscr.clear()
    game_over_text = "GAME OVER"
    final_score_text = f"Final Score: {engine.get_score()}"
    try:
        stdscr.addstr(height // 2, (width - len(game_over_text)) // 2, game_over_text)
        stdscr.addstr(height // 2 + 1, (width - len(final_score_text)) // 2, final_score_text)
        stdscr.addstr(height // 2 + 2, (width - 20) // 2, "Press any key to exit")
    except curses.error:
        pass
    stdscr.refresh()
    stdscr.getch()


if __name__ == "__main__":
    curses.wrapper(main)