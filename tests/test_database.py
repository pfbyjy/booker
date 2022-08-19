import json
from json import JSONDecodeError
from pathlib import Path
from unittest.mock import patch

from _pytest.python_api import raises

from booker import config
from booker.database import (
    write_books,
    read_books,
    incr_id,
    _update_status,
    export_yaml,
    delete_book_id,
)


def test_read_books_succeeds(mock_data_path):
    book_list = read_books(mock_data_path)
    assert len(book_list) > 0


def test_read_books_fails_with_json_decode_error(malformed_data_path, mock_config_dir):
    with raises(JSONDecodeError):
        with patch.object(config, "config_dir_path") as cfig:
            cfig.return_value = mock_config_dir
            read_books(malformed_data_path)


def test_read_books_fails_with_os_error(mock_data_path):
    with raises(OSError):
        with patch.object(Path, "open") as failing_file_read:
            failing_file_read.side_effect = OSError(1, "opening the file fails")
            read_books(mock_data_path)


def test_write_books_succeeds(mock_book_list, mock_db_file):
    mock_db_file.unlink()
    write_books(mock_book_list, mock_db_file)
    assert len(mock_db_file.read_text())
    assert mock_db_file.read_text() == json.dumps(mock_book_list, indent=2)


def test_write_books_fails(mock_book_list, mock_data_path, mock_db_file):
    with raises(OSError):
        with patch.object(Path, "open") as failing_file_write:
            failing_file_write.side_effect = OSError(1, "opening the file fails")
            write_books(mock_book_list, mock_db_file)


def test_write_books_fails_on_none_booklist(mock_db_file):
    with raises(ValueError) as context:
        write_books(None, mock_db_file)
    assert context.value.__str__() == "empty json file supplied"


def test_incr_id_empty(mock_single_book):
    assert incr_id([]) == 0


def test_incr_id_with_values(mock_book_list):
    sub = mock_book_list[:10]
    mx = sorted(sub, key=lambda x: x["id"])[-1]["id"]
    assert incr_id(sub) == mx + 1


def test_update_book_status(mock_book_list):
    to_mod = {**mock_book_list[0]}
    mod_id = to_mod["id"]
    post_mod = _update_status(mock_book_list, mod_id, "test_status")[0]
    assert to_mod["id"] == post_mod["id"]
    assert to_mod["status"] != post_mod["status"]


def test_update_book_status_throws_key_error_for_non_existent_key(mock_book_list):
    with raises(KeyError) as context:
        _update_status(mock_book_list, -1, "test_status")
    assert context.value.__str__() == "'include the --id flag.'"


def test_yaml(mock_dir):
    with patch.object(Path, 'home') as home_mock:
        home_mock.return_value = mock_dir
        write_path = Path().home() / "book_export.yaml"
        print(write_path)
        export_yaml()
        assert write_path.exists()


def test_delete_book(mock_book_list):
    to_del = {**mock_book_list[0]}
    del_id = to_del["id"]
    pre_del_len = len(mock_book_list)
    post_del = delete_book_id(mock_book_list, del_id)
    assert pre_del_len == len(post_del) + 1
    assert all(x["id"] != del_id for x in post_del)


def test_delete_book_throws_key_error_for_non_existent_key(mock_book_list):
    with raises(KeyError) as context:
        delete_book_id(mock_book_list, -1)
    assert context.value.__str__() == "'include the --id flag.'"
