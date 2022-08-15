import configparser
from pathlib import Path

import typer

from booker import __app_name__
from booker.error import CONFIG_DIRECTORY_ERROR, CONFIG_FILE_ERROR, SUCCESS, Outcome


def config_dir_path() -> Path:
    return Path(typer.get_app_dir(__app_name__))


def config_file_path() -> Path:
    return config_dir_path() / "config.ini"


def init_app(db_path: str) -> Outcome:
    config_outcome = _init_config_file()
    if config_outcome.failed():
        return config_outcome
    add_database_outcome = _add_database_config(db_path)
    if add_database_outcome.failed():
        return add_database_outcome
    return SUCCESS


def _init_config_file() -> Outcome:
    try:
        config_dir_path().mkdir(exist_ok=True)
    except OSError as e:
        return CONFIG_DIRECTORY_ERROR(e)
    try:
        config_file_path().touch(exist_ok=True)
    except OSError as e:
        return CONFIG_FILE_ERROR(e)
    return SUCCESS


def _add_database_config(db_path: str) -> Outcome:
    config_parser = configparser.ConfigParser()
    config_parser["General"] = {"database": db_path}
    try:
        with config_file_path().open("w") as file:
            config_parser.write(file)
    except OSError as e:
        return CONFIG_FILE_ERROR(e)
    return SUCCESS
