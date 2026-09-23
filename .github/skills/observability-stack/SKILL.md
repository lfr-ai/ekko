---
name: observability-stack
description: 'Prometheus metrics and structured-logging conventions for the backend service. Use when adding a metric, wiring instrumentation, or reviewing an observability change.'
---

# Observability Stack Skill

Two complementary signals, each with a distinct job — do not reach for one to
solve what the other already owns:

| Signal | Owns | Backing tool here |
| --- | --- | --- |
| Metrics | Aggregate counts/rates/latencies over time | Prometheus + `prometheus_client` / `prometheus-fastapi-instrumentator` (`/metrics`) |
| Logs | Discrete events with full context, root-cause detail | stdlib `logging` (see `python-conventions` skill, Hard Rule 15) |

Grafana/OTel are an **optional** profile for many repos using this stack
(a `<PROJECT>_GRAFANA_*`-style env var group may exist) — do not add a
Grafana dashboards-as-code folder or OTel instrumentation speculatively;
check this project's specs/`PROJECT.md` first, and only add either when a
concrete need for cross-request tracing or a shared dashboard actually exists.

## Prometheus metrics

- **Naming**: `<project>_<subject>_<unit>_total` for a counter, `<project>_<subject>_<unit>`
  for a gauge/histogram (seconds, bytes — never abbreviate the unit). See the
  [Prometheus metric naming guide](https://prometheus.io/docs/practices/naming/).
- **Labels**: low-cardinality only (`status_class` = `"2xx"`, not the full
  status code) — a label with unbounded values (user ID, request ID) blows up
  Prometheus's memory and query cost. Put high-cardinality identifiers in a
  log line instead.
- **Instrument once, module-level**: define a `Counter`/`Histogram`/`Gauge`
  as a module-level singleton (see `infrastructure/metrics.py`) and
  increment/observe it inline at the call site — never construct a new
  instrument per request (each construction re-registers with the default
  registry and either errors on a duplicate name or silently fragments the
  series).
- **Port/adapter boundary**: keep `prometheus_client` imports inside
  `infrastructure/metrics.py` and the app-factory wiring; never let a
  `prometheus_client` type cross into core or application — mirrors the
  `clean-architecture` skill's ports convention.

## References

- [Prometheus metric and label naming](https://prometheus.io/docs/practices/naming/)
- [prometheus_client multiprocess mode](https://prometheus.github.io/client_python/multiprocess/) — only relevant if the app ever runs with multiple Uvicorn/Gunicorn workers.
