from datetime import datetime

import typer
from fetchmesh.peeringdb import PeeringDB
from pint import UnitRegistry
from rich.console import Console
from rich.table import Table

from metatrace.lib.clickhouse import drop_dict, drop_table, insert_into, list_tables
from metatrace.lib.metadata.ixp import MetadataIXPSource, create_metadata_ixp

app = typer.Typer()


@app.command()
def add(
    ctx: typer.Context,
    source: MetadataIXPSource = typer.Option(MetadataIXPSource.PeeringDB.value),
):
    table_name, dict_name = create_metadata_ixp(ctx.obj["client"], source)
    rows = []
    match source:
        case MetadataIXPSource.PeeringDB:
            pdb = PeeringDB.from_api()
            for object in pdb.objects:
                for prefix in object.prefixes:
                    rows.append({"prefix": prefix.prefix, "ixp": object.ix.name})
    insert_into(ctx.obj["client"], table_name, rows)


@app.command()
def remove(ctx: typer.Context, slug: list[str]):
    for slug_ in slug:
        drop_dict(ctx.obj["client"], f"metadata_dict_ixp_{slug_}")
        drop_table(ctx.obj["client"], f"metadata_table_ixp_{slug_}")


@app.command("list")
def list_(ctx: typer.Context):
    ureg = UnitRegistry()
    table = Table()
    table.add_column("Slug")
    table.add_column("Source")
    table.add_column("Creation date")
    table.add_column("Rows")
    table.add_column("Size")
    tables = list_tables(ctx.obj["client"], "metadata_table_ixp_")
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
def query(ctx: typer.Context, slug: str, address: str):
    query = """
    SELECT dictGetString({name:String}, {col:String}, toIPv6({val:String}))
    """
    res = ctx.obj["client"].text(
        query, {"name": f"metadata_dict_ixp_{slug}", "col": "ixp", "val": address}
    )
    typer.echo(res)
