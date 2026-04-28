#!/usr/bin/env bash
set -euo pipefail

echo "Starting postgres for local development using docker compose..."
docker compose -f docker/compose.dev.yml -f docker/compose.postgres.yml up -d
echo "Postgres started. Set DATABASE_URL or POSTGRES_* env vars to connect."
