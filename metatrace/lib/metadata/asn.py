from datetime import datetime

from fetchmesh.bgp import Collector
from pyasn.mrtx import parse_mrt_file
from pych_client import ClickHouseClient

from metatrace.lib.clickhouse import insert_into
from metatrace.lib.logger import logger
from metatrace.lib.metadata.base import Metadata


# TODO: Store collector, ... info in table
# Override create for this?
class ASNMetadata(Metadata):
    attributes = {"asn": "UInt32"}
    shortname = "asn"

    @classmethod
    def insert(
        cls, client: ClickHouseClient, slug: str, collector: Collector, date: datetime
    ) -> None:
        logger.info("Downloading RIB...")
        rib = collector.download_rib(date, ".")
        logger.info("Parsing RIB...")
        prefixes = parse_mrt_file(
            str(rib), print_progress=True, skip_record_on_error=False
        )
        rows = [
            {"prefix": prefix, "asn": asn if isinstance(asn, int) else asn.pop()}
            for prefix, asn in prefixes.items()
        ]
        insert_into(client, cls.table_name(slug), rows)
