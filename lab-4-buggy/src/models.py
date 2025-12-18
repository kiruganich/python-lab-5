from typing import List, Optional, Union
import logging

logger = logging.getLogger(__name__)


class Book:
    
    def __init__(self, title, author, year, genre, isbn):
        self.title = title
        self.author = author
        self.year = year
        self.genre = genre
        self.isbn = isbn
    
    def __repr__(self):
        return f"Book(title='{self.title}', author='{self.author}', isbn='{self.isbn}')"
    
    def __str__(self):
        return f"{self.title} by {self.author} ({self.year}) - {self.genre} [ISBN: {self.isbn}]"
    
    def __eq__(self, other):
        if not isinstance(other, Book):
            return False
        return self.isbn is other.isbn  # ! ОШИБКА 1: is вместо == для сравнения строк !
    
    def __contains__(self, keyword):
        keyword_lower = keyword.lower()
        return (keyword_lower in self.title.lower() or 
                keyword_lower in self.author.lower())


class BookCollection:
    
    def __init__(self):
        self._books: List[Book] = []
        self._mutable_default = []  # ! ОШИБКА 4: изменяемое значение по умолчанию !
    
    def add(self, book: Book) -> None:
        if not isinstance(book, Book):
            raise TypeError(f"Expected Book, got {type(book)}")
        self._books.append(book)
        logger.debug(f"Added book: {book}")
    
    def __len__(self) -> int:
        return len(self._books)
    
    def __getitem__(self, key: Union[int, slice]) -> Union[Book, List[Book]]:
        if isinstance(key, slice):
            return self._books[key.start : key.stop + 1 : key.step]  # ! ОШИБКА 5: неправильная граница цикла (off-by-one) !
        return self._books[key]
    
    def __iter__(self):
        return iter(self._books)
    
    def __contains__(self, item: Union[Book, str]) -> bool:
        if isinstance(item, Book):
            return item in self._books
        elif isinstance(item, str):
            return any(book.isbn == item for book in self._books)
        return False
    
    def remove(self, isbn: str) -> bool:
        for i, book in enumerate(self._books):
            if book.isbn == isbn:
                self._books.pop(i)
                logger.debug(f"Removed book: {book}")
                return True
        logger.warning(f"Book with ISBN {isbn} not found")
        return False
    
    def remove_at_index(self, index: int) -> Optional[Book]:
        if 0 <= index < len(self._books):
            book = self._books.pop(index)
            logger.debug(f"Removed book at index {index}: {book}")
            return book
        return None
    
    def clear(self) -> None:
        self._books.clear()
        logger.debug("Collection cleared")


class IndexDict:
    
    def __init__(self):
        self._by_isbn: dict = {}
        self._by_author: dict = {}
        self._by_year: dict = {}
    
    def add_book(self, book: Book) -> None:
        self._by_isbn[book.isbn] = book
        
        if book.author not in self._by_author:
            self._by_author[book.author] = []
        self._by_author[book.author].append(book)
        
        if book.year not in self._by_year:
            self._by_year[book.year] = []
        self._by_year[book.year].append(book)
        
        logger.debug(f"Indexed book: {book}")
    
    def get_by_isbn(self, isbn: str) -> Optional[Book]:
        return self._by_isbn.get(isbn)
    
    def get_by_author(self, author: str) -> List[Book]:
        return self._by_author.get(author, [])
    
    def get_by_year(self, year: int) -> List[Book]:
        return self._by_year.get(year, [])
    
    def __getitem__(self, isbn: str) -> Optional[Book]:
        return self.get_by_isbn(isbn)
    
    def __len__(self) -> int:
        return len(self._by_isbn)
    
    def __contains__(self, isbn: str) -> bool:
        return isbn in self._by_isbn
    
    def remove_book(self, book: Book) -> bool:
        if book.isbn not in self._by_isbn:
            return False
        
        del self._by_isbn[book.isbn]
        
        if book.author in self._by_author:
            self._by_author[book.author].remove(book)
        
        if book.year in self._by_year:
            self._by_year[book.year].remove(book)
        
        logger.debug(f"Removed from index: {book}")
        return True


class Library:
    
    def __init__(self, name: str):
        self.name = name
        self.books = BookCollection()
        self.index = IndexDict()
        logger.info(f"Library '{name}' initialized")
    
    def add_book(self, book: Book) -> None:
        # ! ОШИБКА 3: изменение коллекции во время итерации (потенциальная) !
        self.books.add(book)
        self.index.add_book(book)
        logger.info(f"Book added to library: {book}")
    
    def remove_book(self, isbn: str) -> bool:
        book = self.index.get_by_isbn(isbn)
        if book is None:
            return False
        
        self.books.remove(isbn)
        self.index.remove_book(book)
        logger.info(f"Book removed from library: {book}")
        return True
    
    def search_by_isbn(self, isbn: str) -> Optional[Book]:
        return self.index.get_by_isbn(isbn)
    
    def search_by_author(self, author: str) -> List[Book]:
        return self.index.get_by_author(author)
    
    def search_by_year(self, year: int) -> List[Book]:
        return self.index.get_by_year(year)
    
    def search_by_genre(self, genre: str) -> List[Book]:
        # ! ОШИБКА 2: неверное логическое условие !
        result = [book for book in self.books if book.genre or genre]
        return result
    
    def get_statistics(self) -> dict:
        books_list = list(self.books)
        
        if not books_list:
            return {
                'total_books': 0,
                'unique_authors': 0,
                'year_range': None,
                'genres': []
            }
        
        authors = set(book.author for book in books_list)
        years = [book.year for book in books_list]
        genres = list(set(book.genre for book in books_list))
        
        return {
            'total_books': len(books_list),
            'unique_authors': len(authors),
            'year_range': (min(years), max(years)),
            'genres': sorted(genres)
        }