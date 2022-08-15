from pathlib import Path
from unittest.mock import patch

from booker import database, SUCCESS, DB_WRITE_ERROR

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
        err_code = database.init_database(db_file)
        assert err_code == DB_WRITE_ERROR


def test_init_database(db_file):
    err_code = database.init_database(db_file)
    assert err_code == SUCCESS
    assert db_file.read_text() == "[]"
