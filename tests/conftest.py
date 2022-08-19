import json
import random
import string
from pathlib import Path

import pkg_resources
from _pytest.fixtures import fixture

from booker.bookerdataclasses import BookList, Book
from booker import __app_name__


@fixture(scope="session")
def mock_dir(tmp_path_factory) -> Path:
    base = tmp_path_factory.mktemp("mock_dir")
    yield base


@fixture(scope="function")
def mock_json_db_location(mock_dir, request) -> Path:
    if len(request.param) > 1:
        request.param += [
            mock_dir / f"{ ''.join(random.sample(string.ascii_letters, 4))}.json"
        ]
    return request.param


@fixture(scope="session")
def mock_config_dir(mock_dir) -> Path:
    mock_path = mock_dir / __app_name__
    mock_path.mkdir(exist_ok=True)
    return mock_path


@fixture(scope="session")
def mock_db_file(mock_dir) -> Path:
    db = mock_dir / "mock_books.json"
    db.write_text("[]")
    return db


def _get_test_resource_path(filename: str) -> Path:
    return Path(pkg_resources.resource_filename("tests.resources", filename))


@fixture(scope="session")
def mock_data_path() -> Path:
    return _get_test_resource_path("test_input_data.json")


@fixture(scope="session")
def mock_single_input() -> Path:
    return _get_test_resource_path("single_test_input_data.json")


@fixture(scope="session")
def malformed_data_path() -> Path:
    return _get_test_resource_path("malformed_input.json")


@fixture(scope="session")
def raw_mock_data(mock_data_path) -> str:
    return mock_data_path.read_text()


@fixture(scope="session")
def mock_single_book(mock_single_input) -> Book:
    parsed_data = json.loads(mock_single_input.read_text())[0]
    parsed_data.pop("id")
    return Book(**parsed_data)


@fixture(scope="session")
def mock_book_list(raw_mock_data) -> BookList:
    return json.loads(raw_mock_data, object_hook=lambda d: Book(**d))


@fixture(scope="session")
def mock_booker_app(mock_db_file):
    mock_db_file.write_text("[]")
