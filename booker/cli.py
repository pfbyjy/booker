from typing import Optional, Any

from pathlib import Path
import typer

from booker import (
    __app_name__,
    __version__,
    config,
    database,
)
from booker.error import Outcome, OutcomeChain

app = typer.Typer()


def cli_error_handler(outcome: Outcome) -> Any:
    if outcome.failed():
        typer.secho(str(outcome), fg=typer.colors.RED)
        raise typer.Exit(1)


@app.command()
def init(
    db_path: str = typer.Option(
        str(database.DEFAULT_DB_FILE_PATH),
        "--db-path",
        "-db",
        prompt="book database location?",
    ),
) -> None:
    db_path = Path(db_path)
    chain = OutcomeChain(
        cli_error_handler,
        lambda: typer.secho(
            f"The book database is {db_path.absolute()}", fg=typer.colors.GREEN
        ),
    )
    chain.sequence(config.init_app, [db_path])
    chain.sequence(database.init_database, [db_path])
    chain.execute_serial()


def _version(version_flag: bool) -> None:
    if version_flag:
        typer.echo(f"{__app_name__} v{__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Show the application's version then exit.",
        callback=_version,
        is_eager=True,
    )
) -> None:
    return
