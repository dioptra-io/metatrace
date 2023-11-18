# ⚡ MetaTrace

[![Tests](https://github.com/dioptra-io/metatrace/actions/workflows/tests.yml/badge.svg)](https://github.com/dioptra-io/metatrace/actions/workflows/tests.yml)
[![PyPI](https://img.shields.io/pypi/v/metatrace?color=blue&logo=pypi&logoColor=white)](https://pypi.org/project/metatrace/)


## Quickstart

### Docker

```bash
docker run ghcr.io/dioptra-io/metatrace --help
```

### Python

```bash
pip install metatrace
metatrace --help
```

### Repository

```bash
git clone git@github.com:dioptra-io/metatrace.git
cd metatrace
poetry install
poetry run metatrace --help
```

## Usage

### CLI

#### Data

```bash
metatrace data create|delete|get|insert|query
```

#### Metadata

```
metatrace METADATA create|delete|get|query
```

For example:
```bash
metatrace asn add --collector route-views2.routeviews.org --date 2014-01-01T00:00:00
metatrace asn get
# ┏━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━┓
# ┃ Identifier        ┃ Collector                   ┃ Date                     ┃ Creation date            ┃ Rows   ┃ Size                  ┃
# ┡━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━┩
# │ 202205312208_1f59 │ route-views2.routeviews.org │ Wed Jan  1 00:00:00 2014 │ Tue May 31 22:08:18 2022 │ 498110 │ 3.5454529999999997 MB │
# └───────────────────┴─────────────────────────────┴──────────────────────────┴──────────────────────────┴────────┴───────────────────────┘
metatrace asn query 202205312208_1f59 8.8.8.8
# 15169
metatrace asn delete 202205312208_1f59
```

### Web

```bash
metatrace server
```

http://localhost:5555

### Python

`metatrace.lib`

## Data

Public [CAIDA Ark](https://www.caida.org/projects/ark/) data is supported.

## Metadata

### Autonomous system number

This metadata maps an IP address to its originating AS number, as seen by a BGP collector.
[RouteViews](http://routeviews.org) and [RIPE RIS](https://www.ripe.net/analyse/internet-measurements/routing-information-service-ris) are supported.

### Geolocation

This metadata maps an IP address to its country, city, latitude and longitude.
[MaxMind GeoLite2 City](https://dev.maxmind.com/geoip/geolite2-free-geolocation-data?lang=en) is supported.

### Internet Exchange Point

This metadata maps an IP address to its IXP if it belongs to its peering LAN.
[PeeringDB](https://www.peeringdb.com) is supported.

## Authors

MetaTrace is developed and maintained by the [Dioptra group](https://dioptra.io) at [Sorbonne Université](https://www.sorbonne-universite.fr) in Paris, France.
