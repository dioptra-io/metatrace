from typing import Type

import typer

from metatrace.lib.metadata import Metadata
from metatrace.lib.utilities import print_tables


class MetadataCLI:
    metadata_cls: Type[Metadata]

    @classmethod
    def get(
        cls, ctx: typer.Context, quiet: bool = typer.Option(False, "--quiet", "-q")
    ) -> None:
        tables = cls.metadata_cls.get(ctx.obj["client"])
        print_tables(ctx.obj["console"], ctx.obj["units"], tables, quiet)

    @classmethod
    def delete(cls, ctx: typer.Context, identifier: list[str]) -> None:
        for s in identifier:
            cls.metadata_cls.delete(ctx.obj["client"], s)

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
        app.command(help="Create a resource")(getattr(cls, "create"))
        app.command(help="Display one or many resources")(cls.get)
        app.command(help="Delete resources")(cls.delete)
        app.command(help="Query a resource")(cls.query)
        return app
