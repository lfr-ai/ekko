# Project Facts — <project-name>

Project-specific overlay for the portable agent configuration.

## Identity

- Project shape: `<backend-only | frontend-only | full-stack>`
- Backend package/source root: `<package>` / `<path>` or `none`
- Frontend package/source root: `<package>` / `<path>` or `none`
- Environment-variable prefix: `<PREFIX_>`
- Agent portability tokens: `<project-name>`, `<organization-or-repository-token>`

## Toolchain

- Backend package manager/task runner: `<uv + Task | none>`
- Frontend package manager: `<Bun | none>`
- Main commands: `<project-owned commands>`

## Architecture

- Layers: `<verified dependency flow>`
- Composition roots: `<backend and/or frontend assembly entry points>`
- Boundary contracts: `<API/schema/generated contract locations>`

## Specs, decisions, and code intelligence

- Specs: `<OpenSpec path or none>`
- Significant decisions: `<focused source path>`
- Code graph/index: `<tool and refresh command>`

## Data and persistence

- `<database ownership and migration location, or none>`

## CI and deployment

- CI: `<provider and owning files>`
- Deployment: `<runtime/topology source of truth>`
