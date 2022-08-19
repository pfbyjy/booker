from enum import Enum
from typing import TypedDict, List, NamedTuple, Callable, Any, Dict

from booker.control import Outcome


class ImportMethod(Enum):
    MANUAL = 0
    BULK = 1


class Status(str, Enum):
    UNREAD = "unread"
    IN_PROGRESS = "in progress"
    FINISHED = "finished"


class Ordering(str, Enum):
    DEFAULT = "id"
    AUTHOR = "author"
    TITLE = "title"
    ISBN = "isbn"
    STATUS = "status"


class ExportFormat(str, Enum):
    PANTRY = "pantry"
    YAML = "yaml"


class Book(TypedDict):
    id: int
    isbn: str
    title: str
    author_fname: str
    author_lname: str
    status: Status


BookList = List[Book]


class CurrentBook(NamedTuple):
    book: Book
    outcome: Outcome
