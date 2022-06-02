from datetime import datetime

from fetchmesh.bgp import Collector
from pyasn.mrtx import parse_mrt_file
from pych_client import ClickHouseClient

from metatrace.lib.clickhouse import (
    create_dict,
    create_table,
    drop_dict,
    drop_table,
    insert_into,
    list_tables,
)
from metatrace.lib.logger import logger
from metatrace.lib.naming import make_slug, metadata_dict_name, metadata_table_name


def create_asn_metadata(
    client: ClickHouseClient, collector: Collector, date: datetime
) -> str:
    created_at = datetime.now()
    slug = make_slug(created_at)
    attributes = {
        "created_at": created_at.isoformat(),
        "slug": slug,
        "collector": collector.fqdn,
        "date": date.isoformat(),
    }
    columns = [
        ("prefix", "String"),
        ("asn", "UInt32"),
    ]
    database = client.config["database"]
    create_table(
        client,
        metadata_table_name("asn", slug),
        columns,
        "prefix",
        attributes=attributes,
    )
    create_dict(
        client,
        metadata_dict_name("asn", slug),
        columns,
        "prefix",
        f"SELECT * FROM {database}.{metadata_table_name('asn', slug)}",
        attributes=attributes,
    )
    return slug


def insert_asn_metadata(
    client: ClickHouseClient, slug: str, collector: Collector, date: datetime
) -> None:
    logger.info("Downloading RIB...")
    rib = collector.download_rib(date, ".")
    logger.info("Parsing RIB...")
    prefixes = parse_mrt_file(str(rib), print_progress=True, skip_record_on_error=False)
    rows = [
        {"prefix": prefix, "asn": asn if isinstance(asn, int) else asn.pop()}
        for prefix, asn in prefixes.items()
    ]
    insert_into(client, metadata_table_name("asn", slug), rows)


def drop_asn_metadata(client: ClickHouseClient, slug: str) -> None:
    drop_dict(client, metadata_dict_name("asn", slug))
    drop_table(client, metadata_table_name("asn", slug))


def list_asn_metadata(client: ClickHouseClient) -> list[dict]:
    return list_tables(client, metadata_table_name("asn", ""))


def query_asn_metadata(client: ClickHouseClient, slug: str, address: str) -> str:
    query = "SELECT dictGetUInt32({name:String}, {col:String}, toIPv6({val:String}))"
    return client.text(
        query, {"name": metadata_dict_name("asn", slug), "col": "asn", "val": address}
    )
