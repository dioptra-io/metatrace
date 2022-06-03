from zipfile import ZipFile

import pandas as pd
from pych_client import ClickHouseClient

from metatrace.lib.clickhouse import insert_into
from metatrace.lib.logger import logger
from metatrace.lib.metadata import Metadata
from metatrace.lib.utilities import download_file, temporary_directory


class GeolocationMetadata(Metadata):
    attributes = {
        "country": "String",
        "city": "String",
        "latitude": "Float64",
        "longitude": "Float64",
    }
    shortname = "geo"

    @classmethod
    def insert(
        cls, client: ClickHouseClient, identifier: str, license_key: str
    ) -> None:
        with temporary_directory() as path:
            url = "https://download.maxmind.com/app/geoip_download"
            params = {
                "edition_id": "GeoLite2-City-CSV",
                "license_key": license_key,
                "suffix": "zip",
            }
            zippath = path / "db.zip"
            download_file(url, params, zippath)
            with ZipFile(zippath) as f:
                f.extractall(path)
            blocks_file_ipv4 = next(path.glob("**/GeoLite2-City-Blocks-IPv4.csv"))
            blocks_file_ipv6 = next(path.glob("**/GeoLite2-City-Blocks-IPv6.csv"))
            locations_file = next(path.glob("**/GeoLite2-City-Locations-en.csv"))
            blocks_cols = ["network", "geoname_id", "latitude", "longitude"]
            logger.info(
                "Load blocks ipv4_file=%s ipv6_file=%s",
                blocks_file_ipv4,
                blocks_file_ipv6,
            )
            blocks = pd.concat(
                [
                    pd.read_csv(blocks_file_ipv4, usecols=blocks_cols),
                    pd.read_csv(blocks_file_ipv6, usecols=blocks_cols),
                ]
            )
            logger.info("Load locations file=%s", locations_file)
            locations = pd.read_csv(
                locations_file,
                index_col="geoname_id",
                usecols=["geoname_id", "country_name", "city_name"],
            )
            logger.info("Merge blocks and locations")
            rows = (
                blocks.join(locations)
                .drop("geoname_id", axis=1)
                .rename(
                    {
                        "network": "prefix",
                        "country_name": "country",
                        "city_name": "city",
                    },
                    axis=1,
                )
                .fillna("")
                .sort_values("prefix")
                .to_dict("records")
            )
        insert_into(client, cls.table_name(identifier), rows)
