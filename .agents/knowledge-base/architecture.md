# Architecture

## Backend

Dependencies point inward:

`config → core → {ai | infrastructure} → application → presentation → composition → cli`

- `core` owns domain values, policies, events, and ports.
- `ai` and `infrastructure` implement inward contracts without importing application or presentation.
- `application` orchestrates use cases.
- `presentation` maps REST/GraphQL transports and obtains dependencies through request-state protocols.
- `composition` is the only layer that wires concrete implementations.

## Frontend

Dependencies follow:

`domain → infrastructure → application → presentation → router`

`lib` is a shared leaf. The dependency-free checker at
`frontend/scripts/check-architecture.mjs` enforces the boundary map.

## Composition roots

- Backend: `ekko.composition.app_factory:create_app`
- Frontend: `frontend/src/main.tsx`
