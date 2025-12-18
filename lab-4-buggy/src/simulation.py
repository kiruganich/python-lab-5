import random
import logging
from typing import List, Callable
from src.models import Library, Book
from src.constants import TITLES, AUTHORS, GENRES

logger = logging.getLogger(__name__)

INITIAL_BOOKS = [
    Book("Foundation", "Isaac Asimov", 1951, "Science", "ISBN-0001"),
    Book("Cosmos", "Carl Sagan", 1980, "Science", "ISBN-0002"),
    Book("2001: A Space Odyssey", "Arthur C. Clarke", 1968, "Fiction", "ISBN-0003"),
]


class LibrarySimulator:
    
    def __init__(self, library: Library):
        self.library = library
        self.step_count = 0
        self.events: List[Callable] = [
            self.event_add_book,
            self.event_remove_book,
            self.event_search_by_author,
            self.event_search_by_year,
            self.event_search_invalid_isbn,
            self.event_search_by_genre,
        ]
        logger.info(f"Simulator initialized with {len(self.events)} event types")
    
    def run_step(self) -> str:
        self.step_count += 1
        
        # Случайно выбрать событие
        event = random.choice(self.events)
        result = event()
        
        return f"[Step {self.step_count}] {result}"
    
    def event_add_book(self) -> str:
        title = random.choice(TITLES)
        author = random.choice(AUTHORS)
        year = random.randint(1950, 2024)
        genre = random.choice(GENRES)
        isbn = f"ISBN-{random.randint(1000, 999999):06d}"
        
        book = Book(title, author, year, genre, isbn)
        self.library.add_book(book)
        return f"Added new book: {book}"
    
    def event_remove_book(self) -> str:
        books = list(self.library.books)
        if not books:
            return "Cannot remove: library is empty"
        
        # ! ОШИБКА 3: изменение коллекции во время итерации !
        book_to_remove = random.choice(books)
        self.library.remove_book(book_to_remove.isbn)
        return f"Removed book: {book_to_remove}"
    
    def event_search_by_author(self) -> str:
        if not list(self.library.books):
            return "Cannot search: library is empty"
        
        author = random.choice(AUTHORS)
        results = self.library.search_by_author(author)
        return f"Search by author '{author}': found {len(results)} book(s)"
    
    def event_search_by_year(self) -> str:
        year = random.randint(1950, 2024)
        results = self.library.search_by_year(year)
        return f"Search by year {year}: found {len(results)} book(s)"
    
    def event_search_invalid_isbn(self) -> str:
        isbn = f"ISBN-{random.randint(1000, 999999):06d}"
        book = self.library.search_by_isbn(isbn)
        if book is None:
            return f"Search by ISBN '{isbn}': NOT FOUND (expected behavior)"
        return f"Search by ISBN '{isbn}': found {book}"
    
    def event_search_by_genre(self) -> str:
        genre = random.choice(GENRES)
        results = self.library.search_by_genre(genre)
        return f"Search by genre '{genre}': found {len(results)} book(s)"


def run_simulation(steps: int = 20, seed: int = None) -> None:
    if seed is not None:
        random.seed(seed)
    
    lib = Library("Central Library")
    
    # Добавить начальные книги
    for book in INITIAL_BOOKS:
        lib.add_book(book)
    
    sim = LibrarySimulator(lib)
    
    print("\n" + "=" * 70)
    print(f"LIBRARY SIMULATION: {steps} steps")
    print("=" * 70 + "\n")
    
    logger.info(f"Simulation started with seed={seed}")
    
    # Запустить симуляцию
    for _ in range(steps):
        result = sim.run_step()
        print(result)
        logger.info(result)
    
    # Финальная статистика
    stats = lib.get_statistics()
    print("\n" + "=" * 70)
    print("FINAL STATISTICS:")
    print("=" * 70)
    print(f"Total books: {stats['total_books']}")
    print(f"Unique authors: {stats['unique_authors']}")
    if stats['year_range']:
        print(f"Year range: {stats['year_range'][0]} - {stats['year_range'][1]}")
    print(f"Genres: {', '.join(stats['genres'])}")
    print("=" * 70)
    
    logger.info("Simulation completed")