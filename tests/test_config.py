from pathlib import Path
from unittest.mock import patch


from booker import config
from booker.error import Error, CONFIG_DIRECTORY_ERROR, CONFIG_FILE_ERROR


def test_init_config_file_with_config_dir_os_error_returns_config_dir_error_code(
    mock_config_dir,
):
    with patch.object(Path, "mkdir") as failing_path:
        failing_path.side_effect = OSError(1, "creating the config directory fails")
        outcome = config._init_config_file()
        assert outcome.failed()
        assert outcome.is_error(Error.CONFIG_DIRECTORY_ERROR)


def test_init_config_file_with_config_file_os_error_returns_config_file_error_code(
    mock_config_dir,
):
    with patch.object(Path, "touch") as failing_path:
        failing_path.side_effect = OSError(1, "creating the config file fails")
        outcome = config._init_config_file()
        assert outcome.failed()
        assert outcome.is_error(Error.CONFIG_FILE_ERROR)


def test_init_config_file_succeeds(mock_config_dir):
    outcome = config._init_config_file()
    assert outcome.succeeded()
    assert config.config_file_path().exists()


def test_add_database_config_succeeds(mock_config_dir):
    outcome = config._add_database_config("test_path")
    assert outcome.succeeded()
    assert (
        config.config_file_path().read_text().strip()
        == "[General]\ndatabase = test_path"
    )


def test_add_database_config_fails_with_config_file_error_code(mock_config_dir):
    with patch.object(Path, "open") as failing_path:
        failing_path.side_effect = OSError(
            1, "adding the database config to the config file fails"
        )
        outcome = config._add_database_config("test_path")
        assert outcome.failed()
        assert outcome.is_error(Error.CONFIG_FILE_ERROR)


def test_init_app_succeeds(mock_config_dir):
    outcome = config.init_app("test_path")
    assert outcome.succeeded()
    assert (
        config.config_file_path().read_text().strip()
        == "[General]\ndatabase = test_path"
    )


def test_init_returns_directory_error_when_creating_config_dir_fails(mock_config_dir):
    with patch.object(config, "_init_config_file") as failing_config_file_init_mock:
        failing_config_file_init_mock.return_value = CONFIG_DIRECTORY_ERROR("")
        outcome = config.init_app("test_path")
        assert outcome.failed()
        assert outcome.is_error(Error.CONFIG_DIRECTORY_ERROR)


def test_init_returns_file_error_when_creating_config_file_fails(mock_config_dir):
    with patch.object(config, "_init_config_file") as failing_config_file_init_mock:
        failing_config_file_init_mock.return_value = CONFIG_FILE_ERROR("")
        outcome = config.init_app("test_path")
        assert outcome.is_error(Error.CONFIG_FILE_ERROR)


def test_init_returns_file_error_when_populating_db_config_fails(mock_config_dir):
    with patch.object(config, "_add_database_config") as failing_db_add_init_mock:
        failing_db_add_init_mock.return_value = CONFIG_FILE_ERROR("")
        outcome = config.init_app("test_path")
        assert outcome.is_error(Error.CONFIG_FILE_ERROR)
