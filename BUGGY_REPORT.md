# ОТЧЁТ ОБ ОШИБКАХ


## Ошибка 1 — сравнение через `is` вместо `==`

**Место:** src/models.py, метод Book.__eq__, строка 25Ы

**Симптом:** Книги с одинаковым ISBN сравниваются как неравные (book1 == book2 возвращает False вместо True)

**Как воспроизвести:**
```python
book1 = Book("Foundation", "Asimov", 1951, "Science", "ISBN-001")
book2 = Book("Other", "Other", 2000, "Other", "ISBN-001")
print(book1 == book2)  # Вывод: False (ожидается True)
```

**Отладка:**
- Установить breakpoint на строку 30 в методе `__eq__`
- В отладчике проверить значения `book1.isbn` и `book2.isbn` — они содержат одинаковые строки
- Выполнить `book1.isbn == book2.isbn` — результат True (равны по значению)
- Выполнить `book1.isbn is book2.isbn` — результат False (разные объекты в памяти)

**Причина:**
Оператор `is` проверяет идентичность объектов (один ли это объект в памяти), а не равенство значений. Для строк это ненадёжно, потому что Python может интернировать строки, и результат зависит от реализации.

**Исправление:**
```python
def __eq__(self, other):
    if not isinstance(other, Book):
        return False
    return self.isbn == other.isbn  # Заменить is на ==
```

**Проверка:**
После исправления `book1 == book2` вернёт True, как ожидается.

**Доказательства:**
![1error](https://github.com/kiruganich/python-lab-5/blob/1344463876f514397e19774adfdb8c677868aa5b/lab-4-buggy/screenshots/1error.png)
![2error](https://github.com/kiruganich/python-lab-5/blob/a2974435ea74181ed1521fcd9349833781740c3d/lab-4-buggy/screenshots/1print.png)




## Ошибка 2 — неверное логическое условие

**Место:** src/models.py, метод Library.search_by_genre, строка 172

**Симптом:** Метод возвращает все книги независимо от жанра; поиск по несуществующему жанру тоже возвращает все книги

**Как воспроизвести:**
```python
lib = Library("Test")
lib.add_book(Book("A", "Auth1", 2020, "Science", "ISBN-1"))
lib.add_book(Book("B", "Auth2", 2021, "Fiction", "ISBN-2"))

result = lib.search_by_genre("Biology")
print(len(result))  # Вывод: 2 (ожидается 0, так как "Biology" отсутствует)
```

**Отладка:**
- Установить breakpoint на строку 172 в list comprehension
- В отладчике посмотреть значение условия `book.genre or genre` для каждой книги
- Для первой книги: `"Science" or "Biology"` -> True (первый операнд непустой)
- Для второй книги: `"Fiction" or "Biology"` -> True (первый операнд непустой)
- Условие всегда True, поэтому все книги добавляются в результат

**Причина:**
Использовано логическое `or` вместо сравнения `==`. Оператор `or` вернёт True, если хотя бы один из операндов истинен. Строки "Science", "Fiction", "Biology" — все непустые (истинные), поэтому выражение всегда True.

**Исправление:**
```python
def search_by_genre(self, genre: str) -> List[Book]:
    result = [book for book in self.books if book.genre == genre]
    return result
```

**Проверка:**
После исправления `lib.search_by_genre("Biology")` вернёт пустой список, `lib.search_by_genre("Science")` вернёт только первую книгу.

**Доказательства:**
- ![2error](https://github.com/kiruganich/python-lab-5/blob/f8125d420d32e0d0d6c5097afb4bee68115fb38b/lab-4-buggy/screenshots/2error.png)
- ![2print](https://github.com/kiruganich/python-lab-5/blob/f8125d420d32e0d0d6c5097afb4bee68115fb38b/lab-4-buggy/screenshots/2print.png)



## Ошибка 3 — некорректная работа после удаления элемента

**Место:** src/simulation.py, метод LibrarySimulator.event_remove_book, строка 58

**Симптом:** Метод печатает "Removed book…" даже если удаление не произошло; может привести к несогласованности данных

**Как воспроизвести:**
```python
lib = Library("Test")
lib.add_book(Book("A", "Auth1", 2020, "Science", "ISBN-1"))

sim = LibrarySimulator(lib)

# Удалить существующую книгу
result1 = sim.event_remove_book()
print(result1)  # "Removed book…" (корректно)

# Попытаться удалить ещё раз (книги нет)
result2 = sim.event_remove_book()
print(result2)  # "Removed book…" (неверно — книги нет)
```

**Отладка:**
- Установить breakpoint на строку 58 в методе `event_remove_book`
- В отладчике проверить значение `self.library.remove_book(book_to_remove.isbn)` — оно возвращает bool (True/False)
- При первом вызове вернёт True, при втором вернёт False
- Однако метод всегда возвращает "Removed book…", игнорируя результат

**Причина:**
Метод вызывает `self.library.remove_book(...)`, которое возвращает True/False, но не проверяет результат. Если удаление не произошло (ISBN не найден), метод всё равно возвращает успешное сообщение.

**Исправление:**
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

**Проверка:**
После исправления второй вызов вернёт "Failed to remove book…", поведение корректно.

**Доказательства:**
- ![3error](https://github.com/kiruganich/python-lab-5/blob/f8125d420d32e0d0d6c5097afb4bee68115fb38b/lab-4-buggy/screenshots/3error.png)
- ![3print](https://github.com/kiruganich/python-lab-5/blob/f8125d420d32e0d0d6c5097afb4bee68115fb38b/lab-4-buggy/screenshots/3print.png)


## Ошибка 4 — изменяемое значение по умолчанию

**Место:** src/models.py, метод BookCollection.__init__, строка 39

**Симптом:** Поле `_mutable_default` разделяется между экземплярами класса; изменение в одном видно в другом

**Как воспроизвести:**
```python
col1 = BookCollection()
col2 = BookCollection()

col1._mutable_default.append("test")

print(col2._mutable_default)  # Вывод: ['test'] (неверно!)
print(col1._mutable_default is col2._mutable_default)  # Вывод: True
```

**Отладка:**
- Установить breakpoint в `__init__` после инициализации `_mutable_default`
- Создать два экземпляра класса, остановиться в каждом
- В отладчике проверить значение `id(col1._mutable_default)` и `id(col2._mutable_default)` — они совпадают (один и тот же объект)
- Изменить один список и проверить другой — изменение видно

**Причина:**
Список `[]` в определении `__init__` создаётся один раз при загрузке класса, а не при каждом вызове `__init__`. Все экземпляры ссылаются на один и тот же объект.

**Исправление:**
Если поле не используется — убрать:
```python
def __init__(self):
    self._books: List[Book] = []
```

Если поле необходимо — оно уже правильно создаётся в `__init__` (в строке `self._books: List[Book] = []`). Убедиться, что любые изменяемые значения создаются внутри `__init__`.

**Проверка:**
После исправления два экземпляра имеют независимые списки, изменение в одном не влияет на другой.

**Доказательства:**
- ![4error](https://github.com/kiruganich/python-lab-5/blob/f8125d420d32e0d0d6c5097afb4bee68115fb38b/lab-4-buggy/screenshots/4error.png)
- ![4print](https://github.com/kiruganich/python-lab-5/blob/f8125d420d32e0d0d6c5097afb4bee68115fb38b/lab-4-buggy/screenshots/4print.png)



## Ошибка 5 — off-by-one при срезе списка

**Место:** src/models.py, метод BookCollection.__getitem__, строка 52

**Симптом:** Срезы возвращают лишний элемент; `collection[0:2]` вернёт 3 элемента вместо 2

**Как воспроизвести:**
```python
bc = BookCollection()
bc.add(Book("B1", "A1", 2001, "Fiction", "ISBN-001"))
bc.add(Book("B2", "A2", 2002, "Science", "ISBN-002"))
bc.add(Book("B3", "A3", 2003, "History", "ISBN-003"))

result = bc[0:2]
print(len(result))  # Вывод: 3 (ожидается 2)
print([b.title for b in result])  # ['B1', 'B2', 'B3'] вместо ['B1', 'B2']
```

**Отладка:**
- Установить breakpoint на строку 57 в методе `__getitem__`
- В отладчике посмотреть значения при срезе `key[0:2]`: `key.start=0`, `key.stop=2`
- Вычисляемый срез: `self._books[0 : 2+1 : None]` -> `self._books[0:3:None]` (включит элементы 0, 1, 2)
- Ожидаемый срез: `self._books[0:2:None]` -> элементы 0, 1

**Причина:**
В Python срез `[start:stop]` включает элементы от `start` до `stop-1` (stop не включается). Добавление `+1` к stop нарушает эту семантику и включает лишний элемент.

**Исправление:**
```python
def __getitem__(self, key: Union[int, slice]) -> Union[Book, List[Book]]:
    return self._books[key]  # Просто вернуть срез без переопределения семантики
```

**Проверка:**
После исправления `bc[0:2]` вернёт 2 элемента, `bc[0:3]` вернёт 3 элемента.

**Доказательства:**
- ![5error](https://github.com/kiruganich/python-lab-5/blob/f8125d420d32e0d0d6c5097afb4bee68115fb38b/lab-4-buggy/screenshots/5error.png)
