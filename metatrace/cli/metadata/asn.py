from datetime import datetime

import typer
from fetchmesh.bgp import Collector
from pint import UnitRegistry
from pyasn.mrtx import parse_mrt_file
from rich.console import Console
from rich.table import Table

from metatrace.lib.clickhouse import drop_dict, drop_table, insert_into, list_tables
from metatrace.lib.metadata.asn import create_metadata_asn

app = typer.Typer()


@app.command()
def add(
    ctx: typer.Context,
    collector: str = typer.Option("route-views2.routeviews.org", metavar="FQDN"),
    date: datetime = typer.Option(datetime(2022, 1, 1)),
    print_progress: bool = True,
    skip_record_on_error: bool = False,
):
    collector_ = Collector.from_fqdn(collector)
    table_name, dict_name = create_metadata_asn(ctx.obj["client"], collector_, date)
    typer.echo("Downloading RIB...")
    rib = collector_.download_rib(date, ".")
    typer.echo("Parsing RIB...")
    prefixes = parse_mrt_file(str(rib), print_progress, skip_record_on_error)
    rows = [
        {"prefix": prefix, "asn": asn if isinstance(asn, int) else asn.pop()}
        for prefix, asn in prefixes.items()
    ]
    insert_into(ctx.obj["client"], table_name, rows)


@app.command()
def remove(ctx: typer.Context, slug: list[str]):
    for slug_ in slug:
        drop_dict(ctx.obj["client"], f"metadata_dict_asn_{slug_}")
        drop_table(ctx.obj["client"], f"metadata_table_asn_{slug_}")


@app.command("list")
def list_(ctx: typer.Context):
    ureg = UnitRegistry()
    table = Table()
    table.add_column("Slug")
    table.add_column("Collector")
    table.add_column("Date")
    table.add_column("Creation date")
    table.add_column("Rows")
    table.add_column("Size")
    tables = list_tables(ctx.obj["client"], "metadata_table_asn_")
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
def query(ctx: typer.Context, slug: str, address: str):
    query = """
    SELECT dictGetUInt32({name:String}, {col:String}, toIPv6({val:String}))
    """
    res = ctx.obj["client"].text(
        query, {"name": f"metadata_dict_asn_{slug}", "col": "asn", "val": address}
    )
    typer.echo(res)
