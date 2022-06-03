from datetime import datetime
from random import getrandbits


def make_identifier(shortname: str, date: datetime) -> str:
    h = getrandbits(16)
    return f"{shortname}_{date:%Y%m%d%H%M}_{h:04x}"
