from pathlib import Path
from typing import List

import typer

from booker import database, config
from booker.bookerdataclasses import Book
from booker.control import Outcome, OutcomeChain
from booker.database import add_book, next_id, read_books


def init(db_path) -> None:
    db_path = Path(db_path)
    OutcomeChain(
        finalizer=lambda: typer.secho(
            f"The book database is {db_path.absolute()}", fg=typer.colors.GREEN
        ),
    ).with_initial_context(
        "db_path", db_path
    ).sequence(
        config.init_app
    ).sequence(
        database.init_database
    ).execute()


def add(title: List[str],
        isbn: str,
        author_fname: str,
        author_lname: str,
        **kwargs
        ) -> Outcome:
    book = Book(
        id=next_id().get_key("next_id"),
        isbn=isbn,
        title=title,
        author_fname=author_fname,
        author_lname=author_lname)

    return add_book(book)


def get_list() -> Outcome:
    return read_books()
