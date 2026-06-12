"""Shared API response models and constants."""

from typing import Annotated, Final, TypeAlias

from fastapi import status
from pydantic import BaseModel, ConfigDict, Field

from ekko.core.types import BaseDict, JSONDict

_MIME_JSON: Final[str] = "application/json"


class ErrorResponse(BaseModel):
    """Standardized error response.

    Attributes:
        detail (str): Human-readable error detail describing the failure.
    """

    model_config = ConfigDict(frozen=True)

    detail: Annotated[
        str,
        Field(
            description="Human-readable error detail describing the failure",
            examples=[
                "Resource not found",
                "Authentication required",
            ],
        ),
    ]


JSON_OK_RESPONSE: Final[JSONDict] = {
    "description": "Successful response",
    "content": {
        _MIME_JSON: {
            "examples": {
                "success": {
                    "summary": "Successful response payload",
                    "value": {"message": "Request processed successfully"},
                }
            }
        }
    },
}

BAD_REQUEST_RESPONSE: Final[JSONDict] = {
    "description": "Request was malformed or invalid",
    "model": ErrorResponse,
    "content": {
        _MIME_JSON: {
            "examples": {
                "bad_request": {
                    "summary": "Malformed payload",
                    "value": {"detail": "Bad request. Please check your input data"},
                }
            }
        }
    },
}

NOT_FOUND_RESPONSE: Final[JSONDict] = {
    "description": "Requested resource could not be found",
    "model": ErrorResponse,
    "content": {
        _MIME_JSON: {
            "examples": {
                "not_found": {
                    "summary": "Resource missing",
                    "value": {"detail": "Resource not found"},
                }
            }
        }
    },
}

UNPROCESSABLE_CONTENT_RESPONSE: Final[JSONDict] = {
    "description": (
        "Request was well-formed, but the server cannot process it due to it being "
        "semantically invalid (validation error)."
    ),
    "model": ErrorResponse,
    "content": {
        _MIME_JSON: {
            "examples": {
                "validation_error": {
                    "summary": "Validation failure",
                    "value": {"detail": "Request validation error"},
                }
            }
        }
    },
}

TOO_MANY_REQUESTS_RESPONSE: Final[JSONDict] = {
    "description": ("Client has sent too many requests in a given amount of time (rate limiting)."),
    "model": ErrorResponse,
    "content": {
        _MIME_JSON: {
            "examples": {
                "rate_limited": {
                    "summary": "Rate limit exceeded",
                    "value": {"detail": "Too many requests; please try again later"},
                }
            }
        }
    },
}

SERVICE_UNAVAILABLE_RESPONSE: Final[JSONDict] = {
    "description": "Service temporarily unavailable",
    "model": ErrorResponse,
    "content": {
        _MIME_JSON: {
            "examples": {
                "service_unavailable": {
                    "summary": "Service unavailable",
                    "value": {"detail": "Service temporarily unavailable"},
                }
            }
        }
    },
}

INTERNAL_SERVER_ERROR_RESPONSE: Final[JSONDict] = {
    "description": ("Unexpected server error. A problem occurred on the server while processing the request."),
    "model": ErrorResponse,
    "content": {
        _MIME_JSON: {
            "examples": {
                "server_error": {
                    "summary": "Unhandled server failure",
                    "value": {"detail": "Server error"},
                }
            }
        }
    },
}


_StatusResponseMap: TypeAlias = dict[int, BaseDict]

STANDARD_ERROR_RESPONSES: Final[_StatusResponseMap] = {
    status.HTTP_422_UNPROCESSABLE_CONTENT: UNPROCESSABLE_CONTENT_RESPONSE,
    status.HTTP_429_TOO_MANY_REQUESTS: TOO_MANY_REQUESTS_RESPONSE,
    status.HTTP_500_INTERNAL_SERVER_ERROR: INTERNAL_SERVER_ERROR_RESPONSE,
}
