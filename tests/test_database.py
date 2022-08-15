import json
from pathlib import Path
from unittest.mock import patch

import pkg_resources

from booker import database
from booker.error import Error


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


def test_read_books_succeeds(mock_db_handler, raw_mock_data):
    response = mock_db_handler.read_books()
    assert response.succeeded()
    assert len(response.result) > 0
    print(json.dumps(response.result))


def test_read_books_fails_with_json_decode_error(mock_db_handler, malformed_data_path):
    response = mock_db_handler.read_books(malformed_data_path)
    assert response.failed()
    assert len(response.result) == 0
    assert response.is_error(Error.JSON_ERROR)


def test_read_books_fails_with_os_error(mock_db_handler, mock_data_path):
    with patch.object(Path, "open") as failing_file_read:
        failing_file_read.side_effect = OSError(1, "opening the file fails")
        response = mock_db_handler.read_books()
        assert response.failed()
        assert len(response.result) == 0
        assert response.is_error(Error.DB_READ_ERROR)


def test_write_books_succeeds(mock_db_handler, mock_book_list, mock_data_path):
    response = mock_db_handler.write_books(mock_book_list)
    assert response.succeeded()
    assert mock_data_path.read_text() == json.dumps(mock_book_list, indent=2)


def test_write_books_fails(mock_db_handler, mock_book_list, mock_data_path):
    with patch.object(Path, "open") as failing_file_write:
        failing_file_write.side_effect = OSError(1, "opening the file fails")
        response = mock_db_handler.write_books(mock_book_list)
        assert response.failed()
        assert response.is_error(Error.DB_WRITE_ERROR)
