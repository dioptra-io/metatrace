import json

import arel
import httpx
from fastapi import Depends, FastAPI, Request
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pych_client import ClickHouseClient
from starlette.routing import Mount, WebSocketRoute

from metatrace.lib.credentials import CREDENTIALS_FILE, get_credentials
from metatrace.lib.metadata import ASNMetadata, GeolocationMetadata, IXPMetadata

hotreload = arel.HotReload(
    paths=[
        arel.Path("./static"),
        arel.Path("./templates"),
    ]
)

app = FastAPI(
    routes=[
        Mount("/static", StaticFiles(directory="static"), name="static"),
        WebSocketRoute("/hot-reload", hotreload, name="hot-reload"),
    ],
    on_startup=[hotreload.startup],
    on_shutdown=[hotreload.shutdown],
)

templates = Jinja2Templates(directory="templates")
templates.env.globals["DEBUG"] = True  # os.getenv("DEBUG")  # Development flag.
templates.env.globals["hotreload"] = hotreload


def get_clickhouse() -> ClickHouseClient:
    credentials = get_credentials(CREDENTIALS_FILE, None, None, None, None)
    with ClickHouseClient(*credentials) as client:
        yield client


# TODO: More specific error for pych-client specifically?
@app.exception_handler(httpx.ConnectError)
def connect_error_handler(request: Request, exc: httpx.ConnectError) -> Response:
    return templates.TemplateResponse(
        "errors/database.html",
        {
            "request": request,
            "config": json.dumps(
                {
                    "base_url": "http://localhost:8123",
                    "database": "default",
                    "username": "default",
                    "password": "***",
                },
                indent=2,
            ),
        },
        status_code=500,
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
