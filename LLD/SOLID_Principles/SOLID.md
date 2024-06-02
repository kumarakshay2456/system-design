

Solid Principles of OOPS:

**S** -> Single Responsibility Principle
**O** -> Open / Closed Principle
**L** -> Liskov Substitution Principle
**I** -> Interface Segmented Principle
**D** ->  Dependency Inversion Principle




**Advantages of Following these Principles:**

- Help us to write the better code
- Avoid Duplication code
- Easy to maintain
- Easy to understand
- Flexible software
- Reduce Complexity

# 1. Single Responsibility Principle (SRP):

1. **Single Responsibility Principles :**
	1. A class should have only one reason to change - 
		The Single Responsibility Principle (SRP) is one of the five principles of the SOLID framework, which stands for Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, and Dependency Inversion. The SRP states that a class should have only one reason to change, meaning it should have only one job or responsibility. This principle helps in creating more maintainable and understandable code.

### Reason for SRP

The primary reason for adhering to the SRP is to improve the maintainability and flexibility of the code. When a class has only one responsibility, it becomes easier to:

1. **Understand**: It's clear what the class is supposed to do.
2. **Maintain**: Changes to one part of the functionality are localized to one class, reducing the risk of introducing bugs in other parts of the system.
3. **Test**: Smaller, single-responsibility classes are easier to test because there are fewer dependencies and less complex behavior to cover.
4. **Reuse**: Classes with a single responsibility are more likely to be reusable in other contexts because they do one thing and do it well.

### Example of SRP in Python

Consider a simple example of an employee management system. Without SRP, you might have a class that handles both employee details and payroll processing:

```python
class Employee:
    def __init__(self, name, position, salary):
        self.name = name
        self.position = position
        self.salary = salary

    def get_employee_details(self):
        return f"Name: {self.name}, Position: {self.position}"

    def calculate_payroll(self):
        # Dummy payroll calculation
        return self.salary * 0.9  # Deducting 10% as tax
```

In this example, the `Employee` class has two responsibilities:
1. Managing employee details.
2. Calculating payroll.

This violates the SRP because changes in payroll logic (e.g., tax calculation changes) would require changes in the `Employee` class, even though they are unrelated to employee details.

### Refactored Example with SRP

To adhere to the SRP, we can refactor the code into two classes, each with a single responsibility:

```python
class Employee:
    def __init__(self, name, position):
        self.name = name
        self.position = position

    def get_employee_details(self):
        return f"Name: {self.name}, Position: {self.position}"

class Payroll:
    def __init__(self, salary):
        self.salary = salary

    def calculate_payroll(self):
        # Dummy payroll calculation
        return self.salary * 0.9  # Deducting 10% as tax

# Usage
employee = Employee("John Doe", "Software Engineer")
print(employee.get_employee_details())

payroll = Payroll(5000)
print(f"Payroll: {payroll.calculate_payroll()}")
```

In this refactored example:
- The `Employee` class is responsible only for managing employee details.
- The `Payroll` class is responsible only for payroll calculations.

By following the SRP, the code is now more maintainable, easier to understand, and each class has a single reason to change. Changes to the payroll calculation logic will not affect the `Employee` class, and vice versa.








# 2. Open / Closed Principle (OCP): 
Open for extension but closed for modification : 
The Open/Closed Principle (OCP) is another key concept within the SOLID principles. It states that software entities (such as classes, modules, functions, etc.) should be open for extension but closed for modification. This means you should be able to add new functionality to a class or module without altering its existing code.

### Reason for OCP

The main reasons for adhering to the OCP are:

1. **Enhance Stability**: By not modifying existing code, you reduce the risk of introducing new bugs.
2. **Encourage Reusability**: New features can be added without changing the existing codebase, which makes the system more adaptable and reusable.
3. **Facilitate Maintainability**: Adding new features through extensions keeps the existing code intact, making it easier to maintain and understand.

### Example of OCP in Python

Let's consider an example where we have a class that processes different types of payments. Without following the OCP, you might have something like this:

```python
class PaymentProcessor:
    def process_credit_card(self, amount):
        print(f"Processing credit card payment of {amount}")

    def process_paypal(self, amount):
        print(f"Processing PayPal payment of {amount}")

# Usage
processor = PaymentProcessor()
processor.process_credit_card(100)
processor.process_paypal(200)
```

This `PaymentProcessor` class is not closed for modification. If a new payment method (e.g., Bitcoin) needs to be added, we have to modify the `PaymentProcessor` class, violating the OCP.

### Refactored Example with OCP

To adhere to the OCP, we can use polymorphism and create a more flexible design:

```python
from abc import ABC, abstractmethod

class PaymentMethod(ABC):
    @abstractmethod
    def process_payment(self, amount):
        pass

class CreditCardPayment(PaymentMethod):
    def process_payment(self, amount):
        print(f"Processing credit card payment of {amount}")

class PayPalPayment(PaymentMethod):
    def process_payment(self, amount):
        print(f"Processing PayPal payment of {amount}")

# New payment method added without modifying existing code
class BitcoinPayment(PaymentMethod):
    def process_payment(self, amount):
        print(f"Processing Bitcoin payment of {amount}")

class PaymentProcessor:
    def __init__(self):
        self.payment_methods = []

    def add_payment_method(self, payment_method):
        self.payment_methods.append(payment_method)

    def process_payments(self, amount):
        for method in self.payment_methods:
            method.process_payment(amount)

# Usage
processor = PaymentProcessor()
processor.add_payment_method(CreditCardPayment())
processor.add_payment_method(PayPalPayment())
processor.add_payment_method(BitcoinPayment())

processor.process_payments(100)
```

In this refactored example:
- The `PaymentMethod` abstract base class defines a contract for payment methods.
- `CreditCardPayment`, `PayPalPayment`, and `BitcoinPayment` are concrete implementations of `PaymentMethod`.
- The `PaymentProcessor` class processes payments using any added payment method without needing to be modified when a new payment method is added.

By following the OCP, new payment methods can be added by simply creating new classes that implement the `PaymentMethod` interface. The existing `PaymentProcessor` class remains unchanged, demonstrating that the system is open for extension but closed for modification.



# 3. Liskov Substitution Principle (LSP):
 If class B is subtype of class A , then we should be able to replace object of A with B without breaking the behaviour of the program. 
 Subclass should extend the capabilty of parent class not narrow it down.
 ### Liskov Substitution Principle (LSP)

**Definition**: The Liskov Substitution Principle (LSP) states that objects of a superclass should be replaceable with objects of a subclass without altering the correctness of the program. In other words, if class B is a subclass of class A, then objects of type A should be replaceable with objects of type B without affecting the program's behavior.

**Key Points**:
- Subclasses should enhance or extend the functionality of the superclass.
- Subclasses should not override or implement superclass methods in a way that changes the expected behavior of the superclass methods.

### Reasons for LSP

1. **Polymorphism**: LSP is fundamental to achieving polymorphism. It ensures that derived classes can be used interchangeably with their base classes.
2. **Code Reliability**: Adhering to LSP increases the reliability of the code because it guarantees that subclass instances can stand in for superclass instances without causing unexpected behavior.
3. **Maintainability**: Following LSP makes the code more maintainable. When subclasses adhere to the expectations set by their superclasses, the code becomes more predictable and easier to understand.

### Example of LSP in Python

Let's look at an example that violates LSP and then refactor it to adhere to LSP.

**Violation of LSP**:
Consider a `Bird` superclass and a `Penguin` subclass. Suppose the `Bird` class has a method `fly()`, but `Penguin` cannot fly. This violates LSP because substituting a `Bird` with a `Penguin` would break the expected behavior.

```python
class Bird:
    def fly(self):
        return "Flying"

class Penguin(Bird):
    def fly(self):
        raise Exception("Penguins cannot fly")

# Usage
def make_bird_fly(bird: Bird):
    return bird.fly()

sparrow = Bird()
print(make_bird_fly(sparrow))  # Output: Flying

penguin = Penguin()
print(make_bird_fly(penguin))  # Raises Exception: Penguins cannot fly
```

In this example, substituting a `Penguin` for a `Bird` breaks the program's behavior, violating LSP.

**Adhering to LSP**:
To adhere to LSP, we should redesign the classes so that the substitution does not break the behavior. One approach is to introduce an interface or abstract class that better represents the capabilities of different birds.

```python
from abc import ABC, abstractmethod

class Bird(ABC):
    @abstractmethod
    def move(self):
        pass

class FlyingBird(Bird):
    def move(self):
        return "Flying"

class NonFlyingBird(Bird):
    def move(self):
        return "Swimming"

class Sparrow(FlyingBird):
    pass

class Penguin(NonFlyingBird):
    pass

# Usage
def make_bird_move(bird: Bird):
    return bird.move()

sparrow = Sparrow()
print(make_bird_move(sparrow))  # Output: Flying

penguin = Penguin()
print(make_bird_move(penguin))  # Output: Swimming
```

In this refactored example:
- The `Bird` class is now an abstract base class with a method `move()` that represents the general behavior of moving.
- `FlyingBird` and `NonFlyingBird` are subclasses of `Bird` that implement the `move()` method appropriately.
- `Sparrow` and `Penguin` are subclasses of `FlyingBird` and `NonFlyingBird`, respectively.

By designing the classes this way, we ensure that substituting any `Bird` instance with its subclass does not break the expected behavior, thus adhering to the Liskov Substitution Principle.
# 4. Interface Segmented Principle (ISP): 
Interfaces should be such, that client should not implement unnecessary functions they do not need. 
### Interface Segregation Principle (ISP)

**Definition**: The Interface Segregation Principle (ISP) states that no client should be forced to depend on methods it does not use. This means that interfaces should be designed in such a way that clients only need to implement the methods that are relevant to them, rather than being burdened with unnecessary methods.

**Key Points**:
- Create specific interfaces tailored to different clients rather than a single, large interface.
- Ensure that implementing a new interface doesn't force a class to include irrelevant or unused methods.
- By segregating interfaces, you reduce the likelihood of clients needing to implement empty or default methods that serve no purpose for them.

### Reasons for ISP

1. **Increased Cohesion**: By creating smaller, more focused interfaces, each interface is highly cohesive, meaning its methods are closely related in functionality.
2. **Enhanced Flexibility**: Smaller interfaces are easier to implement, modify, and extend. Changes in one interface do not affect clients that do not use that interface.
3. **Improved Maintainability**: Segregated interfaces simplify the understanding and maintenance of the code. Clients only need to be concerned with the methods they actually use.

### Example of ISP in Python

Let's consider an example where we violate the ISP and then refactor it to adhere to ISP.

**Violation of ISP**:
Suppose we have an interface for a printer with several methods. A basic printer might not need all of these methods, but it is forced to implement them anyway.

```python
from abc import ABC, abstractmethod

class Printer(ABC):
    @abstractmethod
    def print(self, document):
        pass
    
    @abstractmethod
    def scan(self, document):
        pass

    @abstractmethod
    def fax(self, document):
        pass

class BasicPrinter(Printer):
    def print(self, document):
        print(f"Printing: {document}")

    def scan(self, document):
        raise NotImplementedError("Scan not supported")

    def fax(self, document):
        raise NotImplementedError("Fax not supported")

# Usage
printer = BasicPrinter()
printer.print("My Document")
# If we call printer.scan("My Document"), it will raise NotImplementedError
```

In this example, the `BasicPrinter` class is forced to implement the `scan` and `fax` methods even though it does not support these functionalities, violating the ISP.

**Adhering to ISP**:
To adhere to ISP, we can create smaller, more specific interfaces.

```python
from abc import ABC, abstractmethod

class Printer(ABC):
    @abstractmethod
    def print(self, document):
        pass

class Scanner(ABC):
    @abstractmethod
    def scan(self, document):
        pass

class Fax(ABC):
    @abstractmethod
    def fax(self, document):
        pass

class BasicPrinter(Printer):
    def print(self, document):
        print(f"Printing: {document}")

class AdvancedPrinter(Printer, Scanner, Fax):
    def print(self, document):
        print(f"Printing: {document}")

    def scan(self, document):
        print(f"Scanning: {document}")

    def fax(self, document):
        print(f"Faxing: {document}")

# Usage
basic_printer = BasicPrinter()
basic_printer.print("My Document")
# basic_printer.scan("My Document")  # This will raise an AttributeError

advanced_printer = AdvancedPrinter()
advanced_printer.print("My Document")
advanced_printer.scan("My Document")
advanced_printer.fax("My Document")
```

In this refactored example:
- We have segregated the `Printer`, `Scanner`, and `Fax` interfaces.
- The `BasicPrinter` class implements only the `Printer` interface, as it should.
- The `AdvancedPrinter` class implements all three interfaces (`Printer`, `Scanner`, and `Fax`).

By following ISP, we ensure that classes are not forced to implement methods they do not need, resulting in a more modular and maintainable codebase.
# 5. Dependency Inversion Principle (DIP):

**Definition**: The Dependency Inversion Principle (DIP) is the last principle of the SOLID framework. It states that high-level modules should not depend on low-level modules. Both should depend on abstractions (e.g., interfaces or abstract classes). Furthermore, abstractions should not depend on details. Details should depend on abstractions.

**Key Points**:
- **High-Level Modules**: These modules contain the business logic or significant components of the application.
- **Low-Level Modules**: These modules perform more specific, detailed tasks (e.g., database operations, utility functions).
- **Abstractions**: These are typically interfaces or abstract classes that define a contract without implementing details.
- **Details**: These are concrete implementations of abstractions.

### Reasons for DIP

1. **Flexibility**: By depending on abstractions, the system becomes more flexible and easier to change. Implementations can be swapped without affecting high-level modules.
2. **Maintainability**: High-level modules are protected from changes in low-level modules, making the code easier to maintain.
3. **Testability**: Depending on abstractions allows for easier testing, as you can substitute real implementations with mocks or stubs.
4. **Decoupling**: This principle reduces the coupling between high-level and low-level modules, leading to a more modular system.

### Example of DIP in Python

Let's illustrate this principle with an example.

**Violation of DIP**:
Consider a scenario where a high-level `OrderService` class depends directly on a low-level `MySQLDatabase` class.

```python
class MySQLDatabase:
    def connect(self):
        print("Connecting to MySQL Database")
    
    def get_order(self, order_id):
        print(f"Fetching order {order_id} from MySQL Database")

class OrderService:
    def __init__(self):
        self.db = MySQLDatabase()
    
    def fetch_order(self, order_id):
        self.db.connect()
        self.db.get_order(order_id)

# Usage
service = OrderService()
service.fetch_order(123)
```

In this example:
- The `OrderService` class depends directly on the `MySQLDatabase` class.
- Any change in the database implementation (e.g., switching to PostgreSQL) would require changes in the `OrderService` class, violating DIP.

**Adhering to DIP**:
To adhere to DIP, we can introduce an abstraction for the database and make the high-level module depend on this abstraction.

```python
from abc import ABC, abstractmethod

class Database(ABC):
    @abstractmethod
    def connect(self):
        pass
    
    @abstractmethod
    def get_order(self, order_id):
        pass

class MySQLDatabase(Database):
    def connect(self):
        print("Connecting to MySQL Database")
    
    def get_order(self, order_id):
        print(f"Fetching order {order_id} from MySQL Database")

class OrderService:
    def __init__(self, db: Database):
        self.db = db
    
    def fetch_order(self, order_id):
        self.db.connect()
        self.db.get_order(order_id)

# Usage
mysql_db = MySQLDatabase()
service = OrderService(mysql_db)
service.fetch_order(123)
```

In this refactored example:
- The `Database` abstract base class defines the contract for database operations.
- The `MySQLDatabase` class implements this contract.
- The `OrderService` class depends on the `Database` abstraction, not on a specific implementation.

By adhering to DIP:
- The `OrderService` class is decoupled from the specific database implementation.
- We can easily switch to another database implementation (e.g., `PostgreSQLDatabase`) without modifying the `OrderService` class.
- Testing becomes easier since we can mock the `Database` interface for unit tests.

**Adding Another Database Implementation**:
Let's add another database implementation to show the flexibility DIP provides.

```python
class PostgreSQLDatabase(Database):
    def connect(self):
        print("Connecting to PostgreSQL Database")
    
    def get_order(self, order_id):
        print(f"Fetching order {order_id} from PostgreSQL Database")

# Usage with PostgreSQL
postgresql_db = PostgreSQLDatabase()
service = OrderService(postgresql_db)
service.fetch_order(456)
```

Now, we can switch the database implementation by simply passing a different instance of the database to the `OrderService` without changing its code, demonstrating the power and flexibility of the Dependency Inversion Principle.