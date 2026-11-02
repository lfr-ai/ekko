# Docker assets

Local-only Docker setup. Images are never published to a registry.

## Files

| File | Purpose |
| --- | --- |
| `Containerfile` | Container build definition |
| `Containerfile.dockerignore` | Build-context exclusions (BuildKit per-Dockerfile ignore) |
| `compose.yaml` | Base services (app + optional caddy) with no host port exposure |
| `compose.override.yaml` | Local developer override (hot-reload, host port mappings) |
| `compose.analytics.yaml` | Optional analytics profile (Matomo + MariaDB) |

## Usage

```bash
# Preferred (Taskfile wrapper)
task docker:up:caddy

# Direct compose invocation
docker compose --profile caddy up --build

# Include analytics stack (Matomo + MariaDB)
docker compose -f docker/compose.yaml -f docker/compose.override.yaml -f docker/compose.analytics.yaml --profile analytics up --build

# Standalone image build
docker build -f docker/Containerfile -t ekko .
```

Caddy is enabled via `--profile caddy`.
See `../caddy/README.md` for details.

Matomo analytics is enabled via `--profile analytics` with
`compose.analytics.yaml`.

Host ports are declared in `compose.override.yaml` so the base file
stays safer for CI and non-local runtime scenarios.

## Build context

The build context is the **project root** (not `docker/`). This allows
copying `backend/src/` and `backend/pyproject.toml` into the image.
The `Containerfile.dockerignore` uses an allow-list pattern to minimize
the build context.
