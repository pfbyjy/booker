import configparser
import json
from pathlib import Path

from booker.booker import BookList, Book
from booker.error import DB_WRITE_ERROR, SUCCESS, Outcome, DB_READ_ERROR, JSON_ERROR

DEFAULT_DB_FILE_PATH = Path.home().joinpath("." + Path.home().stem + "_books.json")


def get_database_path(config_file: Path) -> Path:
    config_parser = configparser.ConfigParser()
    config_parser.read(config_file)
    return Path(config_parser["General"]["database"])


def init_database(db_path: Path) -> Outcome:
    try:
        db_path.write_text("[]")
        return SUCCESS
    except OSError as e:
        return DB_WRITE_ERROR(e)


class DBResponse(Outcome):
    def __init__(self, result: BookList, error: Outcome):
        self.result = result
        super(DBResponse, self).__init__(error.err, error.cause)


class DBHandler:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path

    def read_books(self, db_path: Path = None) -> DBResponse:
        db_path = db_path if db_path else self.db_path
        try:
            with db_path.open("r") as db:
                try:
                    book_list = json.load(db, object_hook=lambda d: Book(**d))
                    return DBResponse(book_list, SUCCESS)
                except json.JSONDecodeError as e:
                    decode_error = JSON_ERROR(e)
                    return DBResponse([], decode_error)
        except OSError as e:
            read_error = DB_READ_ERROR(e)
            return DBResponse([], read_error)

    def write_books(self, book_list: BookList) -> DBResponse:
        try:
            with self.db_path.open("w") as db:
                json.dump(book_list, db, indent=2)
            return DBResponse(book_list, SUCCESS)
        except OSError as e:
            write_error = DB_WRITE_ERROR(e)
            return DBResponse(book_list, write_error)
