from typing import Optional, List

import typer

from booker import (
    __app_name__,
    __version__,
    database, booker,
)
from booker.control import OutcomeChain

app = typer.Typer()


def require_option(opt: str) -> None:
    typer.secho(f"--{opt} is required.", fg=typer.colors.RED)
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
    """ Initialize the book database."""
    booker.init(db_path)


@app.command()
def add(
        title: str = typer.Option(None),
        isbn: str = typer.Option(None),
        author_fname: str = typer.Option(None),
        author_lname: str = typer.Option(None)
) -> None:
    """Add a book to the database."""
    OutcomeChain(
        finalizer=lambda: f"{' '.join(title)} was added to the database"
    ).sequence(
        booker.add, locals()  # this is hacky.
    ).execute()


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
