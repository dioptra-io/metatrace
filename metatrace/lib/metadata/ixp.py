from enum import Enum

from pych_client import ClickHouseClient

from metatrace.lib.clickhouse import insert_into
from metatrace.lib.metadata import Metadata
from metatrace.lib.sources import PeeringDB


class IXPMetadataSource(Enum):
    PeeringDB = "peeringdb"


class IXPMetadata(Metadata):
    attributes = {"ixp": "String"}
    shortname = "ixp"

    @classmethod
    def insert(
        cls,
        client: ClickHouseClient,
        identifier: str,
        source: IXPMetadataSource,
        api_key: str | None,
    ) -> None:
        rows = []
        match source:
            case IXPMetadataSource.PeeringDB:
                pdb = PeeringDB.from_api(api_key=api_key)
                for obj in pdb.objects:
                    for prefix in obj.prefixes:
                        rows.append({"prefix": prefix.prefix, "ixp": obj.ix.name})
        insert_into(client, cls.table_name(identifier), rows)
