# metatrace

```bash
poetry install
poetry shell
```

```bash
python -m metatrace.cli metadata ixp add --source peeringdb
python -m metatrace.cli metadata ixp list
# ┏━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━┳━━━━━━━━━━━┓
# ┃ Slug              ┃ Source    ┃ Creation date            ┃ Rows ┃ Size      ┃
# ┡━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━╇━━━━━━━━━━━┩
# │ 202205312134_6cf2 │ peeringdb │ Tue May 31 21:34:10 2022 │ 1952 │ 26.848 kB │
# └───────────────────┴───────────┴──────────────────────────┴──────┴───────────┘
python -m metatrace.cli metadata ixp query 202205312134_6cf2 2001:7f8:1::1
# AMS-IX
python -m metatrace.cli metadata ixp remove 202205312134_6cf2
```