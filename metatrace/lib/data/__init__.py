import subprocess
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime
from enum import Enum
from typing import Iterator

from pych_client import ClickHouseClient
from pych_client.clickhouse_client import get_clickhouse_client_args
from rich.progress import track

from metatrace.lib.clickhouse import create_table, drop_table, list_tables
from metatrace.lib.naming import make_identifier
from metatrace.lib.sources.ark import ark_probe_data_list


class DataSource(Enum):
    ArkPrefixProbing = "ark-prefix-probing"
    ArkTeamProbing = "ark-team-probing"


def create_data(
    client: ClickHouseClient,
    asn_dict_name: str | None,
    geo_dict_name: str | None,
    ixp_dict_name: str | None,
) -> str:
    created_at = datetime.now()
    identifier = make_identifier("data", created_at)
    attributes = {
        "created_at": created_at.isoformat(),
        "identifier": identifier,
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
        (
            "PROJECTION",
            "reply_src_addr_proj",
            "(SELECT agent_id, probe_dst_addr, traceroute_start, reply_src_addr ORDER BY reply_src_addr)",
        ),
    ]
    # TODO: ORDER BY metadata, id in projections?
    if asn_dict_name:
        columns += [
            (
                "reply_asn",
                "UInt32",
                "MATERIALIZED",
                f"dictGetUInt32('{asn_dict_name}', 'asn', reply_src_addr)",
            ),
            (
                "PROJECTION",
                "reply_asn_proj",
                "(SELECT agent_id, probe_dst_addr, traceroute_start, reply_asn ORDER BY reply_asn)",
            ),
        ]
    if geo_dict_name:
        columns += [
            (
                "reply_country",
                "String",
                "MATERIALIZED",
                f"dictGetString('{geo_dict_name}', 'country', reply_src_addr)",
            ),
            (
                "PROJECTION",
                "reply_country_proj",
                "(SELECT agent_id, probe_dst_addr, traceroute_start, reply_country ORDER BY reply_country)",
            ),
        ]
    if ixp_dict_name:
        columns += [
            (
                "reply_ixp",
                "String",
                "MATERIALIZED",
                f"dictGetString('{ixp_dict_name}', 'ixp', reply_src_addr)",
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
        identifier,
        columns,
        order_by,
        info=attributes,
    )
    return identifier


def insert_data(
    client: ClickHouseClient,
    identifier: str,
    source: DataSource,
    start: datetime,
    stop: datetime,
    agents: set[str],
) -> None:
    match source:
        case DataSource.ArkPrefixProbing:
            files = []
        case DataSource.ArkTeamProbing:
            files = ark_probe_data_list(1, start, stop)
    with ProcessPoolExecutor(max_workers=4) as executor:
        # TODO: Cleanup zombie processes on exit (see fetchmesh code)
        futures = []
        for file in files:
            if agents and file.monitor not in agents:
                continue
            assert file.url
            futures.append(
                executor.submit(
                    _insert_file, config=client.config, table=identifier, url=file.url
                )
            )
        for future in track(as_completed(futures), total=len(futures)):
            future.result()


def _insert_file(config: dict, table: str, url: str) -> None:
    # TODO: Implement streaming in pantrace
    # TODO: Rollback if fails (use tag column + partition on tag + drop partition?)
    query = f"INSERT INTO {table} FORMAT JSONEachRow"
    curl = subprocess.Popen(
        ["curl", "--location", "--show-error", "--silent", url], stdout=subprocess.PIPE
    )
    gzip = subprocess.Popen(
        ["gzip", "--decompress", "--stdout"], stdin=curl.stdout, stdout=subprocess.PIPE
    )
    pantrace = subprocess.Popen(
        [
            "pantrace",
            "--from=warts-trace",
            "--to=internal",
        ],
        stdin=gzip.stdout,
        stdout=subprocess.PIPE,
    )
    clickhouse_client = subprocess.Popen(
        [
            "clickhouse",
            "client",
            *get_clickhouse_client_args(
                config,
                query,
                {"table": table},
                {
                    "date_time_input_format": "best_effort",
                    "input_format_skip_unknown_fields": 1,
                },
            ),
        ],
        stdin=pantrace.stdout,
    )
    if curl.stdout:
        curl.stdout.close()
    if gzip.stdout:
        gzip.stdout.close()
    if pantrace.stdout:
        pantrace.stdout.close()
    clickhouse_client.communicate()


def delete_data(client: ClickHouseClient, identifier: str) -> None:
    drop_table(client, identifier)


def list_data(client: ClickHouseClient) -> list[dict]:
    return list_tables(client, "data_")


def query_data(client: ClickHouseClient, identifier: str) -> Iterator[bytes]:
    query = """
    SELECT DISTINCT agent_id, probe_dst_addr, traceroute_start
    FROM {table:Identifier}
    FORMAT CSV
    """
    return client.iter_bytes(query, {"table": identifier})
