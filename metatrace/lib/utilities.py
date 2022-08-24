from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory

import httpx
from babel.dates import format_timedelta
from pint import UnitRegistry
from rich.console import Console
from rich.progress import DownloadColumn, Progress, TransferSpeedColumn
from rich.table import Table

from metatrace.lib.logger import logger


def download_file(url: str, params: dict, path: Path) -> None:
    with httpx.stream("GET", url, params=params) as response:
        response.raise_for_status()
        total = int(response.headers["Content-Length"])
        with path.open("wb") as file:
            with Progress(
                *Progress.get_default_columns(), DownloadColumn(), TransferSpeedColumn()
            ) as progress:
                task = progress.add_task(description=url, total=total)
                for chunk in response.iter_bytes():
                    file.write(chunk)
                    progress.update(task, completed=response.num_bytes_downloaded)


def print_tables(
    console: Console, units: UnitRegistry, tables: list[dict], quiet: bool
) -> None:
    if quiet:
        for t in tables:
            try:
                console.print(t["info"]["identifier"])
            except KeyError:
                logger.exception("Failed to print table %s", t["name"])
        return
    table = Table(box=None, header_style="", pad_edge=False)
    # TODO: Additional columns based on info dict
    # TODO: Directly use table name instead of identifier?
    # Identifier -> Name
    # TODO: Get created_at from clickhouse (metadata_modification_time)?
    # TODO: kube-style CLI: metatrace get --type ... / metatrace delete ... / metatrace resources
    table.add_column("IDENTIFIER")
    table.add_column("CREATED")
    table.add_column("ROWS")
    table.add_column("SIZE")
    for t in tables:
        try:
            created_at = (
                datetime.fromisoformat(t["info"]["created_at"]) - datetime.now()
            )
            total_bytes = t["total_bytes"] * units.byte
            table.add_row(
                t["info"]["identifier"],
                format_timedelta(created_at, add_direction=True),
                str(t["total_rows"]),
                f"{total_bytes:.2fP#~}",
            )
        except (KeyError, ValueError):
            logger.exception("Failed to print table %s", t["name"])
    console.print(table)


@contextmanager
def temporary_directory() -> Iterator[Path]:
    with TemporaryDirectory() as d:
        yield Path(d)
