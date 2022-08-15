from typing import Optional

from pathlib import Path
import typer

from booker import (
    ERRORS,
    __app_name__,
    __version__,
    config,
    database,
)

app = typer.Typer()


@app.command()
def init(
    db_path: str = typer.Option(
        str(database.DEFAULT_DB_FILE_PATH),
        "--db-path",
        "-db",
        prompt="book database location?",
    ),
) -> None:
    app_init_error = config.init_app(db_path)
    if app_init_error:
        typer.secho(
            f'Creating config file failed with "{ERRORS[app_init_error]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    db_init_error = database.init_database(Path(db_path))
    if db_init_error:
        typer.secho(
            f'Creating database failed with "{Errors[db_init_error]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    else:
        typer.secho(f"The book database is {db_path}", fg=typer.colors.GREEN)


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
