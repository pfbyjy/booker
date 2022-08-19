import configparser
import json
from json import JSONDecodeError
from pathlib import Path
from typing import Callable

import typer
import yaml

from booker.bookerdataclasses import BookList, Book, Status
from booker.error import (
    DB_WRITE_ERROR,
    DB_READ_ERROR,
    JSON_ERROR,
    ID_ERROR,
    EXPORT_ERROR,
    EXISTENCE_ERROR,
)
from booker.control import Pipeline, outcome, Argument
from booker.config import config_file_path
from booker.pantry import upload

DEFAULT_DB_FILE_PATH = Path.home().joinpath("." + Path.home().stem + "_books.json")


@outcome(
    requires=("config_file",), returns="db_path", registers={KeyError: EXISTENCE_ERROR}
)
def database_path(config_file: Path) -> Path:
    config_parser = configparser.ConfigParser()
    config_parser.read(config_file)
    return Path(config_parser["General"]["database"])


@outcome(requires=("book_list",), returns="next_id")
def incr_id(book_list: BookList, **kwargs) -> int:
    ids: Callable[[Book], int] = lambda x: x["id"]
    max_book: Book = max(book_list, key=ids, default=Book(id=-1))
    return max_book["id"] + 1


@outcome(requires=("book_list", "book", "next_id"), returns="book_list")
def append_book(book_list: BookList, book: Book, next_id: int) -> BookList:
    book["id"] = next_id
    book_list.append(book)
    return book_list


@outcome(
    requires=(Argument("db_path", optional=True),),
    returns="book_list",
    registers={OSError: DB_READ_ERROR, JSONDecodeError: JSON_ERROR},
)
def read_books(db_path: Path = None) -> BookList:
    db_path = db_path if db_path else database_path(config_file_path(None))
    with db_path.open("r") as db:
        book_list = json.load(db, object_hook=lambda d: Book(**d))
        return book_list


@outcome(
    requires=("book_list", Argument("db_path", optional=True)),
    returns="book_list",
    registers={
        OSError: DB_WRITE_ERROR,
        ValueError: DB_WRITE_ERROR,
    },
)
def write_books(book_list: BookList, db_path: Path = None) -> BookList:
    db_path = db_path if db_path else database_path(config_file_path(None))
    if book_list is None:
        raise ValueError("empty json file supplied")
    with db_path.open("w") as db:
        json.dump(book_list, db, indent=2)
        return book_list


@outcome(
    requires=("book_list", "write_path"), returns="", registers={OSError: EXPORT_ERROR}
)
def json_to_yaml(book_list: BookList, write_path: Path) -> None:
    with open(write_path, "w") as outfile:
        yaml.dump(book_list, outfile, default_flow_style=False)


@outcome()
def export_yaml() -> None:
    write_path = Path().home() / "book_export.yaml"
    ~(Pipeline(initial_args={"write_path": write_path}) << read_books << json_to_yaml)


@outcome()
def export_pantry(pantry_id: str, basket_id: str) -> None:
    ~(
        Pipeline(
            initial_args={"pantry_id": pantry_id, "basket_id": basket_id},
            finalizer=lambda response: typer.secho(
                response.get_key("response"), fg=typer.colors.GREEN
            ),
        )
        << read_books
        << upload
    )


@outcome(
    requires=("book_list", "id", "status"),
    returns="book_list",
    registers={KeyError: ID_ERROR},
)
def _update_status(book_list: BookList, id: int, status: Status) -> BookList:
    for book in book_list:
        if book["id"] == id:
            book["status"] = status
            return book_list
    err_str = "include the --id flag." if id == -1 else f"there is no book with id {id}"
    raise KeyError(err_str)


@outcome(
    requires=("book_list", "id"), returns="book_list", registers={KeyError: ID_ERROR}
)
def delete_book_id(book_list: BookList, id: int) -> BookList:
    for idx, book in enumerate(book_list[:]):
        if book["id"] == id:
            book_list.pop(idx)
            return book_list
    err_str = "include the --id flag." if id == -1 else f"there is no book with id {id}"
    raise KeyError(err_str)
