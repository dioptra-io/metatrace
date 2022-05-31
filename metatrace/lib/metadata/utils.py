from datetime import datetime
from random import getrandbits


def make_slug(date: datetime) -> str:
    h = getrandbits(16)
    return f"{date:%Y%m%d%H%M}_{h:04x}"


def dict_name(kind: str, slug: str) -> str:
    return f"metadata_dict_{kind}_{slug}"


def table_name(kind: str, slug: str) -> str:
    return f"metadata_table_{kind}_{slug}"
