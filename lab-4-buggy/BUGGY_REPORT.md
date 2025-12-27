# ОТЧЁТ ОБ ОШИБКАХ

## Ошибка 1 — сравнение через `is` вместо `==`
`is` проверяет, указывают ли две переменные на **один и тот же объект в памяти**. Для строк это ненадежно, потому что Python может интернировать строки. Для сравнения **значений** нужно использовать `==`.

**Файл:** `src/models.py`  
**Строка:** 30  
**Класс:** `Book`  
**Метод:** `__eq__`

### Код с ошибкой
```python
def __eq__(self, other):
    if not isinstance(other, Book):
        return False
    return self.isbn is other.isbn  # ОШИБКА
```

### Последствия
- Книги с одинаковым ISBN считаются неравными
- Сравнение строк через `is` проверяет идентичность объектов, а не равенство значений
- Ломается логика поиска и сравнения
- Падает тест `test_book_equality`

### Как воспроизвести
```python
book1 = Book("Foundation", "Asimov", 1951, "Science", "ISBN-001")
book2 = Book("Other", "Other", 2000, "Other", "ISBN-001")

print(book1 == book2)  # False вместо True
```

### Исправление
```python
return self.isbn == other.isbn
```


## Ошибка 2 — неверное логическое условие
Условие `book.genre or genre` — это логический оператор `or`. Он вернёт `True`, если:
- `book.genre` истинно (любая непустая строка) **ИЛИ**
- `genre` истинно (любая непустая строка)

**Файл:** `src/models.py`  
**Строка:** 178  
**Класс:** `Library`  
**Метод:** `search_by_genre`

### Код с ошибкой
```python
def search_by_genre(self, genre: str) -> List[Book]:
    result = [book for book in self.books if book.genre or genre] # ОШИБКА
    return result
```

### Последствия
- Метод возвращает все книги независимо от жанра
- Несуществующий жанр даёт ненулевой результат
- Падает тест `test_search_by_genre`

### Как воспроизвести
```python
lib = Library("Test")
lib.add_book(Book("A", "Auth1", 2020, "Science", "ISBN-1"))
lib.add_book(Book("B", "Auth2", 2021, "Fiction", "ISBN-2"))

result = lib.search_by_genre("Biology")
print(len(result))  # 2 вместо 0
```

### Исправление
Правильное условие должно **сравнивать значения**: `book.genre == genre`.
```python
result = [book for book in self.books if book.genre == genre]
```


## Ошибка 3 — некорректная работа после удаления элемента
Метод создаёт **копию** списка (`books = list(self.library.books)`), но затем удаляет книгу из **оригинального** объекта библиотеки. После удаления нет проверки успешности операции. Если удаление не произойдёт (например, ISBN не найден), метод всё равно вернёт успешное сообщение.

**Файл:** `src/simulation.py`  
**Строка:** 59  
**Класс:** `LibrarySimulator`  
**Метод:** `event_remove_book`

### Код с ошибкой
```python
def event_remove_book(self) -> str:
    books = list(self.library.books) 
    if not books:
        return "Cannot remove: library is empty"
    
    book_to_remove = random.choice(books)
    self.library.remove_book(book_to_remove.isbn)
    return f"Removed book: {book_to_remove}"
```

### Последствия
- Нестабильное поведение симуляции
- Возможны ошибки индекса при многократных запусках
- Несогласованность данных между копией и оригиналом коллекции

### Как воспроизвести
```python
for i in range(100):
    run_simulation(steps=50, seed=i)
# Некоторые запуски могут работать нестабильно
```

### Исправление
```python
def event_remove_book(self) -> str:
    books = list(self.library.books)
    if not books:
        return "Cannot remove: library is empty"
    
    book_to_remove = random.choice(books)
    success = self.library.remove_book(book_to_remove.isbn)
    
    if success:
        return f"Removed book: {book_to_remove}"
    else:
        return f"Failed to remove book: {book_to_remove}"
```

## Ошибка 4 — изменяемое значение по умолчанию
Список `[]` создаётся один раз при **определении класса**, а не при каждом создании экземпляра. Все экземпляры класса **используют один и тот же объект**, что приводит к неожиданному поведению.

**Файл:** `src/models.py`  
**Строка:** 41  
**Класс:** `BookCollection`  
**Метод:** `__init__`

### Код с ошибкой
```python
def __init__(self):
    self._books: List[Book] = []
    self._mutable_default = []  # ОШИБКА
```

### Последствия
- `_mutable_default` фактически один и тот же объект для всех экземпляров
- Изменение в одном экземпляре видно в другом

### Как воспроизвести
```python
col1 = BookCollection()
col2 = BookCollection()

col1._mutable_default.append("test")
print(col2._mutable_default)  # ['test']
print(col1._mutable_default is col2._mutable_default)  # True
```

### Исправление (если поле не используется)
```python
def __init__(self):
    self._books: List[Book] = []
```

### Исправление (если поле нужно)
```python
def __init__(self):
    self._books: List[Book] = []
    self._mutable_default = []  # Создаётся при каждом вызове __init__
```


## Ошибка 5 — off-by-one при срезе списка
В Python срезы уже имеют правильные границы:
- `[start:stop]` возвращает элементы с индексом `start` до `stop-1`
- Добавление `+ 1` к `stop` включает лишний элемент


**Файл:** `src/models.py`  
**Строка:** 57  
**Класс:** `BookCollection`  
**Метод:** `__getitem__`

### Код с ошибкой
```python
def __getitem__(self, key: Union[int, slice]) -> Union[Book, List[Book]]:
    if isinstance(key, slice):
        return self._books[key.start : key.stop + 1 : key.step] # ОШИБКА
    return self._books[key]
```

### Последствия
- Срезы возвращают лишний элемент
- `collection[0:2]` возвращает 3 элемента вместо 2
- Возможен выход за границы списка

### Как воспроизвести
```python
bc = BookCollection()
bc.add(Book("B1", "A1", 2001, "Fiction", "ISBN-001"))
bc.add(Book("B2", "A2", 2002, "Science", "ISBN-002"))
bc.add(Book("B3", "A3", 2003, "History", "ISBN-003"))

result = bc[0:2]
print(len(result))  # 3 вместо 2 (включит элемент [2])
```

### Исправление
```python
def __getitem__(self, key: Union[int, slice]) -> Union[Book, List[Book]]:
    return self._books[key]
```

## Кратко про использование отладчика

- Поставить breakpoint на строке с ошибкой
- Запустить проект в режиме Debug
- Использовать пошаговое выполнение (Step Over / Step Into)
- Смотреть локальные переменные и стек вызовов на момент ошибки
- Для ошибок сравнения: проверить значения переменных и тип операции
- Для логических ошибок: пошагово трассировать условия
