from datetime import datetime

import typer
from fetchmesh.bgp import Collector

from metatrace.cli.metadata.base import MetadataCLI
from metatrace.lib.metadata.asn import ASNMetadata


class ASNMetadataCLI(MetadataCLI):
    metadata_cls = ASNMetadata

    @classmethod
    def add(
        cls,
        ctx: typer.Context,
        collector: str = typer.Option("route-views2.routeviews.org", metavar="FQDN"),
        date: datetime = typer.Option(datetime(2022, 1, 1)),
    ) -> None:
        collector_ = Collector.from_fqdn(collector)
        identifier = ASNMetadata.create(ctx.obj["client"])  # , collector_, date)
        ASNMetadata.insert(ctx.obj["client"], identifier, collector_, date)
