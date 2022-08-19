from pathlib import Path
from unittest.mock import patch

from _pytest.python_api import raises

from booker import config


def test_init_config_file_with_config_dir_os_error_returns_config_dir_error_code(
    mock_config_dir,
):
    with raises(OSError):
        with patch.object(Path, "mkdir") as failing_path:
            failing_path.side_effect = OSError(1, "creating the config directory fails")
            config.init_config_file(mock_config_dir)


def test_init_config_file_with_config_file_os_error_returns_config_file_error_code(
    mock_config_dir,
):
    with raises(OSError):
        with patch.object(Path, "touch") as failing_path:
            failing_path.side_effect = OSError(1, "creating the config file fails")
            config.init_config_file(mock_config_dir)


def test_init_config_file_succeeds(mock_config_dir):
    config.init_config_file(mock_config_dir)
    assert config.config_dir_path(mock_config_dir).exists()
    assert config.config_file_path(mock_config_dir).exists()


def test_add_database_config_succeeds(mock_config_dir, mock_db_file):
    config._add_database_config(mock_db_file, mock_config_dir)
    assert (
        config.config_file_path(mock_config_dir).read_text().strip()
        == f"[General]\ndatabase = {mock_db_file}"
    )


def test_add_database_config_fails_with_config_file_error_code(mock_config_dir):
    with raises(OSError):
        with patch.object(Path, "open") as failing_path:
            failing_path.side_effect = OSError(
                1, "adding the database config to the config file fails"
            )
            config._add_database_config(
                config.config_file_path(mock_config_dir), mock_config_dir
            )


def test_init_app_succeeds(mock_config_dir, mock_db_file):
    with patch.object(config, "config_dir_path") as cfig:
        cfig.return_value = mock_config_dir
        outcome = config.init_app(mock_db_file, mock_config_dir)
        assert outcome.succeeded()
        assert (
            config.config_file_path(mock_config_dir).read_text().strip()
            == f"[General]\ndatabase = {mock_db_file}"
        )
