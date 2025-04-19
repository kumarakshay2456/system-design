**📘 What is a UML Class Diagram?**

A **UML (Unified Modeling Language) Class Diagram** is a type of static structure diagram that describes the structure of a system by showing:

• The **classes** in the system

• Their **attributes** and **methods**

• The **relationships** between the classes

**🧩 Classes in the UML Diagram (Tic Tac Toe)**

Here are the main components shown in your UML diagram:

**1. Symbol (Enum)**

    Represents the type of symbol used in the game — either X or O.

**2. Cell**

	• Represents a single cell in the board.
	
	• Attributes: row, col, player_symbol
	
	• Methods: is_empty(), __str__()

**3. Player**

	• Has a name and a symbol (either X or O).

**4. Board**

	• Contains a 2D list of Cell objects.
	
	• Has a size and methods like print_board() and is_full().

**5. Game**

	• Controls the overall gameplay.
	
	• Manages the current turn, the board, and the winner.
	
	• Methods include play_move, check_winner, current_player, switch_turn, and start.


**🔁 Relationship Symbols: What does 1, 2, * mean?**

These numbers denote **cardinality** — how many instances of one class relate to another.

	Symbol Meaning
	
        1 Exactly one
        
        2 Exactly two
        
        * Zero or more (many)

**Examples from your UML:**

1. Game → Player [2]

	👉 A Game object has **exactly 2** Player objects.

2. Game → Board [1]

	👉 A Game object has **one** Board.

3. Board → Cell [*]

	👉 A Board object contains **many** Cell objects (specifically a 2D grid).

4. Cell → Symbol [1]

	👉 A Cell can contain **at most one** Symbol (X or O). If the cell is empty, it may be None.

5. Player → Symbol [1]

	👉 Each Player has **exactly one** Symbol.


**💡 Summary**

This diagram helps visualize:

	• The structure of the Tic Tac Toe game.

	• The responsibilities of each class.

	• The relationships and multiplicity between objects in the system.

  