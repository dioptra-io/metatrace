from datetime import datetime
from enum import Enum

from fetchmesh.peeringdb import PeeringDB
from pych_client import ClickHouseClient

from metatrace.lib.clickhouse import (
    create_dict,
    create_table,
    drop_dict,
    drop_table,
    insert_into,
    list_tables,
)
from metatrace.lib.metadata.utils import dict_name, make_slug, table_name


class MetadataIXPSource(Enum):
    PeeringDB = "peeringdb"


def create_ixp_metadata(client: ClickHouseClient, source: MetadataIXPSource) -> str:
    created_at = datetime.now()
    slug = make_slug(created_at)
    attributes = {
        "created_at": created_at.isoformat(),
        "slug": slug,
        "source": source.value,
    }
    columns = [
        ("prefix", "String"),
        ("ixp", "String"),
    ]
    create_table(
        client,
        table_name("ixp", slug),
        columns,
        "prefix",
        attributes,
    )
    create_dict(
        client,
        dict_name("ixp", slug),
        columns,
        "prefix",
        f"SELECT * FROM {table_name('ixp', slug)}",
        attributes,
    )
    return slug


def insert_ixp_metadata(
    client: ClickHouseClient, slug: str, source: MetadataIXPSource
) -> None:
    rows = []
    match source:
        case MetadataIXPSource.PeeringDB:
            pdb = PeeringDB.from_api()
            for object in pdb.objects:
                for prefix in object.prefixes:
                    rows.append({"prefix": prefix.prefix, "ixp": object.ix.name})
    insert_into(client, table_name("ixp", slug), rows)


def drop_ixp_metadata(client: ClickHouseClient, slug: str) -> None:
    drop_dict(client, dict_name("ixp", slug))
    drop_table(client, table_name("ixp", slug))


def list_ixp_metadata(client: ClickHouseClient) -> list[dict]:
    return list_tables(client, table_name("ixp", ""))


def query_ixp_metadata(client: ClickHouseClient, slug: str, address: str) -> str:
    query = "SELECT dictGetString({name:String}, {col:String}, toIPv6({val:String}))"
    return client.text(
        query, {"name": dict_name("ixp", slug), "col": "ixp", "val": address}
    )
