import logging
import webbrowser
from enum import Enum
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Optional

import typer
import uvicorn
from jinja2 import Environment, PackageLoader, select_autoescape
from pint import UnitRegistry
from pych_client import ClickHouseClient
from rich.console import Console
from rich.logging import RichHandler

from metatrace import __version__
from metatrace.cli import data
from metatrace.cli.metadata import (
    ASNMetadataCLI,
    GeolocationMetadataCLI,
    IXPMetadataCLI,
)
from metatrace.lib.credentials import CREDENTIALS_FILE, get_credentials

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
    Trace = "TRACE"
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
    base_url: Optional[str] = typer.Option(
        None,
        help="ClickHouse HTTP(S) URL.",
        metavar="URL",
    ),
    database: Optional[str] = typer.Option(
        None,
        help="ClickHouse database.",
        metavar="DATABASE",
    ),
    username: Optional[str] = typer.Option(
        None,
        help="ClickHouse username.",
        metavar="USERNAME",
    ),
    password: Optional[str] = typer.Option(
        None,
        help="ClickHouse password.",
        metavar="PASSWORD",
    ),
    credentials_file: Path = typer.Option(
        CREDENTIALS_FILE,
        help="JSON file containing the credentials.",
    ),
    log_level: LogLevel = typer.Option(LogLevel.Info.value, case_sensitive=False),
    _version: Optional[bool] = typer.Option(
        None,
        "--version",
        callback=version_callback,
        help="Print program version.",
    ),
) -> None:
    logging.basicConfig(
        datefmt="[%X]",
        format="%(message)s",
        handlers=[RichHandler(console=Console(stderr=True), show_path=False)],
        level=log_level.value,
    )
    ctx.obj = {
        "client": ClickHouseClient(
            *get_credentials(credentials_file, base_url, database, username, password)
        ),
        "console": Console(),
        "log_level": log_level.value,
        "units": UnitRegistry(),
    }


@app.command(help="Start MetaTrace API server")
def server(
    ctx: typer.Context,
    host: str = typer.Option("127.0.0.1", help="The IP address to listen on."),
    port: int = typer.Option(5555, help="The port to listen on."),
    browser: bool = typer.Option(True, help="Whether to open the web browser or not."),
) -> None:
    env = Environment(loader=PackageLoader("metatrace"), autoescape=select_autoescape())
    template = env.get_template("wait.html")
    # TODO: Pass base_url, ...
    with NamedTemporaryFile("w", suffix=".html") as f:
        f.write(template.render(host=host, port=port))
        f.flush()
        if browser:
            webbrowser.open(f"file:///{f.name}")
        uvicorn.run(
            "metatrace.api:app",
            host=host,
            port=port,
            log_level=ctx.obj["log_level"].lower(),
        )
