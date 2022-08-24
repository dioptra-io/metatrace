# ⚡ MetaTrace

<!-- Uncomment when public
[![Tests](https://img.shields.io/github/workflow/status/dioptra-io/metatrace/Tests?logo=github)](https://github.com/dioptra-io/metatrace/actions/workflows/tests.yml)
[![Coverage](https://img.shields.io/codecov/c/github/dioptra-io/metatrace?logo=codecov&logoColor=white)](https://app.codecov.io/gh/dioptra-io/metatrace)
[![PyPI](https://img.shields.io/pypi/v/metatrace?color=blue&logo=pypi&logoColor=white)](https://pypi.org/project/metatrace/)
-->

[![Tests](https://github.com/dioptra-io/metatrace/actions/workflows/tests.yml/badge.svg)](https://github.com/dioptra-io/metatrace/actions/workflows/tests.yml)

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

### Web

```bash
metatrace server
```

http://localhost:5555

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

TODO: Dataset Kevin?

## Authors

MetaTrace is developed and maintained by the [Dioptra group](https://dioptra.io) at [Sorbonne Université](https://www.sorbonne-universite.fr) in Paris, France.

---
TODO:
- Add local radix-tree loaded from CH (.radix_tree() method on Metadata)
- Refactor metadata as a single type with (identifier, kind, source, date, creation_date, ...) => metadata tab on website
- show error page when clickhouse cannot be reached which explains how to configure metatrace
- Add AS classification meta
- Add quoted TTL field
- Document configuration
- Update queries (look on CH query log)
---

```bash
poetry install
poetry shell
```

```bash
metatrace metadata asn add --collector route-views2.routeviews.org --date 2014-01-01T00:00:00
metatrace metadata asn get
# ┏━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━┓
# ┃ Identifier              ┃ Collector                   ┃ Date                     ┃ Creation date            ┃ Rows   ┃ Size                  ┃
# ┡━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━┩
# │ 202205312208_1f59 │ route-views2.routeviews.org │ Wed Jan  1 00:00:00 2014 │ Tue May 31 22:08:18 2022 │ 498110 │ 3.5454529999999997 MB │
# └───────────────────┴─────────────────────────────┴──────────────────────────┴──────────────────────────┴────────┴───────────────────────┘
metatrace metadata asn query 202205312208_1f59 8.8.8.8
# 15169
metatrace metadata asn delete 202205312208_1f59
```

```bash
metatrace metadata ixp add --source peeringdb
metatrace metadata ixp get
# ┏━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━┳━━━━━━━━━━━┓
# ┃ Identifier              ┃ Source    ┃ Creation date            ┃ Rows ┃ Size      ┃
# ┡━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━╇━━━━━━━━━━━┩
# │ 202205312134_6cf2 │ peeringdb │ Tue May 31 21:34:10 2022 │ 1952 │ 26.848 kB │
# └───────────────────┴───────────┴──────────────────────────┴──────┴───────────┘
metatrace metadata ixp query 202205312134_6cf2 2001:7f8:1::1
# AMS-IX
metatrace metadata ixp delete 202205312134_6cf2
```

```bash
metatrace data create --asn-metadata-identifier 202205312208_1f59 --ixp-metadata-identifier 202205312134_6cf2
metatrace data get
# ┏━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━┳━━━━━━┓
# ┃ Identifier              ┃ Source ┃ Creation date            ┃ Rows ┃ Size ┃
# ┡━━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━╇━━━━━━┩
# │ 202206011116_a93b │ ark    │ Wed Jun  1 11:16:24 2022 │ 0    │ 0 B  │
# └───────────────────┴────────┴──────────────────────────┴──────┴──────┘
```

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
