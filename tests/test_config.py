from pathlib import Path
from unittest.mock import patch

from _pytest.fixtures import fixture

from booker import (
    config,
    __app_name__,
    CONFIG_DIRECTORY_ERROR,
    CONFIG_FILE_ERROR,
    SUCCESS,
)


@fixture(scope="function")
def mock_config_dir(tmp_path) -> None:
    with patch.object(config, "config_dir_path") as mock_config:
        mock_path = tmp_path / f"mock_dir/{__app_name__}"
        mock_config.return_value = mock_path


def test_init_config_file_with_config_dir_os_error_returns_config_dir_error_code(
    mock_config_dir,
):
    with patch.object(Path, "mkdir") as failing_path:
        failing_path.side_effect = OSError(1, "creating the config directory fails")
        code = config._init_config_file()
        assert code == CONFIG_DIRECTORY_ERROR


def test_init_config_file_with_config_file_os_error_returns_config_file_error_code(
    mock_config_dir,
):
    with patch.object(Path, "touch") as failing_path:
        failing_path.side_effect = OSError(1, "creating the config file fails")
        code = config._init_config_file()
        assert code == CONFIG_FILE_ERROR


def test_init_config_file_succeeds(mock_config_dir):
    code = config._init_config_file()
    assert code == SUCCESS
    assert config.config_file_path().exists()


def test_add_database_config_succeeds(mock_config_dir):
    code = config._add_database_config("test_path")
    assert code == SUCCESS
    assert (
        config.config_file_path().read_text().strip()
        == "[General]\ndatabase = test_path"
    )


def test_add_database_config_fails_with_config_file_error_code(mock_config_dir):
    with patch.object(Path, "open") as failing_path:
        failing_path.side_effect = OSError(
            1, "adding the database config to the config file fails"
        )
        code = config._add_database_config("test_path")
        assert code == CONFIG_FILE_ERROR


def test_init_app_succeeds(mock_config_dir):
    code = config.init_app("test_path")
    assert code == SUCCESS
    assert (
        config.config_file_path().read_text().strip()
        == "[General]\ndatabase = test_path"
    )


def test_init_returns_directory_error_when_creating_config_dir_fails(mock_config_dir):
    with patch.object(config, "_init_config_file") as failing_config_file_init_mock:
        failing_config_file_init_mock.return_value = CONFIG_DIRECTORY_ERROR
        code = config.init_app("test_path")
        assert code == CONFIG_DIRECTORY_ERROR


def test_init_returns_file_error_when_creating_config_file_fails(mock_config_dir):
    with patch.object(config, "_init_config_file") as failing_config_file_init_mock:
        failing_config_file_init_mock.return_value = CONFIG_FILE_ERROR
        code = config.init_app("test_path")
        assert code == CONFIG_FILE_ERROR


def test_init_returns_file_error_when_populating_db_config_fails(mock_config_dir):
    with patch.object(config, "_add_database_config") as failing_db_add_init_mock:
        failing_db_add_init_mock.return_value = CONFIG_FILE_ERROR
        code = config.init_app("test_path")
        assert code == CONFIG_FILE_ERROR
