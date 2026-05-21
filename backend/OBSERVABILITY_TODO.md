# Observability TODO (Prometheus, Grafana, OpenTelemetry)

## 1. Metrics & Instrumentation (Backend)
- [ ] Add `prometheus-fastapi-instrumentator` to backend dependencies (pyproject.toml)
- [ ] Expose `/metrics` endpoint in FastAPI app (presentation layer)
- [ ] Add basic HTTP request metrics (latency, count, status)
- [ ] Add custom business/domain metrics (e.g., transcript analysis, agent actions)
- [ ] Document all metrics in code and docs

## 2. Distributed Tracing (OpenTelemetry)
- [ ] Add OpenTelemetry SDK and FastAPI/SQLAlchemy instrumentations to dependencies
- [ ] Configure OTel tracing for FastAPI (middleware)
- [ ] Configure OTel tracing for SQLAlchemy (DB queries)
- [ ] Export traces to OTLP/Prometheus (or Jaeger/Zipkin for local dev)
- [ ] Add trace context propagation (request_id, etc.)
- [ ] Document trace setup and context propagation

## 3. Prometheus & Grafana (Dev Environment)
- [ ] Add Prometheus service to `docker/compose.yaml` (scrape app `/metrics`)
- [ ] Add Grafana service to `docker/compose.yaml` (connect to Prometheus)
- [ ] Add persistent volumes for Prometheus and Grafana data
- [ ] Add example Prometheus config (prometheus.yml)
- [ ] Add example Grafana provisioning (dashboards, data sources)
- [ ] Expose Grafana on local port (e.g., 3000)
- [ ] Document local dev setup and ports

## 4. Dashboards & Alerts
- [ ] Create sample Grafana dashboard for FastAPI metrics
- [ ] Create dashboard for business metrics (transcripts, agent actions)
- [ ] Add example alert rule (e.g., high error rate)
- [ ] Export/import dashboard JSON for easy setup

## 5. Documentation & Validation
- [ ] Update README with observability setup instructions
- [ ] Add troubleshooting section for metrics/tracing
- [ ] Add test/validation steps for metrics and traces
- [ ] Add CI check for `/metrics` endpoint health

---

## References
- [prometheus-fastapi-instrumentator](https://github.com/trallard/prometheus-fastapi-instrumentator)
- [OpenTelemetry Python](https://opentelemetry.io/docs/instrumentation/python/)
- [Grafana Prometheus Docs](https://grafana.com/docs/grafana/latest/datasources/prometheus/)
- [Prometheus Docker Compose Example](https://github.com/prometheus/prometheus/blob/main/documentation/examples/prometheus-docker-compose.yml)
