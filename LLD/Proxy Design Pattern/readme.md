# 🔁 Proxy Design Pattern

## 🎯 Intent

**Provide a surrogate or placeholder for another object to control access to it.**

Imagine you want to access a resource (say, a large image file, a database, or a remote server). Direct access might be slow, costly, or require additional steps like authentication. Instead, you introduce a proxy object that:

- Looks like the real object (i.e., implements the same interface)
- Adds extra functionality before or after delegating to the real object

## 🏗️ Structure

Here's how the proxy pattern is structured:

```
Client → Proxy → RealSubject (Actual Object)
```

### Key Components

1. **Subject**: An interface that both the RealSubject and Proxy implement.
2. **RealSubject**: The actual object that does the real work.
3. **Proxy**: Controls access to the RealSubject. It implements the same interface and may:
    - Instantiate the real object lazily
    - Log requests
    - Enforce security
    - Cache results

## 🧠 Analogy

Think of a proxy server between your browser and the internet:

- You (client) send requests to the proxy server.
- The proxy may log the request, check permissions, cache responses, etc.
- Only then does it forward the request to the actual website (real object).

## 🔍 Types of Proxies

| Type                 | Purpose                                                                            |
| -------------------- | ---------------------------------------------------------------------------------- |
| **Virtual Proxy**    | Delays object creation until it's absolutely needed                                |
| **Protection Proxy** | Controls access to sensitive objects based on permissions                          |
| **Remote Proxy**     | Interacts with an object located in a different address space (e.g., network, RPC) |
| **Smart Proxy**      | Adds extra actions like logging, reference counting, etc.                          |

## 🧪 Implementation Example: Virtual Proxy

Suppose we have an expensive-to-load image (like loading from disk or downloading from the web).

```python
from abc import ABC, abstractmethod

# Common interface
class Image(ABC):
    @abstractmethod
    def display(self):
        pass

# Real subject
class RealImage(Image):
    def __init__(self, filename):
        self.filename = filename
        self.load_from_disk()

    def load_from_disk(self):
        print(f"[RealImage] Loading {self.filename} from disk...")

    def display(self):
        print(f"[RealImage] Displaying {self.filename}")

# Proxy class
class ProxyImage(Image):
    def __init__(self, filename):
        self.filename = filename
        self._real_image = None

    def display(self):
        if self._real_image is None:
            print("[ProxyImage] RealImage not created yet. Creating now...")
            self._real_image = RealImage(self.filename)
        else:
            print("[ProxyImage] RealImage already created.")
        self._real_image.display()

# Client code
print("Creating proxy...")
image = ProxyImage("large_photo.png")

print("\nFirst display call:")
image.display()  # Loads from disk and displays

print("\nSecond display call:")
image.display()  # Only displays, doesn't load again
```

### Expected Output

```
Creating proxy...

First display call:
[ProxyImage] RealImage not created yet. Creating now...
[RealImage] Loading large_photo.png from disk...
[RealImage] Displaying large_photo.png

Second display call:
[ProxyImage] RealImage already created.
[RealImage] Displaying large_photo.png
```

## ⚙️ Real-World Use Cases

- **Database connections**: A proxy can open a DB connection only when needed
- **File download**: Delay download until the file is accessed (lazy-loading)
- **Security**: Only allow authorized users to access a resource (e.g., admin panel)
- **Web scraping tools**: Proxy object can hide identity (anonymize IP)
- **Remote APIs / RPC**: In distributed systems, proxies act as local stubs for remote services

## ✅ Advantages

- **Lazy initialization** – create objects only when needed
- **Access control** – add security and permissions
- **Reduced memory usage** – especially with heavy or expensive resources
- **Logging or auditing** – intercept method calls
- **Caching** – store results and avoid expensive operations

## ⚠️ Disadvantages

- **Added complexity**
- **Indirect access** may reduce performance slightly
- **Harder to debug** if the proxy adds too many layers

## 🧵 Summary

|Term|Description|
|---|---|
|**Pattern Type**|Structural|
|**Main Idea**|Proxy controls access to the real object|
|**Key Benefit**|Can add logging, security, lazy loading, or caching around real objects|
|**Real Examples**|ORM lazy loading, service stubs, image loading in apps|

## 📊 UML Diagram

Here's a UML class diagram representing the Proxy Design Pattern:

```
       +---------------+
       |   Subject     |<-----------------------------+
       | (Interface)   |                              |
       +---------------+                              |
         ^           ^                                |
         |           |                                |
+----------------+  +----------------+         +---------------------+
|   RealSubject  |  |     Proxy      |         |      Client         |
+----------------+  +----------------+         +---------------------+
| - realData     |  | - realSubject  |         | - subject: Subject  |
| + request()    |  | + request()    |         | + doSomething()     |
+----------------+  +----------------+         +---------------------+
                         |
                         | uses
                         v
                 +----------------+
                 |   RealSubject  |
                 +----------------+
```

### 🔍 Diagram Breakdown

- **Subject (Interface)**: Defines a common interface (`request()`) for both RealSubject and Proxy
- **RealSubject**: The actual implementation with real logic
- **Proxy**: Controls access to RealSubject. Implements Subject
- **Client**: Uses Subject to interact with either the Proxy or RealSubject

## 🌍 Real-World Example: Proxy Pattern in Django

In Django, the Proxy Pattern appears in several ways. Let's cover two important ones:

### ✅ 1. Django Model Proxy (Built-in Use)

Django supports model proxies, where you subclass a model without creating a new database table. Instead, you add behavior (like custom ordering or methods).

```python
# models.py
from django.db import models

class User(models.Model):
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name

# Proxy model
class ActiveUserProxy(User):
    class Meta:
        proxy = True
        ordering = ['name']
    
    def greet(self):
        return f"Hello {self.name}, welcome back!"
```

**How it fits the Proxy Pattern:**

- `ActiveUserProxy` is a proxy for `User` — no new table is created
- It extends behavior (adds `greet()` method) without changing the actual object or schema
- Acts like `User` everywhere else

### ✅ 2. Access-Control Proxy for Views (Custom Example)

You can write a proxy-like decorator to control access to Django views.

**Example: Logging and Auth Proxy**

```python
# proxy_decorator.py
from functools import wraps
from django.http import HttpResponseForbidden

def view_proxy(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        print(f"[LOG] Accessing {func.__name__} by user: {request.user}")
        
        if not request.user.is_authenticated:
            return HttpResponseForbidden("Access Denied")
        
        return func(request, *args, **kwargs)
    return wrapper

# views.py
from django.http import HttpResponse
from .proxy_decorator import view_proxy

@view_proxy
def dashboard_view(request):
    return HttpResponse("Welcome to your dashboard.")
```

**How it fits the Proxy Pattern:**

- The decorator is a proxy for the real view
- It intercepts access, logs the request, and performs access control
- The client (browser) only sees the final result, unaware of the proxy logic

### 🔁 Django Proxy Pattern Summary

|Feature|Proxy Pattern Role|
|---|---|
|**Django model proxy**|Subclass of model adds behavior|
|**View decorator as proxy**|Controls access before calling view|
|**ORM lazy loading**|Virtual proxy for related objects|
|**Cached API wrappers**|Smart proxy caching expensive calls|

## 🔗 Related Patterns

- **Decorator Pattern**: Adds behavior to objects without altering structure
- **Adapter Pattern**: Makes incompatible interfaces work together
- **Facade Pattern**: Provides a simplified interface to a complex subsystem

## 📚 Further Reading

- Design Patterns: Elements of Reusable Object-Oriented Software (Gang of Four)
- Head First Design Patterns
- Refactoring Guru - Proxy Pattern
- Django Documentation - Model Proxy

---