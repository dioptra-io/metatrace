import typer

from metatrace.cli.metadata.base import MetadataCLI
from metatrace.lib.metadata.geo import GeolocationMetadata


class GeolocationMetadataCLI(MetadataCLI):
    metadata_cls = GeolocationMetadata

    @classmethod
    def add(
        cls, ctx: typer.Context, license_key: str = typer.Option(..., metavar="KEY")
    ) -> None:
        slug = GeolocationMetadata.create(ctx.obj["client"])
        GeolocationMetadata.insert(ctx.obj["client"], slug, license_key)