import configparser
from pathlib import Path
import typer
from booker import __app_name__
from booker.error import (
    CONFIG_DIRECTORY_ERROR,
    CONFIG_FILE_ERROR,
    EXISTENCE_ERROR,
    DB_WRITE_ERROR,
)
from booker.control import Outcome, SUCCESS, outcome, Argument, Pipeline


def config_dir_path(path: Path) -> Path:
    if path:
        return path
    return Path(typer.get_app_dir(__app_name__))


@outcome(requires=(Argument("path", optional=True),), returns="config_file")
def config_file_path(path: Path = None) -> Path:
    return config_dir_path(path) / "config.ini"


@outcome(
    requires=(Argument("path", optional=True),),
    returns="config_file",
    registers={FileNotFoundError: EXISTENCE_ERROR},
)
def config_file_exists(path: Path = None, **kwargs) -> Outcome:
    path = config_file_path(path)
    if config_file_path(path).exists():
        return config_file_path(path)
    else:
        err_str = f"config file {config_file_path(path)} does not exist. run `{__app_name__} init`"
        raise FileNotFoundError(err_str)


@outcome(requires=("db_path", Argument("config_dir", optional=True)))
def init_app(db_path: Path, config_dir: Path = None) -> Outcome:
    return ~(
        Pipeline(initial_args={"db_path": db_path, "config_dir": config_dir})
        << init_config_file
        << _add_database_config
        << init_database
    )


@outcome(requires=("db_path",), registers={OSError: DB_WRITE_ERROR})
def init_database(db_path: Path) -> None:
    db_path.write_text("[]")


@outcome(
    requires=(Argument("config_path", optional=True),),
    registers={OSError: CONFIG_DIRECTORY_ERROR},
)
def init_config_file(config_path: Path = None) -> None:
    config_dir_path(config_path).mkdir(exist_ok=True)
    config_file_path(config_path).touch(exist_ok=True)


@outcome(
    requires=("db_path", Argument("config_path", optional=True)),
    returns="",
    registers={OSError: CONFIG_FILE_ERROR},
)
def _add_database_config(db_path: Path, config_dir: Path = None) -> None:
    config_parser = configparser.ConfigParser()
    config_parser["General"] = {"database": db_path}
    with config_file_path(config_dir).open("w") as file:
        config_parser.write(file)
