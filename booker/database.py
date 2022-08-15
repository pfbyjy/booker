import configparser
from pathlib import Path

from booker.error import DB_WRITE_ERROR, SUCCESS, Outcome

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
