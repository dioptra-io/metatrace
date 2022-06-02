import typer

from metatrace.lib.data import DataSource, create_data, drop_data, list_data
from metatrace.lib.utilities import print_tables

app = typer.Typer()


@app.command()
def init(
    ctx: typer.Context,
    source: DataSource = typer.Option(DataSource.Ark.value),
    asn_metadata: str = typer.Option(..., metavar="IDENTIFIER"),
    geo_metadata: str = typer.Option(..., metavar="IDENTIFIER"),
    ixp_metadata: str = typer.Option(..., metavar="IDENTIFIER"),
) -> None:
    identifier = create_data(
        ctx.obj["client"], source, asn_metadata, geo_metadata, ixp_metadata
    )
    typer.echo(identifier)


@app.command()
def remove(ctx: typer.Context, identifier: list[str]) -> None:
    for identifier_ in identifier:
        drop_data(ctx.obj["client"], identifier_)


@app.command("list")
def list_(
    ctx: typer.Context, quiet: bool = typer.Option(False, "--quiet", "-q")
) -> None:
    tables = list_data(ctx.obj["client"])
    print_tables(ctx.obj["console"], ctx.obj["units"], tables, quiet)
