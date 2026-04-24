class Book:
    def __init__(self, title, author, isbn) -> None:
        self.title = title
        self.author = author
        self.isbn = isbn
        self.available = True
    
    def __str__(self) -> str:
        return f"Book {self.title} , author {self.author} , isbn {self.isbn} and available {self.available}"

class Library:
    def __init__(self):
        self.books = []
    
    def add_book(self, book):
        self.books.append(book)
        print(f"Book is added -> {book}")
    
    def borrow_book(self, isbn, user):
        for book in self.books:
            if book.isbn == isbn and book.available:
                book.available = False
                user.borrow_book(book)
                print(f"{user.name} borrowd {book}")
                return
        print(f"Book with ISBN {isbn} is not avilable")
    
    def return_book(self, isbn, user):
        for book in self.books:
            if book.isbn == isbn and not book.available:
                book.available = True
                user.return_book(book)
                print(f"{user.name} returned {book}")
                return
        print(f"Book with this ISBN {isbn} is not matched with the library book")
    
    def __str__(self) -> str:
        return f"Library books -> {self.books}"
    

class User:
    def __init__(self, name) -> None:
        self.name = name
        self.borrowed_book = []
    
    def borrow_book(self, book):
        self.borrowed_book.append(book)
    
    def return_book(self, book):
        self.borrowed_book.remove(book)
    
    def __str__(self) -> str:
        return f"User -> {self.name} has borrowed these books ->  {self.borrowed_book}"



library = Library()
book1 = Book("TOC", "PeterLinz", "1233")
book2 = Book("DBMS", "Korth", "10033")
library.add_book(book1)
library.add_book(book2)

user1 = User("Akshay")
user2 = User("abhay")

library.borrow_book("1233", user1)
library.borrow_book("1233", user2)