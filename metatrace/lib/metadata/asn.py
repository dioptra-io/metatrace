from datetime import datetime

from fetchmesh.bgp import Collector
from pyasn.mrtx import parse_mrt_file
from pych_client import ClickHouseClient

from metatrace.lib.clickhouse import insert_into
from metatrace.lib.metadata.base import Metadata

# TODO: Store collector, ... info in table
# Override create for this?
from metatrace.lib.utilities import download_file, temporary_directory


class ASNMetadata(Metadata):
    attributes = {"asn": "UInt32"}
    shortname = "asn"

    @classmethod
    def insert(
        cls,
        client: ClickHouseClient,
        identifier: str,
        collector: Collector,
        date: datetime,
    ) -> None:
        # TODO: Find RIB closest to date.
        with temporary_directory() as path:
            rib = path / collector.table_name(date)
            download_file(collector.table_url(date), {}, rib)
            # TODO: Show parsing progress
            prefixes = parse_mrt_file(
                str(rib), print_progress=True, skip_record_on_error=False
            )
        rows = [
            {"prefix": prefix, "asn": asn if isinstance(asn, int) else asn.pop()}
            for prefix, asn in prefixes.items()
        ]
        insert_into(client, cls.table_name(identifier), rows)
