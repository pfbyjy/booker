import json
from pathlib import Path
from unittest.mock import patch

import pkg_resources
from _pytest.fixtures import fixture

from booker.booker import BookList, Book
from booker.database import DBHandler
from booker import __app_name__, config


@fixture(scope="function")
def mock_config_dir(tmp_path) -> None:
    with patch.object(config, "config_dir_path") as mock_config:
        mock_path = tmp_path / f"mock_dir/{__app_name__}"
        mock_config.return_value = mock_path


@fixture(scope="function")
def db_file(tmp_path) -> Path:
    db = tmp_path / "mock_dir/mock_books.json"
    db.parent.mkdir()
    db.touch()
    return db


@fixture(scope="session")
def mock_data_path() -> Path:
    return Path(
        pkg_resources.resource_filename("tests.resources", "test_input_data.json")
    )


@fixture(scope="session")
def malformed_data_path() -> Path:
    return Path(
        pkg_resources.resource_filename("tests.resources", "malformed_input.json")
    )


@fixture(scope="session")
def mock_db_handler(mock_data_path) -> DBHandler:
    return DBHandler(mock_data_path)


@fixture(scope="session")
def raw_mock_data(mock_data_path) -> str:
    return mock_data_path.read_text()


@fixture(scope="session")
def mock_book_list(raw_mock_data) -> BookList:
    return json.loads(raw_mock_data, object_hook=lambda d: Book(**d))
