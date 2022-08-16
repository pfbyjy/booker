import configparser
import json
from pathlib import Path
from typing import Callable

from booker import __app_name__
from booker.bookerdataclasses import BookList, Book
from booker.error import DB_WRITE_ERROR, DB_READ_ERROR, JSON_ERROR, EXISTENCE_ERROR
from booker.control import Outcome, OutcomeChain, SUCCESS
from booker.config import config_file_path

DEFAULT_DB_FILE_PATH = Path.home().joinpath("." + Path.home().stem + "_books.json")


def database_path(config_file: Path) -> Path:
    config_parser = configparser.ConfigParser()
    config_parser.read(config_file)
    return Path(config_parser["General"]["database"])


def init_database(db_path: Path, **kwargs) -> Outcome:
    try:
        db_path.write_text("[]")
        return SUCCESS()
    except OSError as e:
        return DB_WRITE_ERROR(e)


def db_path_exists(config_file: Path, **kwargs) -> Outcome:
    db_path = database_path(config_file)
    if db_path.exists():
        return SUCCESS({'db_path': db_path})
    else:
        err = FileNotFoundError(f"database path {db_path} does not exist. run `{__app_name__} init`")
        return EXISTENCE_ERROR(err)


def incr_id(book_list: BookList, **kwargs) -> Outcome:
    ids: Callable[[Book], int] = lambda x: x["id"]
    max_id: int = max(book_list, key=ids, default=-1)
    return SUCCESS({'next_id': max_id + 1})


def append_book(book_list: BookList, book: Book, **kwargs) -> Outcome:
    book_list.append(book)
    return SUCCESS({'book_list': book_list})


def read_books(db_path: Path = None, **kwargs) -> Outcome:
    db_path = db_path if db_path else database_path(config_file_path())
    try:
        with db_path.open("r") as db:
            try:
                book_list = json.load(db, object_hook=lambda d: Book(**d))
                return SUCCESS({'book_list': book_list})
            except json.JSONDecodeError as e:
                return JSON_ERROR(e)
    except OSError as e:
        return DB_READ_ERROR(e)


def write_books(book_list: BookList, db_path: Path = None, **kwargs) -> Outcome:
    db_path = db_path if db_path else database_path(config_file_path())
    if book_list is None:
        return DB_WRITE_ERROR(ValueError("empty json file supplied"))
    try:
        with db_path.open("w") as db:
            json.dump(book_list, db, indent=2)
        return SUCCESS({'book_list': book_list})

    except OSError as e:
        return DB_WRITE_ERROR(e)


def next_id(**kwargs) -> Outcome:
    return OutcomeChain().sequence(
        read_books
    ).sequence(
        incr_id
    ).execute()


def add_book(book: Book, **kwargs) -> Outcome:
    return OutcomeChain().sequence(
        read_books
    ).sequence(
        append_book, {'book':  book}
    ).sequence(
        write_books
    ).execute()
