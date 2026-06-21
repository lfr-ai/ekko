# Docker assets

Local-only Docker setup. Images are never published to a registry.

## Files

| File | Purpose |
| --- | --- |
| `Containerfile` | Container build definition |
| `Containerfile.dockerignore` | Build-context exclusions (BuildKit per-Dockerfile ignore) |
| `.dockerignore` | Legacy Docker ignore (fallback for non-BuildKit) |
| `compose.yaml` | Base services (app + optional caddy + optional observability) with no host port exposure |
| `compose.override.yaml` | Local developer override (hot-reload, host port mappings) |
| `prometheus.yml` | Prometheus scrape config for observability |

## Usage

```bash
# Preferred (Taskfile wrapper)
task docker:up:caddy

# Direct compose invocation
docker compose --profile caddy up --build

# Include observability stack (Prometheus + Grafana)
docker compose --profile caddy --profile observability up --build

# Standalone image build
docker build -f docker/Containerfile -t ekko .
```

Caddy is enabled via `--profile caddy`.
See `../caddy/README.md` for details.

Prometheus and Grafana are enabled via `--profile observability`.

Host ports are intentionally declared in `compose.override.yaml` so the base file
stays safer for CI and non-local runtime scenarios.

## Build context

The build context is the **project root** (not `docker/`). This allows
copying `backend/src/` and `backend/pyproject.toml` into the image.
The `Containerfile.dockerignore` uses an allow-list pattern to minimize
the build context.
