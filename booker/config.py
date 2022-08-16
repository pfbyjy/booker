import configparser
from pathlib import Path

import typer

from booker import __app_name__
from booker.error import CONFIG_DIRECTORY_ERROR, CONFIG_FILE_ERROR, EXISTENCE_ERROR
from booker.control import Outcome, SUCCESS


def config_dir_path(path: Path) -> Path:
    if path:
        return path
    return Path(typer.get_app_dir(__app_name__))


def config_file_path(path: Path = None) -> Path:
    return config_dir_path(path) / "config.ini"


def config_file_exists(path: Path = None, **kwargs) -> Outcome:
    path = config_file_path(path)
    if config_file_path(path).exists():
        return SUCCESS({'config_file': config_file_path(path)})
    else:
        err = FileNotFoundError(f"config file {config_file_path(path)} does not exist. run `{__app_name__} init`")
        return EXISTENCE_ERROR(err)


def init_app(db_path: Path, config_dir: Path = None, **kwargs) -> Outcome:
    config_outcome = _init_config_file(config_dir)
    if config_outcome.failed():
        return config_outcome
    add_database_outcome = _add_database_config(db_path)
    if add_database_outcome.failed():
        return add_database_outcome
    return SUCCESS()


def _init_config_file(path: Path = None, **kwargs) -> Outcome:
    try:
        config_dir_path(path).mkdir(exist_ok=True)
    except OSError as e:
        return CONFIG_DIRECTORY_ERROR(e)
    try:
        config_file_path(path).touch(exist_ok=True)
    except OSError as e:
        return CONFIG_FILE_ERROR(e)
    return SUCCESS()


def _add_database_config(db_path: Path, config_dir: Path = None, **kwargs) -> Outcome:
    config_parser = configparser.ConfigParser()
    config_parser["General"] = {"database": db_path}
    try:
        with config_file_path(config_dir).open("w") as file:
            config_parser.write(file)
    except OSError as e:
        return CONFIG_FILE_ERROR(e)
    return SUCCESS()
