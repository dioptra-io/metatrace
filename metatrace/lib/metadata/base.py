from datetime import datetime

from pych_client import ClickHouseClient

from metatrace.lib.clickhouse import (
    create_dict,
    create_table,
    drop_dict,
    drop_table,
    list_tables,
)
from metatrace.lib.naming import make_identifier


class Metadata:
    attributes: dict[str, str]
    shortname: str

    @classmethod
    def create(cls, client: ClickHouseClient) -> str:
        created_at = datetime.now()
        identifier = make_identifier(cls.shortname, created_at)
        info = {
            "created_at": created_at.isoformat(),
            "identifier": identifier,
        }
        columns = [("prefix", "String"), *cls.attributes.items()]
        database = client.config["database"]
        query = f"SELECT * FROM {database}.{cls.table_name(identifier)}"
        create_table(client, cls.table_name(identifier), columns, "prefix", info=info)
        create_dict(
            client, cls.dict_name(identifier), columns, "prefix", query, info=info
        )
        return identifier

    @classmethod
    def delete(cls, client: ClickHouseClient, identifier: str) -> None:
        drop_dict(client, cls.dict_name(identifier))
        drop_table(client, cls.table_name(identifier))

    @classmethod
    def get(cls, client: ClickHouseClient) -> list[dict]:
        return list_tables(client, cls.table_name(cls.shortname))

    @classmethod
    def query(
        cls, client: ClickHouseClient, identifier: str, attribute: str, address: str
    ) -> str:
        function = f"dictGet{cls.attributes[attribute]}"
        query = f"SELECT {function}({{dict_name:String}}, {{attr_names:String}}, toIPv6({{id_expr:String}}))"
        return client.text(
            query,
            {
                "dict_name": cls.dict_name(identifier),
                "attr_names": attribute,
                "id_expr": address,
            },
        )

    @classmethod
    def dict_name(cls, identifier: str) -> str:
        return f"metadata_dict_{identifier}"

    @classmethod
    def table_name(cls, identifier: str) -> str:
        return f"metadata_table_{identifier}"
