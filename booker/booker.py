from dataclasses import field
from enum import Enum
from typing import NamedTuple, List, TypedDict

from booker.error import Outcome


class ImportMethod(Enum):
    MANUAL = 0
    BULK = 1


class Book(TypedDict):
    id: int
    isbn: str
    title: str
    author_fname: str
    author_lname: str


BookList = List[Book]


class CurrentBook(NamedTuple):
    book: Book
    outcome: Outcome

