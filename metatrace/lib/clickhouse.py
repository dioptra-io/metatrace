import json
from collections.abc import Sequence
from json import JSONDecodeError

from pych_client import ClickHouseClient
from rich.progress import track

from metatrace.lib.logger import logger


def make_schema(columns: Sequence[tuple[str, ...]]) -> str:
    """
    >>> make_schema([("a", "UInt8"), ("b", "String", "CODEC(T64, ZSTD(1))")])
    'a UInt8, b String CODEC(T64, ZSTD(1))'
    """
    return ", ".join(" ".join(x) for x in columns)


# As of v22.6.1 ClickHouse does not support parameter interpolation
# for all the parameters of the CREATE statement; so we perform it in Python.
def create_dict(
    client: ClickHouseClient,
    name: str,
    columns: Sequence[tuple[str, ...]],
    primary_key: str,
    query: str,
    *,
    info: dict | None = None,
) -> None:
    user = client.config["username"]
    password = client.config["password"]
    database = client.config["database"]
    comment = json.dumps(info or {})
    query = f"""
    CREATE DICTIONARY {name} ({make_schema(columns)})
    PRIMARY KEY {primary_key}
    SOURCE(CLICKHOUSE(
        USER '{user}'
        PASSWORD '{password}'
        DB '{database}'
        QUERY '{query}'
    ))
    LIFETIME(0)
    LAYOUT(IP_TRIE)
    COMMENT '{comment}'
    """
    client.execute(query)


def create_table(
    client: ClickHouseClient,
    name: str,
    columns: Sequence[tuple[str, ...]],
    order_by: Sequence[str] | str,
    *,
    info: dict | None = None,
    settings: dict | None = None,
    partition_by: str | None = None,
) -> None:
    if isinstance(order_by, str):
        order_by = [order_by]
    comment = json.dumps(info or {})
    partition = f"PARTITION BY {partition_by}" if partition_by else ""
    query = f"""
    CREATE TABLE {name} ({make_schema(columns)})
    ENGINE = MergeTree
    {partition}
    ORDER BY ({', '.join(order_by)})
    COMMENT '{comment}'
    """
    client.execute(query)


def drop_dict(client: ClickHouseClient, name: str) -> None:
    client.execute("DROP DICTIONARY {name:Identifier}", {"name": name})


def drop_table(client: ClickHouseClient, name: str) -> None:
    client.execute("DROP TABLE {name:Identifier}", {"name": name})


def insert_into(client: ClickHouseClient, name: str, rows: list[dict]) -> None:
    data = (json.dumps(row).encode() for row in rows)
    client.execute(
        "INSERT INTO {name:Identifier} FORMAT JSONEachRow",
        params={"name": name},
        data=track(data, description=f"INSERT INTO {name}", total=len(rows)),
    )


def list_tables(client: ClickHouseClient, prefix: str) -> list[dict]:
    query = """
    SELECT
        name,
        comment AS info,
        total_bytes,
        total_rows
    FROM system.tables
    WHERE database = {database:String} AND startsWith(name, {prefix:String})
    """
    tables = []
    rows = client.json(query, {"database": client.config["database"], "prefix": prefix})
    for row in rows:
        try:
            row["info"] = json.loads(row["info"])
            tables.append(row)
        except JSONDecodeError:
            logger.exception("Failed to parse information for table %s", row["name"])
    return tables


def table_exists(client: ClickHouseClient, table: str) -> bool:
    query = """
    SELECT COUNT() == 1
    FROM system.tables
    WHERE name = {table:String}
    """
    return client.text(query, {"table": table}) == "1"
