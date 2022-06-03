import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


class Collector(ABC):
    """
    Base class for Remote Route Controllers (RRCs).
    .. doctest::
        >>> from datetime import datetime
        >>> from metatrace.lib.sources.collectors import Collector
        >>> collector = Collector.from_fqdn("route-views2.routeviews.org")
        >>> collector.table_name(datetime(2020, 1, 1, 8))
        'rib.20200101.0800.bz2'
        >>> collector.table_url(datetime(2020, 1, 1, 8))
        'http://archive.routeviews.org/bgpdata/2020.01/RIBS/rib.20200101.0800.bz2'
    """

    extension = ""

    @property
    @abstractmethod
    def fqdn(self) -> str:
        ...

    @abstractmethod
    def closest(self, t: datetime) -> datetime:
        """
        Return the datetime closest to `t` for which there is an RIB available.
        """
        ...

    @abstractmethod
    def table_name(self, t: datetime) -> str:
        """
        Return the file name for the RIB at time `t`.
        """
        ...

    @abstractmethod
    def table_url(self, t: datetime) -> str:
        """
        Return the URL for the RIB at time `t`.
        """
        ...

    @classmethod
    def from_fqdn(cls, fqdn: str) -> Optional["Collector"]:
        if m := re.match(r"^(.+)\.(routeviews|oregon-ix|ripe)\.\w+", fqdn):
            name, service = m.groups()
            if service == "ripe":
                return RISCollector(name)
            if service in ("routeviews", "oregon-ix"):
                return RouteViewsCollector(name)
        return None


@dataclass(frozen=True)
class RISCollector(Collector):
    """
    A Remote Route Collector (RRC) from the `RIPE Routing Information Service`_ (RIS).
    .. code-block:: python
        from metatrace.lib.sources import RISCollector
        collector = RISCollector("rrc00")
    .. _RIPE Routing Information Service: https://www.ripe.net/analyse/internet-measurements/routing-information-service-ris/ris-raw-data
    """

    name: str
    extension: str = "gz"

    @property
    def base_url(self) -> str:
        return f"http://data.ris.ripe.net/{self.name}"

    @property
    def fqdn(self) -> str:
        return f"{self.name}.ripe.net"

    def closest(self, t: datetime) -> datetime:
        # 00:00, 08:00, 16:00
        return t.replace(hour=round(t.hour / 8) * 8, minute=0)

    def table_name(self, t: datetime) -> str:
        return f"bview.{t:%Y%m%d.%H%M}.{self.extension}"

    def table_url(self, t: datetime) -> str:
        return f"{self.base_url}/{t:%Y.%m}/{self.table_name(t)}"


@dataclass(frozen=True)
class RouteViewsCollector(Collector):
    """
    A Remote Route Collector (RRC) from the `University of Oregon Route Views Project`_.
    .. code-block:: python
        from metatrace.lib.sources.collectors import RISCollector
        collector = RouteViewsCollector("route-views2")
    .. _University of Oregon Route Views Project: http://archive.routeviews.org/
    """

    name: str
    extension: str = "bz2"

    @property
    def base_url(self) -> str:
        if self.name == "route-views2":
            return "http://archive.routeviews.org/bgpdata"
        return f"http://archive.routeviews.org/{self.name}/bgpdata"

    @property
    def fqdn(self) -> str:
        return f"{self.name}.routeviews.org"

    def closest(self, t: datetime) -> datetime:
        # 00:00, 02:00, 04:00, ...
        return t.replace(hour=round(t.hour / 2) * 2, minute=0)

    def table_name(self, t: datetime) -> str:
        return f"rib.{t:%Y%m%d.%H%M}.{self.extension}"

    def table_url(self, t: datetime) -> str:
        return f"{self.base_url}/{t:%Y.%m}/RIBS/{self.table_name(t)}"
