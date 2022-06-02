from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory

import httpx
from rich.progress import DownloadColumn, Progress, TransferSpeedColumn


def download_file(url: str, params: dict, path: Path) -> None:
    with httpx.stream("GET", url, params=params) as response:
        total = int(response.headers["Content-Length"])
        with path.open("wb") as file:
            with Progress(
                *Progress.get_default_columns(), DownloadColumn(), TransferSpeedColumn()
            ) as progress:
                task = progress.add_task(description=url, total=total)
                for chunk in response.iter_bytes():
                    file.write(chunk)
                    progress.update(task, completed=response.num_bytes_downloaded)


@contextmanager
def temporary_directory() -> Iterator[Path]:
    with TemporaryDirectory() as d:
        yield Path(d)
