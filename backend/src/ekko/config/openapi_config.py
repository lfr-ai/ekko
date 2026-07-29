"""OpenAPI specification configuration for Ekko."""

from __future__ import annotations

from typing import Final

from fastapi import status

# OpenAPI metadata
OPENAPI_TITLE: Final[str] = "Ekko API"
OPENAPI_VERSION: Final[str] = "0.1.0"
OPENAPI_DESCRIPTION: Final[str] = """\
AI-powered voice assistant platform with real-time transcription, \
LLM summarization, and PII anonymization.

## Authentication

Local-only desktop application. Requests are auto-authenticated as `dev-user`.

## Error Responses

All errors return:

```json
{"detail": "...", "error_code": "SPECIFIC_ERROR_CODE"}
```
"""

OPENAPI_CONTACT: Final[dict[str, str]] = {
    "name": "Ekko Development Team",
    "url": "https://github.com/ap-pension/ekko",
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
        "description": "Real-time audio streaming control via GraphQL mutations",
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
    "url": "https://github.com/ap-pension/ekko/blob/main/README.md",
}

# Schema customization
# Response examples
OPENAPI_RESPONSES: dict[int | str, dict[str, object]] = {
    status.HTTP_400_BAD_REQUEST: {
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
    status.HTTP_401_UNAUTHORIZED: {
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
    status.HTTP_403_FORBIDDEN: {
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
    status.HTTP_404_NOT_FOUND: {
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
    status.HTTP_422_UNPROCESSABLE_CONTENT: {
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
    status.HTTP_429_TOO_MANY_REQUESTS: {
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
    status.HTTP_500_INTERNAL_SERVER_ERROR: {
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
    status.HTTP_503_SERVICE_UNAVAILABLE: {
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
