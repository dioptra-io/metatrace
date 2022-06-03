from typing import Optional

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
        api_key: Optional[str] = typer.Option(
            None,
            help="Optional PeeringDB API key to avoid rate-limiting",
            metavar="KEY",
        ),
    ) -> None:
        identifier = IXPMetadata.create(ctx.obj["client"])  # , source)
        try:
            IXPMetadata.insert(ctx.obj["client"], identifier, source, api_key)
        except Exception as e:
            IXPMetadata.delete(ctx.obj["client"], identifier)
            raise e
