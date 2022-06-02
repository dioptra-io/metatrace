from datetime import datetime
from random import getrandbits


def make_slug(date: datetime) -> str:
    h = getrandbits(16)
    return f"{date:%Y%m%d%H%M}_{h:04x}"


def data_table_name(slug: str) -> str:
    return f"data_{slug}"
