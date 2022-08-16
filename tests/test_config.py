from pathlib import Path
from unittest.mock import patch
from booker import config
from booker.error import CONFIG_DIRECTORY_ERROR, CONFIG_FILE_ERROR


def test_init_config_file_with_config_dir_os_error_returns_config_dir_error_code(
    mock_config_dir,
):
    with patch.object(Path, "mkdir") as failing_path:
        failing_path.side_effect = OSError(1, "creating the config directory fails")
        outcome = config._init_config_file(mock_config_dir)
        assert outcome.failed()
        assert isinstance(outcome, CONFIG_DIRECTORY_ERROR)


def test_init_config_file_with_config_file_os_error_returns_config_file_error_code(
    mock_config_dir,
):
    with patch.object(Path, "touch") as failing_path:
        failing_path.side_effect = OSError(1, "creating the config file fails")
        outcome = config._init_config_file(mock_config_dir)
        assert outcome.failed()
        assert isinstance(outcome, CONFIG_FILE_ERROR)


def test_init_config_file_succeeds(mock_config_dir):
    outcome = config._init_config_file(mock_config_dir)
    assert outcome.succeeded()
    assert config.config_file_path(mock_config_dir).exists()


def test_add_database_config_succeeds(mock_config_dir, mock_db_file):
    outcome = config._add_database_config(mock_db_file, mock_config_dir)
    assert outcome.succeeded()
    assert (
        config.config_file_path(mock_config_dir).read_text().strip()
        == f"[General]\ndatabase = {mock_db_file}"
    )


def test_add_database_config_fails_with_config_file_error_code(mock_config_dir):
    with patch.object(Path, "open") as failing_path:
        failing_path.side_effect = OSError(
            1, "adding the database config to the config file fails"
        )
        outcome = config._add_database_config(config.config_file_path(mock_config_dir), mock_config_dir)
        assert outcome.failed()
        assert isinstance(outcome, CONFIG_FILE_ERROR)


def test_init_app_succeeds(mock_config_dir, mock_db_file):
    with patch.object(config, 'config_dir_path') as cfig:
        cfig.return_value = mock_config_dir
        outcome = config.init_app(mock_db_file, mock_config_dir)
        assert outcome.succeeded()
        assert (
            config.config_file_path(mock_config_dir).read_text().strip()
            == f"[General]\ndatabase = {mock_db_file}"
         )


def test_init_returns_directory_error_when_creating_config_dir_fails(mock_config_dir, mock_db_file):
    with patch.object(config, "_init_config_file") as failing_config_file_init_mock:
        failing_config_file_init_mock.return_value = CONFIG_DIRECTORY_ERROR("")
        outcome = config.init_app(mock_db_file, mock_config_dir)
        assert outcome.failed()
        assert isinstance(outcome, CONFIG_DIRECTORY_ERROR)


def test_init_returns_file_error_when_creating_config_file_fails(mock_config_dir, mock_db_file):
    with patch.object(config, "_init_config_file") as failing_config_file_init_mock:
        failing_config_file_init_mock.return_value = CONFIG_FILE_ERROR("")
        outcome = config.init_app(mock_db_file, mock_config_dir)
        assert isinstance(outcome, CONFIG_FILE_ERROR)


def test_init_returns_file_error_when_populating_db_config_fails(mock_config_dir, mock_db_file):
    with patch.object(config, "_add_database_config") as failing_db_add_init_mock:
        failing_db_add_init_mock.return_value = CONFIG_FILE_ERROR("")
        outcome = config.init_app(mock_db_file, mock_config_dir)
        assert isinstance(outcome, CONFIG_FILE_ERROR)
