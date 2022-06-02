import logging
from enum import Enum
from typing import Optional

import typer
from pint import UnitRegistry
from pych_client import ClickHouseClient
from rich.console import Console
from rich.logging import RichHandler

from metatrace import __version__
from metatrace.cli import data
from metatrace.cli.metadata.asn import ASNMetadataCLI
from metatrace.cli.metadata.geo import GeolocationMetadataCLI
from metatrace.cli.metadata.ixp import IXPMetadataCLI
from metatrace.lib.credentials import get_credentials

app = typer.Typer(
    context_settings={"max_content_width": 200},
    epilog="""
To get more help with metatrace, check out the documentation
at https://github.com/dioptra-io/metatrace/
""",
)
app.add_typer(
    data.app,
    help="Manage traceroute data",
    name="data",
)
app.add_typer(
    ASNMetadataCLI.to_typer(),
    help="Manage AS numbers metadata",
    name="asn",
)
app.add_typer(
    GeolocationMetadataCLI.to_typer(),
    help="Manage geolocation metadata",
    name="geo",
)
app.add_typer(
    IXPMetadataCLI.to_typer(),
    help="Manage IXP metadata",
    name="ixp",
)


class LogLevel(Enum):
    NotSet = "NOTSET"
    Debug = "DEBUG"
    Info = "INFO"
    Warning = "WARNING"
    Error = "ERROR"
    Critical = "CRITICAL"


def version_callback(value: bool) -> None:
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
) -> None:
    if log_level:
        logging.basicConfig(
            format="%(message)s",
            handlers=[RichHandler()],
            level=log_level.value,
        )
    ctx.obj = {
        "client": ClickHouseClient(
            *get_credentials(base_url, database, username, password)
        ),
        "console": Console(),
        "units": UnitRegistry(),
    }
