import logging
from enum import Enum
from typing import Optional

import typer
from pych_client import ClickHouseClient
from rich.logging import RichHandler

from metatrace import __version__
from metatrace.cli import metadata
from metatrace.lib.credentials import get_credentials

app = typer.Typer()
app.add_typer(metadata.app, name="metadata")


class LogLevel(Enum):
    NotSet = "NOTSET"
    Debug = "DEBUG"
    Info = "INFO"
    Warning = "WARNING"
    Error = "ERROR"
    Critical = "CRITICAL"


def version_callback(value: bool):
    if value:
        typer.echo(f"metatrace {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    ctx: typer.Context,
    base_url: Optional[str] = typer.Option(None, metavar="URL"),
    database: Optional[str] = typer.Option(None, metavar="DATABASE"),
    username: Optional[str] = typer.Option(None, metavar="USERNAME"),
    password: Optional[str] = typer.Option(None, metavar="PASSWORD"),
    log_level: Optional[LogLevel] = typer.Option(None, case_sensitive=False),
    _version: Optional[bool] = typer.Option(
        None,
        "--version",
        callback=version_callback,
        help="Print program version.",
    ),
):
    if log_level:
        logging.basicConfig(
            format="%(message)s",
            handlers=[RichHandler()],
            level=log_level.value,
        )
    client = ClickHouseClient(*get_credentials(base_url, database, username, password))
    ctx.obj = {"client": client}
