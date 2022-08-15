from pathlib import Path
from unittest.mock import patch

from booker import database
from booker.error import Error
from pytest import fixture


@fixture(scope="function")
def db_file(tmp_path) -> Path:
    db = tmp_path / "mock_dir/mock_books.json"
    db.parent.mkdir()
    db.touch()
    return db


def test_init_database_error(db_file):
    with patch.object(Path, "write_text") as failing_write:
        failing_write.side_effect = OSError(1, "writing to the file fails")
        outcome = database.init_database(db_file)
        assert outcome.failed()
        assert outcome.is_error(Error.DB_WRITE_ERROR)


def test_init_database(db_file):
    outcome = database.init_database(db_file)
    assert outcome.succeeded()
    assert db_file.read_text() == "[]"
