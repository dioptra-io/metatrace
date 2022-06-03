import typer

from metatrace.cli.metadata.base import MetadataCLI
from metatrace.lib.metadata import IXPMetadata, IXPMetadataSource


class IXPMetadataCLI(MetadataCLI):
    metadata_cls = IXPMetadata

    @classmethod
    def create(
        cls,
        ctx: typer.Context,
        source: IXPMetadataSource = typer.Option(IXPMetadataSource.PeeringDB.value),
    ) -> None:
        identifier = IXPMetadata.create(ctx.obj["client"])  # , source)
        IXPMetadata.insert(ctx.obj["client"], identifier, source)
