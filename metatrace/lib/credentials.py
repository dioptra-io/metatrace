import json
import os
from pathlib import Path
from typing import Optional, Tuple

from metatrace.lib.logger import logger

CREDENTIALS_FILE = Path.home() / ".config" / "metatrace" / "credentials.json"

BASE_URL_ENV = "METATRACE_BASE_URL"
DATABASE_ENV = "METATRACE_DATABASE"
USERNAME_ENV = "METATRACE_USERNAME"
PASSWORD_ENV = "METATRACE_PASSWORD"

DEFAULT_BASE_URL = "http://localhost:8123"
DEFAULT_DATABASE = "default"
DEFAULT_USERNAME = "default"
DEFAULT_PASSWORD = ""


def get_credentials(
    credentials_file: Path,
    base_url: Optional[str],
    database: Optional[str],
    username: Optional[str],
    password: Optional[str],
) -> Tuple[str, str, str, str]:
    if base_url or database or username or password:
        logger.debug("using credentials from arguments")
        return (
            base_url or DEFAULT_BASE_URL,
            database or DEFAULT_DATABASE,
            username or DEFAULT_USERNAME,
            password or DEFAULT_PASSWORD,
        )
    if (
        BASE_URL_ENV in os.environ
        or DATABASE_ENV in os.environ
        or USERNAME_ENV in os.environ
        or PASSWORD_ENV in os.environ
    ):
        logger.debug("using credentials from environment")
        return (
            os.environ.get(BASE_URL_ENV, DEFAULT_BASE_URL),
            os.environ.get(DATABASE_ENV, DEFAULT_DATABASE),
            os.environ.get(USERNAME_ENV, DEFAULT_USERNAME),
            os.environ.get(PASSWORD_ENV, DEFAULT_PASSWORD),
        )
    if credentials_file.exists():
        logger.debug("using credentials from %s", CREDENTIALS_FILE)
        credentials = json.loads(CREDENTIALS_FILE.read_text())
        return (
            credentials.get("base_url", DEFAULT_BASE_URL),
            credentials.get("database", DEFAULT_DATABASE),
            credentials.get("username", DEFAULT_USERNAME),
            credentials.get("password", DEFAULT_PASSWORD),
        )
    return DEFAULT_BASE_URL, DEFAULT_DATABASE, DEFAULT_USERNAME, DEFAULT_PASSWORD
