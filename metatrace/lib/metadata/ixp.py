from enum import Enum

from fetchmesh.peeringdb import PeeringDB
from pych_client import ClickHouseClient

from metatrace.lib.clickhouse import insert_into
from metatrace.lib.metadata.base import Metadata


class IXPMetadataSource(Enum):
    PeeringDB = "peeringdb"


class IXPMetadata(Metadata):
    attributes = {"ixp": "String"}
    shortname = "asn"

    @classmethod
    def insert(
        cls, client: ClickHouseClient, slug: str, source: IXPMetadataSource
    ) -> None:
        rows = []
        match source:
            case IXPMetadataSource.PeeringDB:
                pdb = PeeringDB.from_api()
                for obj in pdb.objects:
                    for prefix in obj.prefixes:
                        rows.append({"prefix": prefix.prefix, "ixp": obj.ix.name})
        insert_into(client, cls.table_name(slug), rows)
