from datetime import datetime

import typer
from pint import UnitRegistry
from rich.console import Console
from rich.table import Table

from metatrace.lib.metadata.ixp import (
    MetadataIXPSource,
    create_ixp_metadata,
    drop_ixp_metadata,
    insert_ixp_metadata,
    list_ixp_metadata,
    query_ixp_metadata,
)

app = typer.Typer()


@app.command()
def add(
    ctx: typer.Context,
    source: MetadataIXPSource = typer.Option(MetadataIXPSource.PeeringDB.value),
) -> None:
    slug = create_ixp_metadata(ctx.obj["client"], source)
    insert_ixp_metadata(ctx.obj["client"], slug, source)


@app.command()
def remove(ctx: typer.Context, slug: list[str]) -> None:
    for slug_ in slug:
        drop_ixp_metadata(ctx.obj["client"], slug_)


@app.command("list")
def list_(ctx: typer.Context) -> None:
    ureg = UnitRegistry()
    table = Table()
    table.add_column("Slug")
    table.add_column("Source")
    table.add_column("Creation date")
    table.add_column("Rows")
    table.add_column("Size")
    tables = list_ixp_metadata(ctx.obj["client"])
    for t in tables:
        total_bytes = t["total_bytes"] * ureg.byte
        table.add_row(
            t["attributes"]["slug"],
            t["attributes"]["source"],
            datetime.fromisoformat(t["attributes"]["created_at"]).strftime("%c"),
            str(t["total_rows"]),
            f"{total_bytes:P#~}",
        )
    console = Console()
    console.print(table)


@app.command()
def query(ctx: typer.Context, slug: str, address: str) -> None:
    typer.echo(query_ixp_metadata(ctx.obj["client"], slug, address))
