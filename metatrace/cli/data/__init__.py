from datetime import datetime
from typing import Optional

import typer

from metatrace.lib.data import (
    DataSource,
    create_data,
    delete_data,
    insert_data,
    list_data,
    query_data,
)
from metatrace.lib.metadata import ASNMetadata, GeolocationMetadata, IXPMetadata
from metatrace.lib.utilities import print_tables

app = typer.Typer()


@app.command()
def create(
    ctx: typer.Context,
    asn_metadata: Optional[str] = typer.Option(None, metavar="IDENTIFIER"),
    geo_metadata: Optional[str] = typer.Option(None, metavar="IDENTIFIER"),
    ixp_metadata: Optional[str] = typer.Option(None, metavar="IDENTIFIER"),
) -> None:
    identifier = create_data(
        ctx.obj["client"],
        ASNMetadata.dict_name(asn_metadata) if asn_metadata else None,
        GeolocationMetadata.dict_name(geo_metadata) if geo_metadata else None,
        IXPMetadata.dict_name(ixp_metadata) if ixp_metadata else None,
    )
    typer.echo(identifier)


@app.command()
def insert(
    ctx: typer.Context,
    identifier: str,
    source: DataSource,
    start: datetime,
    stop: datetime,
    agents: Optional[str] = typer.Option(
        None,
        help="Agents not included in this comma-separated get will be excluded",
        metavar="AGENTS",
    ),
) -> None:
    agents_set = set(agents.split(",")) if agents else set()
    insert_data(ctx.obj["client"], identifier, source, start, stop, agents_set)


@app.command()
def delete(ctx: typer.Context, identifier: list[str]) -> None:
    for identifier_ in identifier:
        delete_data(ctx.obj["client"], identifier_)


@app.command()
def get(ctx: typer.Context, quiet: bool = typer.Option(False, "--quiet", "-q")) -> None:
    tables = list_data(ctx.obj["client"])
    print_tables(ctx.obj["console"], ctx.obj["units"], tables, quiet)


@app.command()
def query(ctx: typer.Context, identifier: str) -> None:
    for line in query_data(ctx.obj["client"], identifier):
        typer.echo(line)
