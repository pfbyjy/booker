from pathlib import Path
from typing import List

import typer

from booker import config
from booker.bookerdataclasses import Book, Status, Ordering, ExportFormat
from booker.config import config_file_path
from booker.control import Outcome, Pipeline
from booker.database import (
    read_books,
    export_yaml,
    export_pantry,
    append_book,
    write_books,
    _update_status,
    incr_id,
    database_path,
    delete_book_id,
)
from booker.listbooks import fmt_table


def init(db_path) -> None:
    db_path = Path(db_path)
    pipeline = Pipeline(
        finalizer=lambda: typer.secho(
            f"The book database is {db_path.absolute()}", fg=typer.colors.GREEN
        ),
        initial_args={"db_path": db_path},
    )
    return ~(pipeline << config.init_app)


def add(
    title: List[str],
    isbn: str,
    author_fname: str,
    author_lname: str,
    status: Status,
    **kwargs,
) -> Outcome:
    book = Book(
        isbn=isbn,
        title=title,
        author_fname=author_fname,
        author_lname=author_lname,
        status=status,
    )

    pipeline = (
        Pipeline(
            finalizer=lambda: f"{' '.join(title)} was added to the database",
            initial_args={"book": book},
        )
        << read_books
        << incr_id
        << append_book
        << write_books
    )
    return ~pipeline


def get_list(ordering: Ordering, **kwargs) -> Outcome:
    return ~(Pipeline(initial_args={"ordering": ordering}) << read_books << fmt_table)


def update_status(id: int, status: Status, **kwargs) -> Outcome:
    return ~(
        Pipeline(initial_args={"id": id, "status": status})
        << read_books
        << _update_status
        << write_books
    )


def delete_book(id: int, **kwargs) -> Outcome:
    return ~(
        Pipeline(initial_args={"id": id})
        << config_file_path
        << database_path
        << read_books
        << delete_book_id
        << write_books
    )


def export(
    fmt: ExportFormat, pantry_id: str = "", basket_id: str = "", **kwargs
) -> Outcome:
    action = {
        ExportFormat.YAML: lambda: export_yaml(),
        ExportFormat.PANTRY: lambda: export_pantry(pantry_id, basket_id),
    }[fmt]

    return action()
