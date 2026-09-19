---
paths:
  - "**/Dockerfile"
  - "**/Dockerfile.*"
  - "**/*.dockerfile"
  - "**/Containerfile"
  - "**/Containerfile.*"
  - "**/compose*.yaml"
  - "**/compose*.yml"
  - "**/docker-compose*.yaml"
  - "**/docker-compose*.yml"
---

# Container image and Compose conventions

Build small, reproducible, non-root images. The `infrastructure-validation`
skill owns the full validation workflow; the rules below always apply when
editing a Containerfile/Dockerfile or a Compose file under `docker/`.

## Image

- Pin base images to a trusted specific tag or digest — never `latest` — and pin
  the packages you install so a rebuild is reproducible.
- Use multi-stage builds: install/compile in a builder stage, copy only the
  runtime artifacts into a slim final stage. Prefer `COPY` over `ADD`.
- Run as an explicit non-root user; drop privileges before the entrypoint.
- Order layers cheap-to-expensive (dependencies before source) so the cache
  survives source edits, and combine related `RUN` steps to keep layers few.
- Keep a `.dockerignore` so the build context excludes secrets, `.git`,
  caches, and local env files.
- Declare a `HEALTHCHECK` (or a Compose healthcheck) and an explicit `EXPOSE`.

## Secrets

- Never bake a secret into an image layer, an `ENV`, or a build `ARG` — a value
  in any layer is recoverable. Use a build secret, a runtime env var, or a
  mounted secret instead.

## Compose

- One concern per service; express dependencies with `depends_on` plus
  healthchecks, not sleeps. Keep environment-specific values in `.env`/override
  files, never committed inline.
- Use named volumes and explicit networks, pin every service image tag, and do
  not publish a port wider than the environment needs.

## Before finishing

- Render the merged Compose configuration (`docker compose config`) and
  confirm profiles/env inputs resolve as expected before relying on it.
