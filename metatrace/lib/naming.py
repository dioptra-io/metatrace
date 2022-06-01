from datetime import datetime
from random import getrandbits


def make_slug(date: datetime) -> str:
    h = getrandbits(16)
    return f"{date:%Y%m%d%H%M}_{h:04x}"


def data_table_name(slug: str) -> str:
    return f"data_{slug}"


def metadata_dict_name(kind: str, slug: str) -> str:
    return f"metadata_dict_{kind}_{slug}"


def metadata_table_name(kind: str, slug: str) -> str:
    return f"metadata_table_{kind}_{slug}"
