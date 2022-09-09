# ⚡ MetaTrace

<!-- Uncomment when public
[![Tests](https://img.shields.io/github/workflow/status/dioptra-io/metatrace/Tests?logo=github)](https://github.com/dioptra-io/metatrace/actions/workflows/tests.yml)
[![Coverage](https://img.shields.io/codecov/c/github/dioptra-io/metatrace?logo=codecov&logoColor=white)](https://app.codecov.io/gh/dioptra-io/metatrace)
[![PyPI](https://img.shields.io/pypi/v/metatrace?color=blue&logo=pypi&logoColor=white)](https://pypi.org/project/metatrace/)
-->

[![Tests](https://github.com/dioptra-io/metatrace/actions/workflows/tests.yml/badge.svg)](https://github.com/dioptra-io/metatrace/actions/workflows/tests.yml)

## Research

- **Evaluation:** https://github.com/dioptra-io/metatrace-evaluation
- **Paper repository:** https://github.com/kvermeul/metatrace-paper
- **Paper document:** https://docs.google.com/document/d/1aPFUckHBUkWSdT3y_Jm0r8ItGpCv885Hj797gOP87sM/edit
- **Working document:** https://docs.google.com/document/d/1lPjq4h68D31f7zESqBtkAj1uVhm4FbLYwOvuxltGH50/edit
- **To release the project:**
  - [ ] Create a PyPI token and add it to the `PYPI_PASSWORD` repository secret
  - [ ] Uncomment the `docker` and `pypi` jobs in the [`tests.yml`](.github/workflows/tests.yml) workflow
  - [ ] Uncomment the badges at the top of [`README.md`](README.md)

## Quickstart

### Docker

```bash
# NOTE: The image is currently not published.
docker run ghcr.io/dioptra-io/metatrace --help
```

### Python

```bash
# NOTE: The package is currently not published.
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

## Queries

(We're always assuming single-path traceroutes here)

### Traceroutes going through an ASN

```sql
SELECT DISTINCT
    agent_id,
    probe_dst_addr,
    traceroute_start
FROM data_202206021549_11e3
WHERE reply_asn = 15169
```

### Traceroutes going through an IXP

```sql
SELECT DISTINCT
    agent_id,
    probe_dst_addr,
    traceroute_start
FROM data_202206021549_11e3
WHERE reply_ixp = 'AMS-IX'
```

### Traceroutes going through a country

(TODO: Insert maxmind)

### Traceroutes going through multiple ASNs (or IXPs, countries...)

```sql
WITH groupUniqArray(reply_asn) AS asns
SELECT
    agent_id,
    probe_dst_addr,
    traceroute_start
FROM data_202206021549_11e3
GROUP BY
    agent_id,
    probe_dst_addr,
    traceroute_start
HAVING hasAll(asns, [3356, 15169])
SETTINGS optimize_aggregation_in_order = 1
```

### AS-PATH

```sql
WITH
    groupArray((traceroute_start, probe_ttl, reply_asn)) AS replies,
    -- Build a map (traceroute_start, probe_ttl) -> reply_asn 
    arrayMap(x -> cityHash64(x.1, x.2), replies) AS keys,
    arrayMap(x -> x.3, replies) AS values,
    CAST((keys, values), 'Map(UInt64, UInt32)') AS map,
    -- Find the distinct traceroute_start values
    arrayDistinct(arrayMap(x -> x.1, replies)) AS starts,
    -- Find the distinct probe_ttl values
    arrayDistinct(arrayMap(x -> x.2, replies)) AS ttls,
    -- Find the min/max probe_ttl values in order to produce sorted results
    arrayMin(ttls) AS min_ttl,
    arrayMax(ttls) AS max_ttl,
    -- Build the paths
    arrayMap(start -> (start, arrayMap(ttl -> (ttl, map[cityHash64(start, ttl)]), range(min_ttl, max_ttl))), starts) AS paths,
    -- Optional, to get one line per path
    arrayJoin(paths) AS path
SELECT
    agent_id,
    probe_dst_addr,
    path.1 AS timestamp,
    path.2 AS as_path
FROM data_202206021549_11e3
GROUP BY agent_id, probe_dst_addr
SETTINGS optimize_aggregation_in_order = 1
```
