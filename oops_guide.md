
# Python OOP Concepts for Low-Level Design

This comprehensive guide covers all essential Python Object-Oriented Programming (OOP) concepts with practical examples to help you prepare for Low-Level Design (LLD) interviews.

## Table of Contents
- [1. Classes and Objects](#1-classes-and-objects)
- [2. Constructors](#2-constructors)
- [3. Instance Variables and Methods](#3-instance-variables-and-methods)
- [4. Class Variables and Methods](#4-class-variables-and-methods)
- [5. Encapsulation](#5-encapsulation)
- [6. Inheritance](#6-inheritance)
- [7. Polymorphism](#7-polymorphism)
- [8. Abstraction](#8-abstraction)
- [9. Magic Methods](#9-magic-methods)
- [10. Static Methods and Class Methods](#10-static-methods-and-class-methods)
- [11. Composition](#11-composition)
- [12. Design Patterns](#12-design-patterns)

---

## 1. Classes and Objects

A **class** is a blueprint for creating objects. An **object** is an instance of a class.

```python
class Car:
    """A simple Car class"""
    
    def __init__(self, brand, model):
        self.brand = brand
        self.model = model
        
    def get_full_name(self):
        return f"{self.brand} {self.model}"
        
    def drive(self):
        print(f"{self.get_full_name()} is driving")

# Creating an object (instance) of the Car class
my_car = Car("Toyota", "Camry")
my_car.drive()  # Output: Toyota Camry is driving
```

**Key Points:**
- Classes are created using the `class` keyword
- Classes can have attributes (variables) and methods (functions)
- Objects are instances of a class created using the class name followed by parentheses

**Real-World Analogy**: A class is like a blueprint for a house, while objects are the actual houses built from that blueprint.

---

## 2. Constructors

A **constructor** is a special method called `__init__` that initializes a new object.

```python
class Dog:
    """A simple Dog class with a constructor"""
    
    def __init__(self, name, breed, age):
        self.name = name
        self.breed = breed
        self.age = age
        print(f"A new dog named {self.name} has been created!")

# The constructor is called when creating a new object
dog1 = Dog("Buddy", "Golden Retriever", 3)  
# Output: A new dog named Buddy has been created!

print(f"{dog1.name} is a {dog1.breed} and is {dog1.age} years old")
# Output: Buddy is a Golden Retriever and is 3 years old
```

**Key Points:**
- The `__init__` method is called automatically when an object is created
- It initializes the object's attributes
- `self` refers to the current instance of the class
- Parameters can be passed to set initial values

---

## 3. Instance Variables and Methods

**Instance variables** are unique to each object. **Instance methods** operate on individual objects.

```python
class BankAccount:
    """A simple bank account class"""
    
    def __init__(self, account_number, owner_name, balance=0):
        self.account_number = account_number
        self.owner_name = owner_name
        self.balance = balance
    
    def deposit(self, amount):
        """Add money to the account"""
        if amount > 0:
            self.balance += amount
            return f"Deposited ${amount}. New balance: ${self.balance}"
        return "Amount must be positive"
    
    def withdraw(self, amount):
        """Remove money from the account if funds are available"""
        if amount > 0:
            if self.balance >= amount:
                self.balance -= amount
                return f"Withdrew ${amount}. New balance: ${self.balance}"
            return "Insufficient funds"
        return "Amount must be positive"

# Create two different bank accounts (objects)
account1 = BankAccount("12345", "Alice", 1000)
account2 = BankAccount("67890", "Bob", 500)

# Each account has its own instance variables
print(account1.balance)  # Output: 1000
print(account2.balance)  # Output: 500

# Using instance methods
print(account1.deposit(500))  # Output: Deposited $500. New balance: $1500
print(account2.withdraw(200))  # Output: Withdrew $200. New balance: $300
```

**Key Points:**
- Instance variables store data unique to each object
- Instance methods can access and modify instance variables using `self`
- Each object maintains its own state independently

---

## 4. Class Variables and Methods

**Class variables** are shared by all instances. **Class methods** operate on the class itself rather than instances.

```python
class Person:
    """A Person class with both instance and class variables"""
    
    species = "Human"  # Class variable shared by all instances
    count = 0  # Counter to track number of Person objects
    
    def __init__(self, name, age):
        self.name = name  # Instance variable
        self.age = age    # Instance variable
        Person.count += 1  # Increment the counter when a new Person is created
    
    def introduce(self):  # Instance method
        return f"Hi, I'm {self.name}, a {self.age}-year-old {Person.species}."
    
    @classmethod
    def get_species(cls):  # Class method
        return cls.species
    
    @classmethod
    def get_count(cls):  # Class method
        return f"There are {cls.count} {cls.species}s created."

# Create Person objects
person1 = Person("Alice", 25)
person2 = Person("Bob", 30)

# Access instance variables and methods
print(person1.name)        # Output: Alice
print(person2.introduce()) # Output: Hi, I'm Bob, a 30-year-old Human.

# Access class variables directly or through class methods
print(Person.species)           # Output: Human
print(Person.get_species())     # Output: Human
print(Person.get_count())       # Output: There are 2 Humans created.

# Class variables can also be accessed through instances
print(person1.species)          # Output: Human
```

**Key Points:**
- Class variables are defined at the class level and shared by all instances
- Class methods can access and modify class variables
- Class methods are defined using the `@classmethod` decorator
- Class methods receive `cls` (the class itself) as their first parameter

**Important Note**: Be careful when modifying class variables through instances, as it can create instance-specific variables that shadow the class variable.

---

## 5. Encapsulation

**Encapsulation** is the bundling of data and methods that operate on that data within a single unit (class), and restricting access to some of the object's components.

```python
class Employee:
    """A class demonstrating encapsulation in Python"""
    
    def __init__(self, name, salary):
        self.name = name             # Public attribute
        self.__salary = salary       # Private attribute (name mangling)
        self._department = "General" # Protected attribute (convention)
    
    def get_salary(self):
        """Getter method for the private salary attribute"""
        return self.__salary
    
    def set_salary(self, new_salary):
        """Setter method for the private salary attribute with validation"""
        if new_salary > 0:
            self.__salary = new_salary
        else:
            print("Salary must be positive")
    
    def _internal_method(self):
        """Protected method (by convention)"""
        print("This is an internal method")
    
    def display_info(self):
        """Public method to display employee information"""
        print(f"Name: {self.name}, Salary: ${self.__salary}, Department: {self._department}")

# Create an Employee object
emp = Employee("John", 50000)

# Access public attribute
print(emp.name)  # Output: John

# Attempt to access private attribute directly
try:
    print(emp.__salary)  # Raises AttributeError
except AttributeError as e:
    print(f"Error: {e}")  # Output: Error: 'Employee' object has no attribute '__salary'

# Access private attribute through getter method
print(emp.get_salary())  # Output: 50000

# Modify private attribute through setter method
emp.set_salary(55000)
print(emp.get_salary())  # Output: 55000

# Access protected attribute (possible but discouraged)
print(emp._department)  # Output: General

# Display employee information
emp.display_info()  # Output: Name: John, Salary: $55000, Department: General
```

**Key Points:**

1. Python implements **name mangling** for privacy (not true encapsulation):
   - `self.__salary` is transformed into `self._Employee__salary` internally
   - This prevents accidental access, but doesn't provide strict access control

2. Python naming conventions for access levels:
   - `self.name`: Public (accessible from anywhere)
   - `self._department`: Protected (should only be accessed within the class and subclasses)
   - `self.__salary`: Private (should only be accessed within the class)

3. Getter and setter methods provide controlled access to private attributes

**Real-World Analogy**: A bank account where direct access to your balance is restricted, but you can deposit or withdraw money through controlled methods.

---

## 6. Inheritance

**Inheritance** allows a class (child/derived class) to acquire properties and behaviors (methods) of another class (parent/base class).

```python
class Vehicle:
    """Base class for all vehicles"""
    
    def __init__(self, brand, model, year):
        self.brand = brand
        self.model = model
        self.year = year
        self.is_running = False
    
    def start_engine(self):
        self.is_running = True
        return f"{self.brand} {self.model}'s engine started"
    
    def stop_engine(self):
        self.is_running = False
        return f"{self.brand} {self.model}'s engine stopped"
    
    def description(self):
        return f"{self.year} {self.brand} {self.model}"


class Car(Vehicle):
    """Car class that inherits from Vehicle"""
    
    def __init__(self, brand, model, year, num_doors):
        # Call the parent class's __init__ method
        super().__init__(brand, model, year)
        # Add car-specific attributes
        self.num_doors = num_doors
        self.wheels = 4
    
    # Override the parent class's description method
    def description(self):
        return f"{super().description()}, {self.num_doors} doors, {self.wheels} wheels"
    
    # Add a car-specific method
    def drive(self):
        if self.is_running:
            return f"The {self.brand} {self.model} is driving smoothly"
        return f"Start the engine first!"


class Motorcycle(Vehicle):
    """Motorcycle class that inherits from Vehicle"""
    
    def __init__(self, brand, model, year, has_sidecar):
        super().__init__(brand, model, year)
        self.has_sidecar = has_sidecar
        self.wheels = 2 if not has_sidecar else 3
    
    def wheelie(self):
        if self.is_running and not self.has_sidecar:
            return f"The {self.brand} {self.model} pops a wheelie!"
        elif self.has_sidecar:
            return f"Can't do a wheelie with a sidecar!"
        else:
            return f"Start the engine first!"


# Create a Car object
my_car = Car("Toyota", "Camry", 2022, 4)
print(my_car.description())  # Output: 2022 Toyota Camry, 4 doors, 4 wheels

# Call method from the parent class
print(my_car.start_engine())  # Output: Toyota Camry's engine started

# Call method specific to the Car class
print(my_car.drive())  # Output: The Toyota Camry is driving smoothly

# Create a Motorcycle object
my_motorcycle = Motorcycle("Harley-Davidson", "Sportster", 2021, False)
	print(my_motorcycle.description())  # Output: 2021 Harley-Davidson Sportster
	print(my_motorcycle.start_engine())  # Output: Harley-Davidson Sportster's engine started
print(my_motorcycle.wheelie())  # Output: The Harley-Davidson Sportster pops a wheelie!
```

**Key Points:**
- Inheritance creates an "is-a" relationship between classes
- Use `super()` to call methods from the parent class
- Child classes can:
  - Inherit methods and attributes from the parent class
  - Override methods from the parent class
  - Add new methods and attributes specific to the child class
- Python supports multiple inheritance (a class can inherit from multiple base classes)

**Types of Inheritance:**
1. **Single inheritance**: A class inherits from one base class
2. **Multiple inheritance**: A class inherits from more than one base class
3. **Multilevel inheritance**: A class inherits from a derived class, creating a parent-child-grandchild relationship
4. **Hierarchical inheritance**: Multiple classes inherit from a single base class

---

## 7. Polymorphism

**Polymorphism** means "many forms" and allows objects of different classes to be treated as objects of a common base class.
or 
Polymorphism means **“many forms”** — in programming, it allows us to call the same method on different objects, and each object responds in its own way.

**Real-life analogy:**

Imagine you have a **Remote Control**. You press the **“power”** button.

• If it’s a **TV**, it turns **on/off** the screen.

• If it’s an **AC**, it turns **on/off** the cooling system.

• If it’s a **Sound System**, it turns **on/off** the music.

👉 Same action (press power button), but different behavior depending on the device.

```python
class Device:
    def turn_on(self):
        print("Turning on the device")

class TV(Device):
    def turn_on(self):
        print("Turning on the TV")

class AC(Device):
    def turn_on(self):
        print("Turning on the Air Conditioner")

class SoundSystem(Device):
    def turn_on(self):
        print("Turning on the Sound System")

# Polymorphism in action
def activate_device(device):
    device.turn_on()

# Create objects
tv = TV()
ac = AC()
sound = SoundSystem()

# Call same method on different objects
activate_device(tv)
activate_device(ac)
activate_device(sound)

""" Ouput - 
Turning on the TV  

Turning on the Air Conditioner  

Turning on the Sound System
"""

```

**Key Points:**
1. **Method Overriding**: When a child class provides a specific implementation of a method that is already defined in its parent class
2. **Duck Typing**: "If it walks like a duck and quacks like a duck, then it must be a duck"
   - Python doesn't check the type of an object, but whether it has the required methods or attributes

**Types of Polymorphism:**
1. **Compile-time polymorphism** (Method Overloading)
   - Python doesn't support traditional method overloading, but it can be simulated using default arguments or `*args` and `**kwargs`
2. **Runtime polymorphism** (Method Overriding)
   - Demonstrated in the example above with the `Shape`, `Circle`, `Rectangle`, and `Square` classes

**Real-World Example**: A TV remote with a power button works the same way regardless of the device (TV, DVD player, etc.) but the actual implementation varies by device.

Both **Method Overloading** and **Method Overriding** are forms of **Polymorphism**, but they differ in **where and how** they are used.

**🔁 1. Method Overloading**

**Same method name**, **different parameters**, **in the same class**.

**✅ Concept:**

In many languages (like Java or C++), you can define multiple methods with the same name but with different arguments.

However, in **Python**, **true method overloading** like in Java is **not supported directly**. But we can **simulate** it using default arguments or *args.

**🧑‍💻 Python Example:**

class Calculator:

    def add(self, a, b=0, c=0):

        return a + b + c

calc = Calculator()

print(calc.add(5))        _# Output: 5_

print(calc.add(5, 3))     _# Output: 8_

print(calc.add(5, 3, 2))  _# Output: 10_


🟢 Same method add() works with 1, 2, or 3 arguments — this is **method overloading (simulated)**.

**🔁 2. Method Overriding**

**Same method name**, **same parameters**, but **defined in parent and child classes** — the child class overrides the parent method.

**✅ Concept:**

Used when a child class wants to provide a **specific implementation** of a method already defined in the parent.

**🧑‍💻 Python Example:**
```python
class Animal:

    def speak(self):

        print("Animal makes a sound")

class Dog(Animal):

    def speak(self):

        print("Dog barks")

class Cat(Animal):

    def speak(self):

        print("Cat meows")

# Method overriding in action_

dog = Dog()

cat = Cat()

dog.speak()  _# Output: Dog barks_

cat.speak()  _# Output: Cat meows_

```



🟢 Dog and Cat override the speak() method of Animal.

**🧠 Summary Table:**

**Concept** **Method Overloading** **Method Overriding**

Where? Same class Parent and child class

Arguments Different number/type Same as parent method

Purpose Add flexibility within the class Customize behavior in child class

Python Support Simulated (via default args / *args) Fully supported

  
---

## 8. Abstraction

**Abstraction** is the concept of hiding complex implementation details and showing only the necessary features of an object.

```python
from abc import ABC, abstractmethod

class PaymentProcessor(ABC):
    """Abstract base class for payment processors"""
    
    @abstractmethod
    def process_payment(self, amount):
        """Process a payment of the given amount"""
        pass
    
    @abstractmethod
    def refund_payment(self, amount):
        """Refund a payment of the given amount"""
        pass
    
    def payment_details(self):
        """Returns payment details (non-abstract method)"""
        return "Generic Payment Processor"


class CreditCardProcessor(PaymentProcessor):
    """Concrete implementation of a credit card payment processor"""
    
    def __init__(self, card_number, expiry_date, cvv):
        self.card_number = card_number
        self.expiry_date = expiry_date
        self.cvv = cvv
    
    def process_payment(self, amount):
        # In a real application, this would interact with a payment gateway
        print(f"Processing credit card payment of ${amount}")
        return f"Payment of ${amount} processed successfully with card ending in {self.card_number[-4:]}"
    
    def refund_payment(self, amount):
        print(f"Processing credit card refund of ${amount}")
        return f"Refund of ${amount} processed successfully to card ending in {self.card_number[-4:]}"
    
    def payment_details(self):
        # Override the base class method
        return f"Credit Card: **** **** **** {self.card_number[-4:]}, Expiry: {self.expiry_date}"


class PayPalProcessor(PaymentProcessor):
    """Concrete implementation of a PayPal payment processor"""
    
    def __init__(self, email):
        self.email = email
    
    def process_payment(self, amount):
        print(f"Processing PayPal payment of ${amount}")
        return f"Payment of ${amount} processed successfully with PayPal account {self.email}"
    
    def refund_payment(self, amount):
        print(f"Processing PayPal refund of ${amount}")
        return f"Refund of ${amount} processed successfully to PayPal account {self.email}"
    
    def payment_details(self):
        return f"PayPal: {self.email}"


# Function that demonstrates abstraction through an interface
def make_payment(processor, amount):
    return processor.process_payment(amount)


# Try to instantiate the abstract base class
try:
    payment_processor = PaymentProcessor()
except TypeError as e:
    print(f"Error: {e}")  # Output: Error: Can't instantiate abstract class PaymentProcessor with abstract methods process_payment, refund_payment

# Create concrete payment processor objects
credit_card = CreditCardProcessor("1234567890123456", "12/25", "123")
paypal = PayPalProcessor("user@example.com")

# Use the same interface for different payment methods
print(make_payment(credit_card, 100))  # Output: Payment of $100 processed successfully with card ending in 3456
print(make_payment(paypal, 75))       # Output: Payment of $75 processed successfully with PayPal account user@example.com

# Access payment details
print(credit_card.payment_details())  # Output: Credit Card: **** **** **** 3456, Expiry: 12/25
print(paypal.payment_details())       # Output: PayPal: user@example.com
```

**Key Points:**
1. **Abstract Base Classes** (ABCs):
   - Cannot be instantiated directly
   - Serve as interfaces/contracts for subclasses
   - Created using the `ABC` class from the `abc` module

2. **Abstract Methods**:
   - Defined using the `@abstractmethod` decorator
   - Have no implementation in the abstract class
   - Must be implemented by concrete subclasses

3. **Concrete Classes**:
   - Implement all abstract methods from their abstract base classes
   - Can be instantiated directly

**Benefits of Abstraction:**
- Reduces complexity by hiding implementation details
- Enhances security by exposing only what's necessary
- Improves maintainability and extensibility
- Ensures consistent interfaces across different implementations

**Real-World Analogy**: A car's steering wheel and pedals provide a simple interface to operate the vehicle without needing to understand the internal combustion engine.

---

## 9. Magic Methods

**Magic Methods** (or dunder methods, short for double underscore) are special methods that add "magic" to your classes, enabling operator overloading and customizing built-in behavior.

```python
class Vector:
    """A 2D vector class with magic methods"""
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __str__(self):
        """Return a string representation for print()"""
        return f"Vector({self.x}, {self.y})"
    
    def __repr__(self):
        """Return a string representation for repr()"""
        return f"Vector({self.x}, {self.y})"
    
    def __eq__(self, other):
        """Vector equality: v1 == v2"""
        if isinstance(other, Vector):
            return self.x == other.x and self.y == other.y
        return False
    
    def __add__(self, other):
        """Vector addition: v1 + v2"""
        if isinstance(other, Vector):
            return Vector(self.x + other.x, self.y + other.y)
        raise TypeError("Can only add another Vector")
    
    def __sub__(self, other):
        """Vector subtraction: v1 - v2"""
        if isinstance(other, Vector):
            return Vector(self.x - other.x, self.y - other.y)
        raise TypeError("Can only subtract another Vector")
    
    def __mul__(self, scalar):
        """Vector scalar multiplication: v * scalar"""
        if isinstance(scalar, (int, float)):
            return Vector(self.x * scalar, self.y * scalar)
        raise TypeError("Can only multiply by a scalar")
    
    def __rmul__(self, scalar):
        """Right vector scalar multiplication: scalar * v"""
        return self.__mul__(scalar)
    
    def __neg__(self):
        """Negation of a vector: -v"""
        return Vector(-self.x, -self.y)
    
    def __abs__(self):
        """Absolute value (magnitude) of a vector: abs(v)"""
        import math
        return math.sqrt(self.x**2 + self.y**2)
    
    def __bool__(self):
        """Boolean value of a vector: bool(v)"""
        return self.x != 0 or self.y != 0
    
    def __len__(self):
        """Length of a vector (always 2 for a 2D vector): len(v)"""
        return 2
    
    def __getitem__(self, key):
        """Index access: v[0], v[1]"""
        if key == 0:
            return self.x
        elif key == 1:
            return self.y
        raise IndexError("Vector index out of range")


# Create vectors
v1 = Vector(3, 4)
v2 = Vector(1, 2)

# String representation
print(v1)          # Output: Vector(3, 4)
print(repr(v2))    # Output: Vector(1, 2)

# Equality
print(v1 == v2)    # Output: False
print(v1 == Vector(3, 4))  # Output: True

# Addition and subtraction
print(v1 + v2)     # Output: Vector(4, 6)
print(v1 - v2)     # Output: Vector(2, 2)

# Scalar multiplication
print(v1 * 2)      # Output: Vector(6, 8)
print(3 * v2)      # Output: Vector(3, 6)

# Negation
print(-v1)         # Output: Vector(-3, -4)

# Magnitude
print(abs(v1))     # Output: 5.0 (√(3² + 4²) = 5)

# Boolean value
print(bool(v1))    # Output: True
print(bool(Vector(0, 0)))  # Output: False

# Length
print(len(v1))     # Output: 2

# Index access
print(v1[0])       # Output: 3
print(v1[1])       # Output: 4
```

**Commonly Used Magic Methods:**

| Method | Description | Usage |
|--------|-------------|-------|
| `__init__` | Constructor | Object creation |
| `__str__` | String representation for humans | `print(obj)`, `str(obj)` |
| `__repr__` | String representation for developers | `repr(obj)` |
| `__eq__`, `__ne__` | Equality and inequality | `obj1 == obj2`, `obj1 != obj2` |
| `__lt__`, `__gt__` | Less than and greater than | `obj1 < obj2`, `obj1 > obj2` |
| `__add__`, `__sub__` | Addition and subtraction | `obj1 + obj2`, `obj1 - obj2` |
| `__mul__`, `__truediv__` | Multiplication and division | `obj * scalar`, `obj / scalar` |
| `__rmul__`, `__rtruediv__` | Right operations | `scalar * obj`, `scalar / obj` |
| `__getitem__`, `__setitem__` | Item access and assignment | `obj[key]`, `obj[key] = value` |
| `__len__` | Length | `len(obj)` |
| `__bool__` | Boolean value | `bool(obj)`, `if obj:` |
| `__call__` | Callable objects | `obj()` |
| `__enter__`, `__exit__` | Context manager | `with obj as x:` |

**Benefits of Magic Methods:**
- Enable operator overloading and intuitive syntax
- Make objects behave like Python's built-in types
- Provide hooks into language features (iteration, context management, etc.)

---

## 10. Static Methods and Class Methods

**Static Methods** and **Class Methods** are special types of methods in Python that don't operate on instances like regular instance methods.

```python
class MathUtils:
    """A utility class with static and class methods"""
    
    PI = 3.14159  # Class variable
    
    def __init__(self):
        """Regular constructor - rarely used with utility classes"""
        self.history = []
    
    def add_to_history(self, result):
        """Instance method - requires an instance of the class"""
        self.history.append(result)
    
    @staticmethod
    def add(a, b):
        """Static method - doesn't need the class or an instance"""
        return a + b
    
    @staticmethod
    def subtract(a, b):
        """Static method - doesn't need the class or an instance"""
        return a - b
    
    @staticmethod
    def multiply(a, b):
        """Static method - doesn't need the class or an instance"""
        return a * b
    
    @classmethod
    def circle_area(cls, radius):
        """Class method - has access to class attributes via cls"""
        return cls.PI * radius * radius
    
    @classmethod
    def circle_circumference(cls, radius):
        """Class method - has access to class attributes via cls"""
        return 2 * cls.PI * radius
    
    @classmethod
    def update_pi(cls, new_pi):
        """Class method - can modify class attributes"""
        cls.PI = new_pi
        return f"PI updated to {cls.PI}"


class ScientificMathUtils(MathUtils):
    """Subclass that inherits from MathUtils"""
    
    PI = 3.141592653589793  # More precise value of PI
    
    @classmethod
    def calculate_sphere_volume(cls, radius):
        """Class method that uses the class's value of PI"""
        return (4/3) * cls.PI * radius**3


# Using static methods without creating an instance
print(MathUtils.add(5, 3))       # Output: 8
print(MathUtils.subtract(10, 4)) # Output: 6
print(MathUtils.multiply(2, 6))  # Output: 12

# Using class methods without creating an instance
print(MathUtils.circle_area(5))          # Output: 78.53975
print(MathUtils.circle_circumference(5)) # Output: 31.4159

# Updating a class variable via a class method
print(MathUtils.update_pi(3.14))  # Output: PI updated to 3.14
print(MathUtils.circle_area(5))   # Output: 78.5 (using updated PI)

# Using inherited class methods with different class variables
print(ScientificMathUtils.PI)  # Output: 3.141592653589793
print(ScientificMathUtils.circle_area(5))  # Output: 78.53981633974483 (using more precise PI)
print(ScientificMathUtils.calculate_sphere_volume(5))  # Output: 523.5987755982989
```

**Key Differences:**

| Feature | Instance Method | Static Method | Class Method |
|---------|----------------|---------------|-------------|
| Decorator | None | `@staticmethod` | `@classmethod` |
| First parameter | `self` (instance) | None | `cls` (class) |
| Requires instance | Yes | No | No |
| Access to instance | Yes | No | No |
| Access to class | Via `self.__class__` | No | Yes, via `cls` |
| Inheritance aware | Yes | No | Yes |

**When to Use Each:**

1. **Instance Methods**:
   - When you need to access or modify instance state
   - When the method's behavior depends on instance attributes

2. **Static Methods**:
   - When the method doesn't need access to instance or class attributes
   - For utility functions that logically belong to the class namespace
   - When the method's behavior is independent of the class

3. **Class Methods**:
   - When you need to access or modify class state
   - For factory methods that create instances of the class
   - When the method needs to be aware of inheritance

**Real-World Example**:
- A `Date` class might have a static method `is_valid_date(year, month, day)` that validates a date without creating a Date object.
- It might also have a class method `from_string(date_str)` that creates a Date instance from a string.

---

## 11. Composition

**Composition** is a design principle where complex objects are built by combining simpler objects, creating a "has-a" relationship rather than an "is-a" relationship (inheritance).

```python
class Engine:
    """A simple engine class"""
    
    def __init__(self, fuel_type, horsepower):
        self.fuel_type = fuel_type
        self.horsepower = horsepower
        self.is_running = False
    
    def start(self):
        if not self.is_running:
            self.is_running = True
            return f"{self.horsepower}HP {self.fuel_type} engine started"
        return "Engine is already running"
    
    def stop(self):
        if self.is_running:
            self.is_running = False