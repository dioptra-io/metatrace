from fastapi import Depends, FastAPI
from pych_client import ClickHouseClient

from metatrace.lib.credentials import CREDENTIALS_FILE, get_credentials
from metatrace.lib.metadata.asn import ASNMetadata

app = FastAPI()


def get_clickhouse() -> ClickHouseClient:
    credentials = get_credentials(CREDENTIALS_FILE, None, None, None, None)
    with ClickHouseClient(*credentials) as client:
        yield client


@app.get("/metadata/asn")
def list_asn(clickhouse: ClickHouseClient = Depends(get_clickhouse)) -> list[dict]:
    return ASNMetadata.list(clickhouse)
