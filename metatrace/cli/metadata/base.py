from datetime import datetime
from typing import Type

import typer
from babel.dates import format_timedelta
from pint import UnitRegistry
from rich.console import Console
from rich.table import Table

from metatrace.lib.metadata.base import Metadata


class MetadataCLI:
    metadata_cls: Type[Metadata]

    @classmethod
    def list_(
        cls, ctx: typer.Context, quiet: bool = typer.Option(False, "--quiet", "-q")
    ) -> None:
        # TODO: Autogenerate from attributes
        tables = cls.metadata_cls.list(ctx.obj["client"])
        if quiet:
            for t in tables:
                typer.echo(t["info"]["slug"])
            return
        ureg = UnitRegistry()
        table = Table(box=None, header_style="")
        table.add_column("SLUG")
        table.add_column("CREATED")
        table.add_column("ROWS")
        table.add_column("SIZE")
        for t in tables:
            created_at = (
                datetime.fromisoformat(t["info"]["created_at"]) - datetime.now()
            )
            total_bytes = t["total_bytes"] * ureg.byte
            table.add_row(
                t["info"]["slug"],
                format_timedelta(created_at, add_direction=True),
                str(t["total_rows"]),
                f"{total_bytes:.2fP#~}",
            )
        console = Console()
        console.print(table)

    @classmethod
    def remove(cls, ctx: typer.Context, slug: list[str]) -> None:
        for s in slug:
            cls.metadata_cls.drop(ctx.obj["client"], s)

    @classmethod
    def query(cls, ctx: typer.Context, slug: str, attribute: str, address: str) -> None:
        typer.echo(cls.metadata_cls.query(ctx.obj["client"], slug, attribute, address))

    @classmethod
    def to_typer(cls) -> typer.Typer:
        app = typer.Typer()
        if add := getattr(cls, "add"):
            app.command(add)
        app.command("list")(cls.list_)
        app.command()(cls.remove)
        app.command()(cls.query)
        return app
