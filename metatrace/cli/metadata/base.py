from typing import Type

import typer

from metatrace.lib.metadata.base import Metadata
from metatrace.lib.utilities import print_tables


class MetadataCLI:
    metadata_cls: Type[Metadata]

    @classmethod
    def list_(
        cls, ctx: typer.Context, quiet: bool = typer.Option(False, "--quiet", "-q")
    ) -> None:
        tables = cls.metadata_cls.list(ctx.obj["client"])
        print_tables(ctx.obj["console"], ctx.obj["units"], tables, quiet)

    @classmethod
    def remove(cls, ctx: typer.Context, identifier: list[str]) -> None:
        for s in identifier:
            cls.metadata_cls.drop(ctx.obj["client"], s)

    @classmethod
    def query(
        cls, ctx: typer.Context, identifier: str, attribute: str, address: str
    ) -> None:
        typer.echo(
            cls.metadata_cls.query(ctx.obj["client"], identifier, attribute, address)
        )

    @classmethod
    def to_typer(cls) -> typer.Typer:
        app = typer.Typer()
        if add := getattr(cls, "add"):
            app.command()(add)
        app.command("list")(cls.list_)
        app.command()(cls.remove)
        app.command()(cls.query)
        return app
