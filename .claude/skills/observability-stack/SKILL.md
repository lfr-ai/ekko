---
name: observability-stack
description: 'Prometheus metrics, Grafana dashboards-as-code, and OpenTelemetry instrumentation conventions for a backend service. Use when adding a metric, editing a Grafana dashboard/datasource, wiring OTel instrumentation, or reviewing an observability change.'
---

# Observability Stack Skill

Three complementary signals, each with a distinct job — do not reach for one
to solve what another already owns:

| Signal | Owns | Backing tool here |
| --- | --- | --- |
| Metrics | Aggregate counts/rates/latencies over time, alerting thresholds | Prometheus + `prometheus_client` |
| Traces | One request's causal path across processes/services | OpenTelemetry (`opentelemetry-instrumentation-*`) |
| Logs | Discrete events with full context, root-cause detail | stdlib `logging` (see `python-conventions` skill, Hard Rule 15) |

A dashboard is a *view* over metrics (Grafana), never a replacement for
tracing a single request — if you find yourself grep-ing dashboards to
explain one request's behavior, that request needed a trace or a
correlation-ID'd log line instead.

## Prometheus metrics

- **Naming**: `<namespace>_<subject>_<unit>_total` for a counter (e.g.
  `kris_http_requests_total`), `<namespace>_<subject>_<unit>` for a gauge/
  histogram (seconds, bytes — never abbreviate the unit). See the
  [Prometheus metric naming guide](https://prometheus.io/docs/practices/naming/).
- **Labels**: low-cardinality only (`status_class` = `"2xx"`, not the full
  status code; `outcome`, `intake_channel`) — a label with unbounded values
  (user ID, request ID) blows up Prometheus's memory and query cost. Put
  high-cardinality identifiers in a trace or a log line instead.
- **Multiprocess mode**: a multi-worker ASGI server (Uvicorn/Gunicorn with
  workers > 1) needs `prometheus_client.multiprocess` and a shared
  `PROMETHEUS_MULTIPROC_DIR`; each worker's `/metrics` endpoint must build its
  `CollectorRegistry` from that directory (`multiprocess.MultiProcessCollector`),
  never the process-local default registry, or scraped values undercount by a
  factor of the worker count.
- **Instrument once, module-level**: define a `Counter`/`Histogram`/`Gauge` as
  a module-level singleton and increment/observe it inline at the call site —
  never construct a new instrument per request (each construction re-registers
  with the default registry and either errors on a duplicate name or silently
  fragments the series).
- **Port/adapter boundary**: define the metrics contract as a Core port
  (`MetricsPort`) with named methods (`record_http_request`,
  `record_pipeline_outcome`), never leak `prometheus_client` types past the
  Infrastructure adapter — mirrors the `clean-architecture` skill's ports
  convention, and the `ports:check`/`check_ports_adapters.py` guard applies to
  it exactly like any other port.

## Grafana dashboards-as-code

- Dashboards and datasources are provisioned as committed JSON/YAML
  (`observability/dashboards/*.json`,
  `observability/grafana/{dashboards,datasources}/*.yaml`), never edited only
  through the Grafana UI and left uncommitted — the UI is for iterating, the
  commit is the source of truth.
- Every panel's query should read as: "which Prometheus metric, over what
  window, aggregated how" — a panel with a raw unexplained PromQL expression
  and no title/description is a maintenance trap for the next reader.
- Review a dashboard change like any other diff: does a renamed/removed
  metric still have a panel referencing the old name (a silent "No data"
  panel is worse than a query error).

## OpenTelemetry instrumentation

- Start with the framework auto-instrumentor
  (`opentelemetry-instrumentation-fastapi`/`-httpx`/`-sqlalchemy`, one line in
  the app factory) before hand-writing spans — it covers request/response,
  outbound HTTP, and DB spans for free.
- A custom span is for a unit of work auto-instrumentation can't see (a
  retrieval pipeline step, an LLM call — see the `litellm`/`rag` skills):

  ```python
  from opentelemetry import trace

  tracer = trace.get_tracer(__name__)

  with tracer.start_as_current_span("rerank_candidates") as span:
      span.set_attribute("candidate_count", len(candidates))
      ...
  ```

- **Correlation context vs. distributed tracing are not the same thing.** A
  hand-rolled `contextvars`-based request/case-ID (propagated only through a
  logging filter) gives you grep-able logs but no causal graph across
  service boundaries, no latency breakdown per span, and no automatic
  parent/child linking. If the project already has a correlation-context
  module for structured logging, treat it as the *logging* signal's ID, and
  either bridge it to the active OTel span (`trace.get_current_span()
  .set_attribute("request_id", ...)`) or plan a migration once traces need to
  cross a real process boundary (a queue, a second service) — a single
  in-process correlation ID cannot do that on its own.
- Never instrument business logic with vendor-specific span/metric calls in
  Core or Application layers — instrumentation is an Infrastructure/
  composition-layer concern (it wraps a port's adapter or the app factory),
  matching the `clean-architecture` skill's Dependency Rule.

## Local stack

Two deployment modes for the metrics/dashboards pipeline exist as Taskfile
targets (see `observability/README.md` for the concrete ports/service list):

```shell
task observability:docker   # Prometheus + Grafana via Docker Compose
task observability          # native (Windows Server) — file_sd targets rendered first
```

## References

- [Prometheus metric and label naming](https://prometheus.io/docs/practices/naming/)
- [prometheus_client multiprocess mode](https://prometheus.github.io/client_python/multiprocess/)
- [Grafana provisioning](https://grafana.com/docs/grafana/latest/administration/provisioning/)
- [OpenTelemetry Python instrumentation](https://opentelemetry.io/docs/languages/python/instrumentation/)
