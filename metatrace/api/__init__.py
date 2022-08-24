import os

import arel
from fastapi import Depends, FastAPI, Request
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from httpx import RequestError
from jinja2 import PackageLoader
from pych_client import ClickHouseClient
from pych_client.exceptions import ClickHouseException
from starlette.routing import Mount, WebSocketRoute

from metatrace.lib.credentials import CREDENTIALS_FILE, get_credentials
from metatrace.lib.metadata import ASNMetadata, GeolocationMetadata, IXPMetadata

hotreload = arel.HotReload(
    paths=[
        arel.Path("metatrace/static"),
        arel.Path("metatrace/templates"),
    ]
)

app = FastAPI(
    routes=[
        Mount(
            "/static",
            StaticFiles(packages=[("metatrace", "static")]),
            name="static",
        ),
        WebSocketRoute(
            "/hot-reload",
            hotreload,
            name="hot-reload",
        ),
    ],
    on_startup=[hotreload.startup],
    on_shutdown=[hotreload.shutdown],
)

templates = Jinja2Templates("", loader=PackageLoader("metatrace"))
templates.env.globals["DEBUG"] = os.getenv("DEBUG")
templates.env.globals["hotreload"] = hotreload


def get_clickhouse() -> ClickHouseClient:
    credentials = get_credentials(CREDENTIALS_FILE, None, None, None, None)
    with ClickHouseClient(*credentials) as client:
        yield client


@app.exception_handler(RequestError)
def request_error_handler(request: Request, exc: RequestError) -> Response:
    return templates.TemplateResponse(
        "errors/request.html", {"request": request, "exc": exc}, status_code=500
    )


@app.exception_handler(ClickHouseException)
def clickhouse_error_handler(request: Request, exc: ClickHouseException) -> Response:
    return templates.TemplateResponse(
        "errors/query.html", {"request": request, "exc": exc}, status_code=500
    )


@app.get("/", response_class=HTMLResponse)
def index(
    request: Request, clickhouse: ClickHouseClient = Depends(get_clickhouse)
) -> Response:
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/metadata", response_class=HTMLResponse)
def list_metadata(
    request: Request, clickhouse: ClickHouseClient = Depends(get_clickhouse)
) -> Response:
    metadata = []
    for meta in ASNMetadata.get(clickhouse):
        metadata.append({"kind": "asn", **meta})
    for meta in GeolocationMetadata.get(clickhouse):
        metadata.append({"kind": "geo", **meta})
    for meta in IXPMetadata.get(clickhouse):
        metadata.append({"kind": "ixp", **meta})
    return templates.TemplateResponse(
        "metadata.html", {"request": request, "metadata": metadata}
    )


@app.get("/metadata/asn")
def list_asn(clickhouse: ClickHouseClient = Depends(get_clickhouse)) -> list[dict]:
    return ASNMetadata.get(clickhouse)
