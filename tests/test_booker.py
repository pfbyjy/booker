from unittest.mock import patch

import pytest

from booker import config
from booker.booker import add, get_list
from booker.database import read_books, write_books


def test_add(mock_single_book, mock_config_dir, mock_db_file):
    with patch.object(config, 'config_dir_path') as cfig:
        cfig.return_value = mock_config_dir
        config.init_app(mock_db_file)
        outcome = add(**mock_single_book)
        assert outcome.succeeded()
        contents = read_books()
        assert contents.succeeded()
        assert len(contents.get_key('book_list')) > 0


def test_list_all(mock_config_dir, mock_db_file, mock_book_list):
    with patch.object(config, 'config_dir_path') as cfig:
        cfig.return_value = mock_config_dir
        config.init_app(mock_db_file)
        write_books(mock_book_list, mock_db_file)
        outcome = get_list()
        assert outcome.succeeded()
        assert len(outcome.get_key('book_list')) == len(mock_book_list)