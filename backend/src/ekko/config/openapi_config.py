"""
OpenAPI specification generation configuration for Ekko.

This module provides configuration for generating OpenAPI/Swagger documentation
from the FastAPI application with enhanced metadata and examples.
"""

from typing import Final

# OpenAPI metadata
OPENAPI_TITLE: Final[str] = "Ekko API"
OPENAPI_VERSION: Final[str] = "0.1.0"
OPENAPI_DESCRIPTION: Final[str] = """
# Ekko — AI-Powered Voice Assistant Platform

Ekko is a modern, full-stack AI voice assistant platform built with Clean Architecture principles.

## Features

- 🎤 **Real-time Voice Streaming**: Low-latency audio capture and processing
- 🤖 **AI-Powered Conversations**: LLM integration with CrewAI multi-agent system
- 🔒 **PII Anonymization**: Regex-based sensitive data scrubbing
- 📊 **GraphQL + REST**: Flexible API layer with subscriptions support
- 🧪 **Comprehensive Testing**: Unit, integration, property-based, and E2E tests

## Architecture

This API follows Clean Architecture with strict layer boundaries:

```
Presentation → Application → Core ← Infrastructure
```

- **Core**: Domain entities, value objects, business rules
- **Application**: Use case orchestration, DTOs, mappers
- **Infrastructure**: Database, external integrations, adapters
- **Presentation**: REST routes, GraphQL schema, WebSocket handlers

## Authentication

This is a local-only desktop application. All requests are auto-authenticated as `dev-user`.

## Rate Limiting

Rate limits are applied per endpoint:
- Health endpoints: 100 requests/minute
- Stream endpoints: 20 requests/minute
- GraphQL: 60 requests/minute

## WebSocket Connections

Real-time features use WebSocket connections:
- Audio streaming: `/api/v1/stream/audio`
- GraphQL subscriptions: `/graphql` (WebSocket upgrade)

## Error Responses

All errors follow a consistent structure:

```json
{
  "detail": "Human-readable error message",
  "error_code": "SPECIFIC_ERROR_CODE",
  "timestamp": "2026-05-02T10:52:21.123456"
}
```

## Changelog

- **v0.1.0** (2026-05-02): Initial release
  - Core voice streaming functionality
  - LLM integration with OpenAI
  - CrewAI multi-agent system
  - GraphQL API with subscriptions
  - PII anonymization
"""

OPENAPI_TERMS_OF_SERVICE: Final[str] = "https://example.com/terms"

OPENAPI_CONTACT: Final[dict[str, str]] = {
    "name": "Ekko Development Team",
    "url": "https://github.com/yourusername/ekko",
    "email": "lfr@tik-ai.dk",
}

OPENAPI_LICENSE: Final[dict[str, str]] = {
    "name": "MIT License",
    "url": "https://opensource.org/licenses/MIT",
}

# Server configurations
OPENAPI_SERVERS: Final[list[dict[str, str]]] = [
    {
        "url": "http://localhost:8000",
        "description": "Local development server",
    },
    {
        "url": "http://localhost:8000",
        "description": "Production server (desktop app)",
    },
]

# Tag metadata for route grouping
OPENAPI_TAGS: Final[list[dict[str, str]]] = [
    {
        "name": "health",
        "description": "Health check and system status endpoints",
    },
    {
        "name": "stream",
        "description": "Real-time audio streaming and processing",
    },
    {
        "name": "chat",
        "description": "Conversational AI endpoints",
    },
    {
        "name": "graphql",
        "description": "GraphQL API with queries, mutations, and subscriptions",
    },
]

# External documentation
OPENAPI_EXTERNAL_DOCS: Final[dict[str, str]] = {
    "description": "Project Documentation",
    "url": "https://github.com/yourusername/ekko/blob/main/README.md",
}

# Schema customization
OPENAPI_SCHEMA_EXTRA: Final[dict[str, object]] = {
    "x-logo": {
        "url": "https://example.com/logo.png",
        "altText": "Ekko Logo",
    },
}

# Response examples
OPENAPI_RESPONSES: Final[dict[int, dict[str, object]]] = {
    400: {
        "description": "Bad Request - Invalid input parameters",
        "content": {
            "application/json": {
                "example": {
                    "detail": "Invalid request format",
                    "error_code": "VALIDATION_ERROR",
                }
            }
        },
    },
    401: {
        "description": "Unauthorized - Authentication required",
        "content": {
            "application/json": {
                "example": {
                    "detail": "Authentication credentials were not provided",
                    "error_code": "UNAUTHORIZED",
                }
            }
        },
    },
    403: {
        "description": "Forbidden - Insufficient permissions",
        "content": {
            "application/json": {
                "example": {
                    "detail": "You don't have permission to access this resource",
                    "error_code": "FORBIDDEN",
                }
            }
        },
    },
    404: {
        "description": "Not Found - Resource doesn't exist",
        "content": {
            "application/json": {
                "example": {
                    "detail": "The requested resource was not found",
                    "error_code": "NOT_FOUND",
                }
            }
        },
    },
    422: {
        "description": "Unprocessable Entity - Validation error",
        "content": {
            "application/json": {
                "example": {
                    "detail": [
                        {
                            "loc": ["body", "field_name"],
                            "msg": "field required",
                            "type": "value_error.missing",
                        }
                    ]
                }
            }
        },
    },
    429: {
        "description": "Too Many Requests - Rate limit exceeded",
        "content": {
            "application/json": {
                "example": {
                    "detail": "Rate limit exceeded. Try again later.",
                    "error_code": "RATE_LIMIT_EXCEEDED",
                }
            }
        },
    },
    500: {
        "description": "Internal Server Error - Something went wrong",
        "content": {
            "application/json": {
                "example": {
                    "detail": "An internal server error occurred",
                    "error_code": "INTERNAL_SERVER_ERROR",
                }
            }
        },
    },
    503: {
        "description": "Service Unavailable - Server is temporarily unavailable",
        "content": {
            "application/json": {
                "example": {
                    "detail": "Service temporarily unavailable",
                    "error_code": "SERVICE_UNAVAILABLE",
                }
            }
        },
    },
}
