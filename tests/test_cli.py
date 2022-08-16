from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from booker.booker import init
from booker import __app_name__, __version__, cli, config

runner = CliRunner()


@pytest.mark.integration
def test_version():
    result = runner.invoke(cli.app, ["-v"])
    assert result.exit_code == 0
    assert f"{__app_name__} v{__version__}\n" in result.stdout


@pytest.mark.integration
@pytest.mark.parametrize(
    "mock_json_db_location",
    [
        ["init"],
        ["init", "--db-path"],
        ["init", "-db"],
    ],
    indirect=True
)
def test_init(mock_json_db_location, mock_config_dir):
    with patch.object(config, 'config_dir_path') as cfig:
        cfig.return_value = mock_config_dir
        result = runner.invoke(cli.app, mock_json_db_location)
        assert result.exit_code == 0


@pytest.mark.integration
@pytest.mark.parametrize(
    "flags",
    [
        ["add",
         "--title", "'the unbearable lightness of being'",
         "--isbn", "1234567890123",
         "--author-fname", "Milo",
         "--author-lname", "Bricheimmer"
         ]
    ], )
def test_add(flags, mock_config_dir, mock_db_file):
    with patch.object(config, 'config_dir_path') as cfig:
        cfig.return_value = mock_config_dir
        mock_config_dir.parent.mkdir(exist_ok=True)
        init(mock_db_file)
        result = runner.invoke(cli.app, flags)
        assert result.exit_code == 0