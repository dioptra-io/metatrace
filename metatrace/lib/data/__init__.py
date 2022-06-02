from datetime import datetime
from enum import Enum

from pych_client import ClickHouseClient

from metatrace.lib.clickhouse import create_table, drop_table, list_tables
from metatrace.lib.naming import data_table_name, make_slug


class DataSource(Enum):
    Ark = "ark"


def create_data(
    client: ClickHouseClient,
    source: DataSource,
    asn_metadata_slug: str,
    ixp_metadata_slug: str,
) -> str:
    created_at = datetime.now()
    slug = make_slug(created_at)
    attributes = {
        "created_at": created_at.isoformat(),
        "slug": slug,
        "source": source.value,
    }
    columns = [
        ("measurement_id", "String"),
        ("agent_id", "String"),
        ("traceroute_start", "DateTime", "CODEC(T64, ZSTD(1))"),
        ("probe_protocol", "UInt8"),
        ("probe_src_addr", "IPv6"),
        ("probe_dst_addr", "IPv6"),
        ("probe_src_port", "UInt16"),
        ("probe_dst_port", "UInt16"),
        ("probe_ttl", "UInt8"),
        ("reply_ttl", "UInt8"),
        ("reply_size", "UInt16"),
        ("reply_mpls_labels", "Array(Tuple(UInt32, UInt8, UInt8, UInt8))"),
        ("reply_src_addr", "IPv6"),
        ("reply_icmp_type", "UInt8"),
        ("reply_icmp_code", "UInt8"),
        ("rtt", "UInt16"),
        # Materialized columns
        (
            "probe_dst_prefix",
            "IPv6",
            "MATERIALIZED",
            "toIPv6(cutIPv6(probe_src_addr, 8, 1))",
        ),
        (
            "reply_src_prefix",
            "IPv6",
            "MATERIALIZED",
            "toIPv6(cutIPv6(reply_src_addr, 8, 1))",
        ),
        # (
        #     "reply_asn",
        #     "UInt32",
        #     "MATERIALIZED",
        #     f"dictGetUInt32('{metadata_dict_name('asn', asn_metadata_slug)}', 'asn', reply_src_addr)",
        # ),
        # (
        #     "reply_ixp",
        #     "String",
        #     "MATERIALIZED",
        #     f"dictGetString('{metadata_dict_name('ixp', ixp_metadata_slug)}', 'ixp', reply_src_addr)",
        # ),
        # Projections
        (
            "PROJECTION",
            "reply_src_addr_proj",
            "(SELECT agent_id, probe_dst_addr, traceroute_start, reply_src_addr ORDER BY reply_src_addr)",
        ),
        (
            "PROJECTION",
            "reply_asn_proj",
            "(SELECT agent_id, probe_dst_addr, traceroute_start, reply_asn ORDER BY reply_asn)",
        ),
        (
            "PROJECTION",
            "reply_ixp_proj",
            "(SELECT agent_id, probe_dst_addr, traceroute_start, reply_ixp ORDER BY reply_ixp)",
        ),
    ]
    order_by = [
        "agent_id",
        "probe_dst_addr",
        "traceroute_start",
    ]
    create_table(
        client,
        data_table_name(slug),
        columns,
        order_by,
        info=attributes,
        partition_by="toYYYYMM(traceroute_start)",
    )
    return slug


# def add_data(client: ClickHouseClient, source: DataSource)


def drop_data(client: ClickHouseClient, slug: str) -> None:
    drop_table(client, data_table_name(slug))


def list_data(client: ClickHouseClient) -> list[dict]:
    return list_tables(client, data_table_name(""))
