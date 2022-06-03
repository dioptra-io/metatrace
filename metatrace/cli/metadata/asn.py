from datetime import datetime, timedelta, timezone

import typer

from metatrace.cli.metadata.base import MetadataCLI
from metatrace.lib.metadata import ASNMetadata
from metatrace.lib.sources import Collector


class ASNMetadataCLI(MetadataCLI):
    metadata_cls = ASNMetadata

    @classmethod
    def create(
        cls,
        ctx: typer.Context,
        collector: str = typer.Option("route-views2.routeviews.org", metavar="FQDN"),
        date: datetime = typer.Option(
            datetime.now(tz=timezone.utc) - timedelta(hours=2)
        ),
    ) -> None:
        if collector_ := Collector.from_fqdn(collector):
            date = collector_.closest(date)
            identifier = ASNMetadata.create(ctx.obj["client"])  # , collector_, date)
            ASNMetadata.insert(ctx.obj["client"], identifier, collector_, date)
        else:
            typer.echo(f"Unknown collector: {collector}")
