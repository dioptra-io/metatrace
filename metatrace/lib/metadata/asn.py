import random
from datetime import datetime

from fetchmesh.bgp import Collector
from pych_client import ClickHouseClient

from metatrace.lib.clickhouse import create_dict, create_table


def create_metadata_asn(client: ClickHouseClient, collector: Collector, date: datetime):
    h = random.getrandbits(16)
    created_at = datetime.now()
    slug = f"{created_at:%Y%m%d%H%M}_{h:04x}"
    attributes = {
        "created_at": created_at.isoformat(),
        "slug": slug,
        "collector": collector.fqdn,
        "date": date.isoformat(),
    }
    table_name = f"metadata_table_asn_{slug}"
    dict_name = f"metadata_dict_asn_{slug}"
    create_table(
        client,
        table_name,
        [("prefix", "String"), ("asn", "UInt32")],
        "prefix",
        attributes,
    )
    create_dict(
        client,
        dict_name,
        [("prefix", "String"), ("asn", "UInt32")],
        "prefix",
        f"SELECT * FROM {table_name}",
        attributes,
    )
    return table_name, dict_name
