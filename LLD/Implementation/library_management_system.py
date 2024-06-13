"""
Library Management System
Requirements:

    1. The system should manage books.
    2. Users should be able to borrow and return books.
    3. Track the borrowed books by each user.

    Classes: 
        Book
        Library
        User
"""


class Book:
    def __init__(self, title, author, isbn) -> None:
        self.title = title
        self.author = author
        self.isbn = isbn
        self.available = True

    def __str__(self) -> str:
        return f'Book(title="{self.title}", author="{self.author}", isbn="{self.isbn}",available={self.available})'


class Library:
    def __init__(self) -> None:
        self.books = []
    
    def add_book(self, book):
        self.books.append(book)
        print(f'Added Book - {book}')
    
    def borrow_book(self, isbn, user):
        for book in self.books:
            if book.isbn == isbn and book.available:
                book.available = False
                user.borrow_book(book)
                print(f"{user.name} borrowed {book}")
                return
        print(f"Book with this ISBN {isbn} is not available")
    
    def return_book(self, isbn, user):
        for book in self.books:
            if book.isbn==isbn and not book.available:
                book.available = True
                user.return_book(book)
                print(f'{user.name} returned {book}')
                return 
        print(f"Book with ISBN {isbn} is not recognized as borrowed")
    
    def __str__(self) -> str:
        return f'Library(books={self.books})'
    

class User:
    def __init__(self, name) -> None:
        self.name=name
        self.borrowed_books = []

    def borrow_book(self, book):
        self.borrowed_books.append(book)

    def return_book(self, book):
        self.borrowed_books.remove(book)

    def __str__(self) -> str:
        return f'User(name="{self.name}", borrowed_books={self.borrowed_books})'
    

# Example usage:
library = Library()

book1 = Book("The Great Gatsby", "F. Scott Fitzgerald", "1234567890")
book2 = Book("1984", "George Orwell", "2345678901")

library.add_book(book1)
library.add_book(book2)

user = User("John Doe")

library.borrow_book("1234567890", user)
library.return_book("1234567890", user)

print(library.__dict__)
print(user.__dict__)