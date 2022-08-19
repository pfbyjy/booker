# misc utils. to be moved to their own file soon.
from typing import Callable, Any, Dict

from booker.bookerdataclasses import BookList, Book, Ordering
from booker.control import Outcome, outcome
from booker.error import DB_READ_ERROR


def order_books(book_list: BookList, ordering: Ordering) -> BookList:
    return sorted(book_list, key=lookup_ordering_key(ordering))


def fmt_author(book: Book) -> str:
    return f"{book['author_lname']}, {book['author_fname']}"


def lookup_ordering_key(ordering: str) -> Callable[[Book], Any]:
    if ordering is not Ordering.AUTHOR:
        return lambda x: x[ordering]
    else:
        return lambda x: fmt_author(x)


def fmt_book(book: Book) -> Dict[str, str]:
    return (
        str(book["id"]),
        fmt_author(book),
        book["title"],
        book["isbn"],
        book["status"],
    )


def fmt_books(book_list: BookList):
    return [fmt_book(book) for book in book_list]


def table_header():
    return "ID", "AUTHOR", "TITLE", "ISBN", "STATUS"


@outcome(
    requires=["book_list", "ordering"],
    returns="table_args",
    registers={Exception: DB_READ_ERROR},
)
def fmt_table(book_list: BookList, ordering: str) -> Outcome:
    bl = order_books(book_list, ordering)
    formatted_table = table_header(), fmt_books(bl)
    return formatted_table
