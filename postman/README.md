# Postman API Testing — Ekko

API collection for testing the Ekko backend (REST + GraphQL).

## Structure

```
postman/
├── ekko-api.postman_collection.json    # Main collection
├── newman.config.json                   # Newman CLI config
├── environments/
│   ├── local.postman_environment.json       # Development (default)
│   └── production.postman_environment.json  # Desktop EXE (stricter timeout)
└── reports/                            # Generated reports (gitignored)
```

## Quick Start

1. Import `ekko-api.postman_collection.json` into Postman
2. Import `environments/local.postman_environment.json`
3. Select the environment and run requests

### Run with Newman

```bash
npm install -g newman

cd postman

# Using config file (recommended — applies all settings):
newman run --config newman.config.json

# Or with explicit flags:
newman run ekko-api.postman_collection.json \
  -e environments/local.postman_environment.json \
  --timeout-request 10000
```

## Collection Folders

| Folder | Description |
|--------|-------------|
| **Health** | REST + GraphQL health and readiness checks |
| **Stream Control** | Audio stream start/pause (REST + GraphQL) |
| **Conversations** | Conversation lifecycle (start, message, end, list) |
| **PII Anonymization** | PII detection and text anonymization |
| **GraphQL Introspection** | Schema discovery queries |
| **OpenAPI & Documentation** | OpenAPI spec, Swagger UI, ReDoc |
| **Error Handling** | Negative tests (404, 405, invalid queries, CORS) |
| **Workflows** | End-to-end chained sequences |

## Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/health` | REST health check |
| POST | `/start_stream` | Start audio capture |
| POST | `/pause_stream` | Pause audio capture |
| POST | `/graphql/graphql` | GraphQL endpoint |
| GET | `/openapi.json` | OpenAPI specification |
| GET | `/docs` | Swagger UI |
| GET | `/redoc` | ReDoc |

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `baseUrl` | Backend server URL | `http://localhost:8000` |
| `graphqlUrl` | GraphQL endpoint | `http://localhost:8000/graphql/graphql` |
| `wsUrl` | WebSocket (subscriptions) | `ws://localhost:8000/graphql/graphql` |
| `requestTimeoutMs` | SLA threshold for response time assertions | `5000` |

## Authentication

None required. The app auto-authenticates as `dev-user` (local-only desktop app).

## Collection-level Scripts

**Pre-request**: Adds `X-Request-ID` header and logs request timing.

**Test**: Validates response time < `requestTimeoutMs` (env variable), Content-Type header present, no traceback leakage.
