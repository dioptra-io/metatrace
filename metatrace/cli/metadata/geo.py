import typer

from metatrace.cli.metadata.base import MetadataCLI
from metatrace.lib.metadata import GeolocationMetadata


class GeolocationMetadataCLI(MetadataCLI):
    metadata_cls = GeolocationMetadata

    @classmethod
    def create(
        cls, ctx: typer.Context, license_key: str = typer.Option(..., metavar="KEY")
    ) -> None:
        identifier = GeolocationMetadata.create(ctx.obj["client"])
        try:
            GeolocationMetadata.insert(ctx.obj["client"], identifier, license_key)
        except Exception as e:
            GeolocationMetadata.delete(ctx.obj["client"], identifier)
            raise e
