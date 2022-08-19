from datetime import datetime
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from typer import Option

from booker import __app_name__, __version__, database, booker
from booker.booker import update_status, delete_book, export
from booker.bookerdataclasses import Status, Ordering, ExportFormat

app = typer.Typer()
export_app = typer.Typer()  # nested sub app for export commands
app.add_typer(export_app, name="export", help="Export reading list data.")
bulk_app = typer.Typer()
app.add_typer(bulk_app, name="bulk", help="bulk actions on csv files")


@app.command()
def init(
    db_path: str = Option(
        str(database.DEFAULT_DB_FILE_PATH),
        "--db-path",
        "-db",
        prompt="book database location?",
    ),
) -> None:
    """Initialize the reading list."""
    booker.init(db_path)


@app.command()
def update(id: int = Option(-1), status: Status = Option(Status.FINISHED)) -> None:
    """Update a book's status in the reading list."""
    update_status(id, status)


@app.command()
def delete(id: int = Option(-1)) -> None:
    """Delete a book from the reading list."""
    delete_book(id)


@app.command()
def add(
    title: str = Option(None),
    isbn: str = Option(None),
    author_fname: str = Option(None),
    author_lname: str = Option(None),
    status: Status = Option(Status.UNREAD),
) -> None:
    """Add a book to the reading list."""
    booker.add(**locals())


@app.command(name="list")
def list_all(ordering: Ordering = Option(Ordering.DEFAULT)) -> None:
    """List all the books in the reading list in the order specified by Ordering. Defaults to ID sorting."""
    header, body = booker.get_list(ordering).get_key("table_args")

    if len(body) == 0:
        typer.secho("There are no books in the reading list yet", fg=typer.colors.RED)
        raise typer.Exit()

    table = Table(*header)
    for row in body:
        table.add_row(*row)

    console = Console()
    with console.pager():
        console.print(table)


def _version(version_flag: bool) -> None:
    if version_flag:
        typer.echo(f"{__app_name__} v{__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = Option(
        None,
        "--version",
        "-v",
        help="Show the application's version then exit.",
        callback=_version,
        is_eager=True,
    )
) -> None:
    return


@export_app.command()
def yaml():
    """Export the reading list to $HOME/book_export.yaml"""
    export(ExportFormat.YAML)


@export_app.command()
def pantry(
    pantry_id: str = Option(""),
    basket_id: str = Option(
        lambda: f'book_export_{datetime.now().strftime("%Y-%m-%d_%H:%M:%S")}.json'
    ),
):
    """Export the reading list to Pantry."""
    export(ExportFormat.PANTRY, pantry_id, basket_id)
