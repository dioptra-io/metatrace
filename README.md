# metatrace

```bash
poetry install
poetry shell
```

```bash
metatrace metadata asn add --collector route-views2.routeviews.org --date 2014-01-01T00:00:00
metatrace metadata asn list
# ┏━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━┓
# ┃ Slug              ┃ Collector                   ┃ Date                     ┃ Creation date            ┃ Rows   ┃ Size                  ┃
# ┡━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━┩
# │ 202205312208_1f59 │ route-views2.routeviews.org │ Wed Jan  1 00:00:00 2014 │ Tue May 31 22:08:18 2022 │ 498110 │ 3.5454529999999997 MB │
# └───────────────────┴─────────────────────────────┴──────────────────────────┴──────────────────────────┴────────┴───────────────────────┘
metatrace metadata asn query 202205312208_1f59 8.8.8.8
# 15169
metatrace metadata asn remove 202205312208_1f59
```

```bash
metatrace metadata ixp add --source peeringdb
metatrace metadata ixp list
# ┏━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━┳━━━━━━━━━━━┓
# ┃ Slug              ┃ Source    ┃ Creation date            ┃ Rows ┃ Size      ┃
# ┡━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━╇━━━━━━━━━━━┩
# │ 202205312134_6cf2 │ peeringdb │ Tue May 31 21:34:10 2022 │ 1952 │ 26.848 kB │
# └───────────────────┴───────────┴──────────────────────────┴──────┴───────────┘
metatrace metadata ixp query 202205312134_6cf2 2001:7f8:1::1
# AMS-IX
metatrace metadata ixp remove 202205312134_6cf2
```