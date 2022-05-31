import json

from pych_client import ClickHouseClient


def make_schema(columns: list[tuple[str, str]]) -> str:
    """
    >>> make_schema([("a", "UInt8"), ("b", "String")])
    'a UInt8, b String'
    """
    return ", ".join(f"{x} {y}" for x, y in columns)


# As of v22.6.1 ClickHouse does not support parameter interpolation
# for all the parameters of the CREATE statement; so we perform it in Python.
def create_dict(
    client: ClickHouseClient,
    name: str,
    columns: list[tuple[str, str]],
    primary_key: str,
    query: str,
    attributes: dict | None = None,
) -> None:
    comment = json.dumps(attributes or {})
    query = f"""
    CREATE DICTIONARY {name} ({make_schema(columns)})
    PRIMARY KEY {primary_key}
    SOURCE(CLICKHOUSE(query '{query}'))
    LIFETIME(0)
    LAYOUT(IP_TRIE)
    COMMENT '{comment}'
    """
    client.execute(query)


def create_table(
    client: ClickHouseClient,
    name: str,
    columns: list[tuple[str, str]],
    order_by: list[str] | str,
    attributes: dict | None = None,
):
    if isinstance(order_by, str):
        order_by = [order_by]
    comment = json.dumps(attributes or {})
    query = f"""
    CREATE TABLE {name} ({make_schema(columns)})
    ENGINE = MergeTree
    ORDER BY ({', '.join(order_by)})
    COMMENT '{comment}'
    """
    client.execute(query)


def drop_dict(client: ClickHouseClient, name: str):
    client.execute("DROP DICTIONARY {name:Identifier}", {"name": name})


def drop_table(client: ClickHouseClient, name: str):
    client.execute("DROP TABLE {name:Identifier}", {"name": name})


def insert_into(client: ClickHouseClient, name: str, rows: list[dict]):
    data = (json.dumps(row).encode() for row in rows)
    client.execute(
        "INSERT INTO {name:Identifier} FORMAT JSONEachRow",
        params={"name": name},
        data=data,
    )


def list_tables(client: ClickHouseClient, prefix: str):
    query = """
    SELECT
        name,
        comment AS attributes,
        total_bytes,
        total_rows
    FROM system.tables
    WHERE startsWith(name, {prefix:String})
    """
    rows = client.json(query, {"prefix": prefix})
    for row in rows:
        row["attributes"] = json.loads(row["attributes"])
    return rows


def table_exists(client: ClickHouseClient, table: str):
    query = """
    SELECT COUNT() == 1
    FROM system.tables
    WHERE name = {table:String}
    """
    return client.text(query, {"table": table}) == "1"
