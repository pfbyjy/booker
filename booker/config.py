import configparser
from functools import cached_property
from pathlib import Path

import typer

from booker import (
    DB_WRITE_ERROR,
    CONFIG_DIRECTORY_ERROR,
    CONFIG_FILE_ERROR,
    SUCCESS,
    __app_name__,
)


def config_dir_path() -> Path:
    return Path(typer.get_app_dir(__app_name__))


def config_file_path() -> Path:
    return config_dir_path() / "config.ini"


def init_app(db_path: str) -> int:
    config_code = _init_config_file()
    if config_code != SUCCESS:
        return config_code
    add_database_code = _add_database_config(db_path)
    if add_database_code != SUCCESS:
        return add_database_code
    return SUCCESS


def _init_config_file() -> int:
    try:
        config_dir_path().mkdir(exist_ok=True)
    except OSError:
        print("here")
        return CONFIG_DIRECTORY_ERROR
    try:
        config_file_path().touch(exist_ok=True)
    except OSError:
        return CONFIG_FILE_ERROR
    return SUCCESS


def _add_database_config(db_path: str) -> int:
    config_parser = configparser.ConfigParser()
    config_parser["General"] = {"database": db_path}
    try:
        with config_file_path().open("w") as file:
            config_parser.write(file)
    except OSError:
        return CONFIG_FILE_ERROR
    return SUCCESS
