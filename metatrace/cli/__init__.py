from typing import Optional

import typer
from pych_client import ClickHouseClient

from metatrace.cli import metadata
from metatrace.lib.credentials import get_credentials

app = typer.Typer()
app.add_typer(metadata.app, name="metadata")


@app.callback()
def main(
    ctx: typer.Context,
    base_url: Optional[str] = typer.Option(None, metavar="URL"),
    database: Optional[str] = typer.Option(None, metavar="DATABASE"),
    username: Optional[str] = typer.Option(None, metavar="USERNAME"),
    password: Optional[str] = typer.Option(None, metavar="PASSWORD"),
):
    client = ClickHouseClient(*get_credentials(base_url, database, username, password))
    ctx.obj = {"client": client}
