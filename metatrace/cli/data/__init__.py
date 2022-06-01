from datetime import datetime

import typer
from pint import UnitRegistry
from rich.console import Console
from rich.table import Table

from metatrace.lib.data import DataSource, create_data, drop_data, list_data

app = typer.Typer()


@app.command()
def init(
    ctx: typer.Context,
    source: DataSource = typer.Option(DataSource.Ark.value),
    asn_metadata_slug: str = typer.Option(..., metavar="SLUG"),
    ixp_metadata_slug: str = typer.Option(..., metavar="SLUG"),
) -> None:
    slug = create_data(ctx.obj["client"], source, asn_metadata_slug, ixp_metadata_slug)
    typer.echo(slug)


@app.command()
def remove(ctx: typer.Context, slug: list[str]) -> None:
    for slug_ in slug:
        drop_data(ctx.obj["client"], slug_)


@app.command("list")
def list_(ctx: typer.Context) -> None:
    ureg = UnitRegistry()
    table = Table()
    table.add_column("Slug")
    table.add_column("Source")
    table.add_column("Creation date")
    table.add_column("Rows")
    table.add_column("Size")
    tables = list_data(ctx.obj["client"])
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
