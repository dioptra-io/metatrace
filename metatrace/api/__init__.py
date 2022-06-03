import arel
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


@app.get("/", response_class=HTMLResponse)
async def index(
    request: Request, clickhouse: ClickHouseClient = Depends(get_clickhouse)
) -> Response:
    asns = ASNMetadata.get(clickhouse)
    geos = GeolocationMetadata.get(clickhouse)
    ixps = IXPMetadata.get(clickhouse)
    return templates.TemplateResponse(
        "index.html", {"request": request, "asns": asns, "geos": geos, "ixps": ixps}
    )


@app.get("/metadata/asn")
def list_asn(clickhouse: ClickHouseClient = Depends(get_clickhouse)) -> list[dict]:
    return ASNMetadata.get(clickhouse)
