from datetime import datetime

from pych_client import ClickHouseClient

from metatrace.lib.clickhouse import (
    create_dict,
    create_table,
    drop_dict,
    drop_table,
    list_tables,
)
from metatrace.lib.naming import make_slug


class Metadata:
    attributes: dict[str, str]
    shortname: str

    @classmethod
    def create(cls, client: ClickHouseClient) -> str:
        created_at = datetime.now()
        slug = make_slug(created_at)
        info = {
            "created_at": created_at.isoformat(),
            "slug": slug,
        }
        columns = [("prefix", "String"), *cls.attributes.items()]
        database = client.config["database"]
        query = f"SELECT * FROM {database}.{cls.table_name(slug)}"
        create_table(client, cls.table_name(slug), columns, "prefix", info=info)
        create_dict(client, cls.dict_name(slug), columns, "prefix", query, info=info)
        return slug

    @classmethod
    def drop(cls, client: ClickHouseClient, slug: str) -> None:
        drop_dict(client, cls.dict_name(slug))
        drop_table(client, cls.table_name(slug))

    @classmethod
    def list(cls, client: ClickHouseClient) -> list[dict]:
        return list_tables(client, cls.table_name(""))

    @classmethod
    def query(
        cls, client: ClickHouseClient, slug: str, attribute: str, address: str
    ) -> str:
        function = f"dictGet{cls.attributes[attribute]}"
        query = f"SELECT {function}({{dict_name:String}}, {{attr_names:String}}, toIPv6({{id_expr:String}}))"
        return client.text(
            query,
            {
                "dict_name": cls.dict_name(slug),
                "attr_names": attribute,
                "id_expr": address,
            },
        )

    @classmethod
    def dict_name(cls, slug: str) -> str:
        return f"metadata_dict_{cls.shortname}_{slug}"

    @classmethod
    def table_name(cls, slug: str) -> str:
        return f"metadata_table_{cls.shortname}_{slug}"
