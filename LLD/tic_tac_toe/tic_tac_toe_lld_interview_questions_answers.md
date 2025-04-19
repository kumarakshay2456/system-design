
# 🎯 Tic Tac Toe LLD – Interview Questions ans Answers

This document includes **frequently asked interview questions** on the Tic Tac Toe Low-Level Design (LLD) and **detailed answers** that show deep understanding of design principles, object-oriented thinking, and extensibility.

---

## ✅ 1. Can you explain your class design for Tic Tac Toe?

### ✅ Answer:
The system is divided into the following key classes:

- **`Game`**: Controls the overall flow of the game including turn switching, move execution, winner detection, and game state.
- **`Board`**: Manages the 2D grid of cells and provides utilities like checking if the board is full or printing the current state.
- **`Cell`**: Represents an individual cell on the board. Contains a `row`, `column`, and optional `Symbol` placed by a player.
- **`Player`**: Each player has a name and a `Symbol` (X or O).
- **`Symbol` (Enum)**: Simple enumeration to differentiate between X and O symbols.

This separation allows each class to have a **single responsibility**, which makes the codebase modular and extensible.

---

## ✅ 2. Why did you separate the `Player` and `Symbol` classes?

### ✅ Answer:
We follow **SRP (Single Responsibility Principle)**. By separating `Player` and `Symbol`:
- The `Player` is responsible for who is playing.
- The `Symbol` is responsible for what mark (X or O) the player uses.

This abstraction allows you to extend the system easily — e.g., add emoji symbols or special tokens without modifying the `Player` class.

---

## ✅ 3. What design patterns are used in your implementation?

### ✅ Answer:
- **Factory Pattern**: Could be used to instantiate different types of `Player` objects (AIPlayer, HumanPlayer) or to assign Symbols dynamically.
- **Strategy Pattern**: Could be used for AI logic (Minimax algorithm) if the game supports bot play.
- **Observer Pattern** (optional): Could notify listeners (like UI or loggers) when game state updates.

---

## ✅ 4. Why does the `Cell` class exist instead of just using a 2D list of characters?

### ✅ Answer:
A `Cell` class encapsulates the complexity of each cell. It lets us:
- Add future features (e.g., timestamp of move, visual highlights, undo operations)
- Maintain consistent behavior through methods like `is_empty()`

This is an example of **encapsulation**, which increases flexibility and testability.

---

## ✅ 5. How would you extend this to support a 4-player game?

### ✅ Answer:
We'd make the `Game` class accept a **list of players** instead of a fixed 2-player structure.

- `self.players: List[Player]`
- `self.current_player_index: int`

We’d also update `check_winner()` logic to be dynamic based on the current player’s symbol.

---

## ✅ 6. How would you support dynamic board sizes like 5x5 or 10x10?

### ✅ Answer:
Make `Board` take a `size` parameter and dynamically create a 2D grid of that size:
```python
self.grid = [[Cell(i, j) for j in range(size)] for i in range(size)]
```

Additionally, we’d generalize win-checking to handle "N in a row" logic based on board size and win condition.

---

## ✅ 7. How would you implement custom win conditions (like 4 in a row)?

### ✅ Answer:
We can pass a `win_length` parameter to the `Game` or `Board` class.

Then, in `check_winner()` logic:
- Count consecutive symbols in each direction (horizontal, vertical, diagonal)
- Check if count >= win_length

This makes the design **configurable and scalable**.

---

## ✅ 8. Why does the `Game` class manage both flow and logic?

### ✅ Answer:
It’s okay for a simple system, but for larger applications:
- We can **refactor** into a `GameEngine` (rules and logic) and a `GameManager` (UI or player interaction).
- This follows **Separation of Concerns** and improves testability.

---

## ✅ 9. How would you persist game state for resume/later play?

### ✅ Answer:
Add a method to serialize the game:
```python
game_state = {
    "players": [...],
    "board": [...],
    "current_turn": ...
}
```

We can use `pickle`, `json`, or store the state in a database.

---

## ✅ 10. How would you expose this logic as a REST API?

### ✅ Answer:
Wrap the logic in a backend framework like **FastAPI** or **Flask**:

- `POST /start` → create a new game
- `POST /move` → play a move
- `GET /state` → fetch current board and status

The core classes remain the same — demonstrating good **separation between business logic and transport layer**.

---

## ✅ 11. How is encapsulation used in this system?

### ✅ Answer:
Encapsulation ensures that:
- Internal state is hidden.
- Modifications are only allowed via methods.

Example: `Cell` only allows setting a symbol if it’s empty:
```python
if cell.is_empty():
    cell.set_symbol(player.symbol)
```

This reduces the chance of bugs and enforces rules cleanly.

---

## ✅ 12. Can you apply SOLID principles here?

### ✅ Answer:

- **S (Single Responsibility)**: `Board`, `Player`, `Game` each have clear responsibilities.
- **O (Open/Closed)**: Adding new players or board sizes doesn’t modify existing logic.
- **L (Liskov)**: You can swap a `Player` subclass (AIPlayer) without breaking the game.
- **I (Interface Segregation)**: Not directly applicable here.
- **D (Dependency Inversion)**: The game depends on abstractions like `Player`, not specific implementations.

---

## ✅ 13. Would it make sense to use inheritance in `Player`?

### ✅ Answer:
Yes. If we plan to introduce:
- `HumanPlayer`: Gets input from CLI/UI
- `AIPlayer`: Calculates move using strategy

We can define an abstract base class:
```python
class Player(ABC):
    @abstractmethod
    def make_move(self, board): ...
```

---

## ✅ 14. How would you unit test this system?

### ✅ Answer:
Tests to write:
- Validate player turn switching.
- Validate win and draw logic.
- Ensure `Cell` enforces "only one move per cell".
- Full game flow: simulate game until win/draw.

Testing ensures your code adheres to contracts and supports refactoring.

---

## ✅ 15. What parts are prone to bugs or require refactoring?

### ✅ Answer:
- `check_winner()` logic: Can be complex and error-prone.
- Board initialization for dynamic sizes.
- Turn switching logic in games with more than 2 players.

These areas need **clear unit tests and modularization**.

---

## ✅ 16. What was the hardest part to design in this LLD?

### ✅ Answer:
Often the `check_winner()` function is hardest, because it must work:
- For all board sizes
- In all directions (horizontal, vertical, diagonals)
- With different win lengths (e.g., 3-in-a-row, 4-in-a-row)

It needs to be optimized and testable.

---

## ✅ 17. If you had more time, what improvements would you make?

### ✅ Answer:
- Add GUI or API layer
- Implement an AI using Minimax
- Add undo feature
- Add multiplayer support via sockets or REST

---

## ✅ 18. How would you integrate an AI player?

### ✅ Answer:
- Inherit from `Player` class
- Implement a `make_move()` method using Minimax or other algorithms
- AI can be passed into the game like any other player

This allows **plug-and-play behavior** using the **Strategy pattern**.

---

