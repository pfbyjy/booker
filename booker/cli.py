from typing import Optional

import typer

from booker import __app_name__, __version__

app = typer.Typer()


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
