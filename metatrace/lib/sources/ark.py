import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional

import httpx
from bs4 import BeautifulSoup
from datetimerange import DateTimeRange


@dataclass(frozen=True)
class ArkPrefixProbingFile:
    """
    >>> ArkPrefixProbingFile.from_filename("ams-nl.20151211.1449794700.warts.gz").filename
    'ams-nl.20151211.1449794700.warts.gz'
    """

    monitor: str
    date: datetime
    md5: str | None

    @property
    def filename(self) -> str:
        timestamp = int(self.date.timestamp())
        return f"{self.monitor}.{self.date:%Y%m%d}.{timestamp}.warts.gz"

    @classmethod
    def from_filename(
        cls, name: str, md5: str | None = None
    ) -> Optional["ArkPrefixProbingFile"]:
        if m := re.match(r"([\w-]+)\.\d+\.(\d+)\.warts\.gz", name):
            monitor, timestamp = m.groups()
            return cls(
                monitor=monitor,
                date=datetime.fromtimestamp(int(timestamp), tz=timezone.utc),
                md5=md5,
            )
        return None


@dataclass(frozen=True)
class ArkTeamProbingFile:
    """
    >>> ArkTeamProbingFile.from_filename("daily.l7.t1.c000027.20070913.amw-us.warts.gz")
    ArkTeamProbingFile(monitor='amw-us', cycle=27, date=datetime.datetime(2007, 9, 13, 0, 0, tzinfo=datetime.timezone.utc), md5=None, url=None)
    >>> ArkTeamProbingFile.from_filename("aal-dk.team-probing.c007146.20190103.warts.gz")
    ArkTeamProbingFile(monitor='aal-dk', cycle=7146, date=datetime.datetime(2019, 1, 3, 0, 0, tzinfo=datetime.timezone.utc), md5=None, url=None)
    """

    monitor: str
    cycle: int
    date: datetime
    md5: str | None
    url: str | None

    @classmethod
    def from_filename(
        cls, name: str, md5: str | None = None, url: str | None = None
    ) -> Optional["ArkTeamProbingFile"]:
        if m := re.match(r"([\w-]+)\.team-probing\.c(\d+)\.(\d+)\.warts\.gz", name):
            monitor, cycle, date = m.groups()
        elif m := re.match(r".+\.c(\d+)\.(\d+)\.([\w-]+)\.warts\.gz", name):
            cycle, date, monitor = m.groups()
        else:
            return None
        return cls(
            monitor=monitor,
            cycle=int(cycle),
            date=datetime.strptime(date, "%Y%m%d").replace(tzinfo=timezone.utc),
            md5=md5,
            url=url,
        )


def ark_probe_data_list(
    team: int, start: datetime, stop: datetime
) -> list[ArkTeamProbingFile]:
    """
    >>> len(ark_probe_data_list(1, datetime(2020, 1, 1), datetime(2020, 1, 2)))
    895
    """
    files = []
    base_url = f"https://publicdata.caida.org/datasets/topology/ark/ipv4/probe-data/team-{team}/"
    time_range = DateTimeRange(start, stop).range(timedelta(days=1))
    with httpx.Client(base_url=base_url) as client:
        for date in time_range:
            path = f"{date:%Y}/cycle-{date:%Y%m%d}/"
            # md5s = ark_get_md5(client, path)
            for link in ark_get_links(client, path):
                if file := ArkTeamProbingFile.from_filename(
                    link, None, base_url + path + link
                ):
                    files.append(file)
    return files


def ark_get_links(client: httpx.Client, path: str) -> list[str]:
    soup = BeautifulSoup(client.get(path).content, "html.parser")
    return [link.text for link in soup.find_all("a")]


def ark_get_md5(client: httpx.Client, path: str) -> dict[str, str]:
    hs = {}
    for line in client.get(f"{path}/md5.md5").text.splitlines():
        name, h = line.split(" ")
        hs[name] = h
    return hs
