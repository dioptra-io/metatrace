from dataclasses import dataclass

import httpx
from more_itertools import map_reduce

PEERINGDB_BASE_URL = "https://www.peeringdb.com/api/"


@dataclass(frozen=True)
class IX:
    id: int
    name: str

    @classmethod
    def from_dict(cls, d: dict) -> "IX":
        return cls(d["id"], d["name"])


@dataclass(frozen=True)
class LAN:
    id: int
    ix_id: int

    @classmethod
    def from_dict(cls, d: dict) -> "LAN":
        return cls(d["id"], d["ix_id"])


@dataclass(frozen=True)
class Prefix:
    id: int
    ixlan_id: int
    prefix: str

    @classmethod
    def from_dict(cls, d: dict) -> "Prefix":
        return cls(d["id"], d["ixlan_id"], d["prefix"])


@dataclass(frozen=True)
class Object:
    ix: IX
    prefixes: list[Prefix]


class PeeringDB:
    """
    An object-oriented interface to `PeeringDB <https://www.peeringdb.com>`_.
    .. code-block:: python
        from metatrace.lib.sources import PeeringDB
        peeringdb = PeeringDB.from_api()
        peeringdb.objects[0]
        # Object(ix=IX(id=1, name='Equinix Ashburn'), prefixes=[
        #    Prefix(id=2, ixlan_id=1, prefix='2001:504:0:2::/64'),
        #    Prefix(id=386, ixlan_id=1, prefix='206.126.236.0/22')
        # ])
        ixtree = peeringdb.radix_tree()
        ixtree.search_best("37.49.236.1").data["ix"]
        # IX(id=359, name='France-IX Paris')
    """

    def __init__(self, objects: list[Object]):
        self.objects = objects

    @classmethod
    def from_api(
        cls, base_url: str = PEERINGDB_BASE_URL, api_key: str | None = None
    ) -> "PeeringDB":
        """Load PeeringDB from the PeeringDB API."""
        headers = {}
        if api_key:
            headers = {"Authorization": f"Api-Key {api_key}"}
        with httpx.Client(base_url=base_url, headers=headers, timeout=30) as client:
            ixs = [IX.from_dict(x) for x in client.get("ix.json").json()["data"]]
            lans = [LAN.from_dict(x) for x in client.get("ixlan.json").json()["data"]]
            pfxs = [
                Prefix.from_dict(x) for x in client.get("ixpfx.json").json()["data"]
            ]

        pfxs_by_lan = map_reduce(pfxs, lambda x: x.ixlan_id)
        lans_by_ix = map_reduce(lans, lambda x: x.ix_id)

        objects = []

        for ix in ixs:
            if ix.id not in lans_by_ix:
                continue
            pfxs_ = []
            for lan in lans_by_ix[ix.id]:
                if lan.id not in pfxs_by_lan:
                    continue
                pfxs_.extend(pfxs_by_lan[lan.id])
            objects.append(Object(ix, pfxs_))

        return PeeringDB(objects)
