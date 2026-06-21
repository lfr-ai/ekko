# Caddy Configuration

This directory contains the reverse-proxy configuration for Ekko.

## Structure

- `Caddyfile` — top-level entrypoint and imports
- `snippets/` — reusable route/security/transport snippets

## Design goals

- Keep config modular and composable
- Prefer secure defaults (headers, HTTPS-first posture)
- Keep app routing and transport policy separate

## Local usage

Caddy is started through the Docker compose stack under `docker/`.

## Operational notes

- Keep security headers centralized in `snippets/security.caddy`
- Keep route definitions in dedicated snippet files
- Keep `trusted_proxies` constrained to private ranges or explicit upstream CIDRs only
- Document any new public route behavior in root `README.md`
