import json
from pathlib import Path
from unittest.mock import patch

import pytest

from booker import database, config
from booker.booker import init
from booker.database import write_books, read_books, init_database, add_book, incr_id
from booker.error import DB_WRITE_ERROR, DB_READ_ERROR, JSON_ERROR


def test_init_database_error(mock_db_file):
    with patch.object(Path, "write_text") as failing_write:
        failing_write.side_effect = OSError(1, "writing to the file fails")
        outcome = init_database(mock_db_file)
        assert outcome.failed()
        assert isinstance(outcome, DB_WRITE_ERROR)


def test_init_database(mock_db_file):
    outcome = database.init_database(mock_db_file)
    assert outcome.succeeded()
    assert mock_db_file.read_text() == "[]"


def test_read_books_succeeds(mock_data_path):
    response = read_books(mock_data_path)
    assert response.succeeded()
    book_list = response.get_key('book_list')
    assert len(book_list) > 0


def test_read_books_fails_with_json_decode_error( malformed_data_path):
    response = read_books(malformed_data_path)
    assert response.failed()
    assert response.get_key('book_list') is None
    assert isinstance(response, JSON_ERROR)


def test_read_books_fails_with_os_error( mock_data_path):
    with patch.object(Path, "open") as failing_file_read:
        failing_file_read.side_effect = OSError(1, "opening the file fails")
        response = read_books(mock_data_path)
        assert response.failed()
        assert response.get_key('book_list') is None
        assert isinstance(response, DB_READ_ERROR)


def test_write_books_succeeds(mock_book_list, mock_db_file):
    response = write_books(mock_book_list, mock_db_file)
    assert response.succeeded()
    assert mock_db_file.read_text() == json.dumps(mock_book_list, indent=2)


def test_write_books_fails( mock_book_list, mock_data_path, mock_db_file):
    with patch.object(Path, "open") as failing_file_write:
        failing_file_write.side_effect = OSError(1, "opening the file fails")
        response = write_books(mock_book_list, mock_db_file)
        assert response.failed()
        assert isinstance(response, DB_WRITE_ERROR)


def test_add_book_succeeds(mock_single_book, mock_db_file, mock_config_dir):
    with patch.object(config, 'config_dir_path') as cfig:
        cfig.return_value = mock_config_dir
        mock_config_dir.parent.mkdir(exist_ok=True)
        init(mock_db_file)
        response = add_book(mock_single_book)
        assert response.succeeded()


def test_incr_id(mock_single_book):
    outcome = incr_id([])
    assert outcome.succeeded()
    assert outcome.get_key('next_id') == 0