from datetime import datetime

import typer
from fetchmesh.bgp import Collector
from pint import UnitRegistry
from rich.console import Console
from rich.table import Table

from metatrace.lib.metadata.asn import (
    create_asn_metadata,
    drop_asn_metadata,
    insert_asn_metadata,
    list_asn_metadata,
    query_asn_metadata,
)

app = typer.Typer()


@app.command()
def add(
    ctx: typer.Context,
    collector: str = typer.Option("route-views2.routeviews.org", metavar="FQDN"),
    date: datetime = typer.Option(datetime(2022, 1, 1)),
) -> None:
    collector_ = Collector.from_fqdn(collector)
    slug = create_asn_metadata(ctx.obj["client"], collector_, date)
    insert_asn_metadata(ctx.obj["client"], slug, collector_, date)


@app.command()
def remove(ctx: typer.Context, slug: list[str]) -> None:
    for slug_ in slug:
        drop_asn_metadata(ctx.obj["client"], slug_)


@app.command("list")
def list_(ctx: typer.Context) -> None:
    ureg = UnitRegistry()
    table = Table()
    table.add_column("Slug")
    table.add_column("Collector")
    table.add_column("Date")
    table.add_column("Creation date")
    table.add_column("Rows")
    table.add_column("Size")
    tables = list_asn_metadata(ctx.obj["client"])
    for t in tables:
        total_bytes = t["total_bytes"] * ureg.byte
        table.add_row(
            t["attributes"]["slug"],
            t["attributes"]["collector"],
            datetime.fromisoformat(t["attributes"]["date"]).strftime("%c"),
            datetime.fromisoformat(t["attributes"]["created_at"]).strftime("%c"),
            str(t["total_rows"]),
            f"{total_bytes:P#~}",
        )
    console = Console()
    console.print(table)


@app.command()
def query(ctx: typer.Context, slug: str, address: list[str]) -> None:
    for address_ in address:
        typer.echo(query_asn_metadata(ctx.obj["client"], slug, address_))
