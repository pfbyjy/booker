import pathlib

import pytest
from typer.testing import CliRunner

from booker import __app_name__, __version__, cli, database, config

runner = CliRunner()


@pytest.mark.integration
def test_version():
    result = runner.invoke(cli.app, ["-v"])
    assert result.exit_code == 0
    assert f"{__app_name__} v{__version__}\n" in result.stdout


@pytest.mark.integration
@pytest.mark.parametrize(
    "flags",
    [
        ["init"],
        ["init", "--db-path", "test_long_flag.json"],
        ["init", "-db", "test_short_flag.json"],
    ],
)
def test_init(flags):
    result = runner.invoke(cli.app, flags)
    db_path = database.get_database_path(config.config_file_path())
    assert result.exit_code == 0
    assert f"The book database is {db_path.absolute()}" in result.stdout
    # clean up what we've created
    db_path.unlink()
    config.config_file_path().unlink()
    # assert that the cleanup actually happened
    assert not db_path.exists()
    assert not config.config_file_path().exists()
