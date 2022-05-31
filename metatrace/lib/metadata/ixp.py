import random
from datetime import datetime
from enum import Enum

from pych_client import ClickHouseClient

from metatrace.lib.clickhouse import create_dict, create_table


class MetadataIXPSource(Enum):
    PeeringDB = "peeringdb"


def create_metadata_ixp(
    client: ClickHouseClient, source: MetadataIXPSource
) -> tuple[str, str]:
    h = random.getrandbits(16)
    created_at = datetime.now()
    slug = f"{created_at:%Y%m%d%H%M}_{h:04x}"
    attributes = {
        "created_at": created_at.isoformat(),
        "slug": slug,
        "source": source.value,
    }
    table_name = f"metadata_table_ixp_{slug}"
    dict_name = f"metadata_dict_ixp_{slug}"
    create_table(
        client,
        table_name,
        [("prefix", "String"), ("ixp", "String")],
        "prefix",
        attributes,
    )
    create_dict(
        client,
        dict_name,
        [("prefix", "String"), ("ixp", "String")],
        "prefix",
        f"SELECT * FROM {table_name}",
        attributes,
    )
    return table_name, dict_name
