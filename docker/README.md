# Docker assets

Local-only Docker setup. Images are never published to a registry.

## Files

| File | Purpose |
| --- | --- |
| `Containerfile` | Container build definition |
| `Containerfile.dockerignore` | Build-context exclusions (BuildKit per-Dockerfile ignore) |
| `compose.yaml` | Base services (app + optional caddy) with no host port exposure |
| `compose.override.yaml` | Local developer override (hot-reload, host port mappings) |
| `compose.observability.yaml` | Optional observability profile (OTel Collector + Prometheus + Grafana) |
| `compose.analytics.yaml` | Optional analytics profile (Matomo + MariaDB) |
| `observability/` | Prometheus config, OTel config, Grafana provisioning + dashboards |

## Usage

```bash
# Preferred (Taskfile wrapper)
task docker:up:caddy
task docker:up:observability
task docker:up:caddy:observability

# Direct compose invocation
docker compose --profile caddy up --build

# Include observability stack (OTel Collector + Prometheus + Grafana)
docker compose -f docker/compose.yaml -f docker/compose.override.yaml -f docker/compose.observability.yaml --profile observability up --build

# Include both Caddy and observability
docker compose -f docker/compose.yaml -f docker/compose.override.yaml -f docker/compose.observability.yaml --profile caddy --profile observability up --build

# Include analytics stack (Matomo + MariaDB)
docker compose -f docker/compose.yaml -f docker/compose.override.yaml -f docker/compose.analytics.yaml --profile analytics up --build

# Standalone image build
docker build -f docker/Containerfile -t ekko .
```

Caddy is enabled via `--profile caddy`.
See `../caddy/README.md` for details.

Prometheus, Grafana, and OTel Collector are enabled via `--profile observability`
with the `compose.observability.yaml` file.

Matomo analytics is enabled via `--profile analytics` with
`compose.analytics.yaml`.

Grafana credentials are configured through:

- `GRAFANA_ADMIN_USER`
- `GRAFANA_ADMIN_PASSWORD`

in `.env.local` (do not commit real values).

Host ports are intentionally declared in `compose.override.yaml` so the base file
stays safer for CI and non-local runtime scenarios.

## Build context

The build context is the **project root** (not `docker/`). This allows
copying `backend/src/` and `backend/pyproject.toml` into the image.
The `Containerfile.dockerignore` uses an allow-list pattern to minimize
the build context.
