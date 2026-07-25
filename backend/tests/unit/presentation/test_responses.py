"""Unit tests for API response models and constants."""

from __future__ import annotations

import pytest
from fastapi import status
from pydantic import ValidationError

from ekko.presentation.api.responses import (
    BAD_REQUEST_RESPONSE,
    INTERNAL_SERVER_ERROR_RESPONSE,
    JSON_OK_RESPONSE,
    NOT_FOUND_RESPONSE,
    SERVICE_UNAVAILABLE_RESPONSE,
    STANDARD_ERROR_RESPONSES,
    TOO_MANY_REQUESTS_RESPONSE,
    UNPROCESSABLE_CONTENT_RESPONSE,
    ErrorResponse,
)


@pytest.mark.unit
class TestErrorResponse:
    """Test ErrorResponse model."""

    def test_construction(self) -> None:
        """Construct error response with detail."""
        resp = ErrorResponse(detail="Something went wrong")
        assert resp.detail == "Something went wrong"

    def test_immutable(self) -> None:
        """Reject mutation on frozen model."""
        resp = ErrorResponse(detail="test")
        with pytest.raises(ValidationError):
            resp.detail = "changed"  # type: ignore[misc]

    def test_serialization(self) -> None:
        """Serialize to dict with detail key."""
        resp = ErrorResponse(detail="Not found")
        data = resp.model_dump()
        assert data == {"detail": "Not found"}


@pytest.mark.unit
class TestResponseConstants:
    """Test response constant dictionaries."""

    def test_json_ok_has_description(self) -> None:
        """JSON_OK_RESPONSE has description key."""
        assert "description" in JSON_OK_RESPONSE

    def test_bad_request_has_model(self) -> None:
        """BAD_REQUEST_RESPONSE references ErrorResponse model."""
        assert BAD_REQUEST_RESPONSE["model"] is ErrorResponse

    def test_not_found_has_model(self) -> None:
        """NOT_FOUND_RESPONSE references ErrorResponse model."""
        assert NOT_FOUND_RESPONSE["model"] is ErrorResponse

    def test_unprocessable_content_has_model(self) -> None:
        """UNPROCESSABLE_CONTENT_RESPONSE references ErrorResponse model."""
        assert UNPROCESSABLE_CONTENT_RESPONSE["model"] is ErrorResponse

    def test_too_many_requests_has_model(self) -> None:
        """TOO_MANY_REQUESTS_RESPONSE references ErrorResponse model."""
        assert TOO_MANY_REQUESTS_RESPONSE["model"] is ErrorResponse

    def test_service_unavailable_has_model(self) -> None:
        """SERVICE_UNAVAILABLE_RESPONSE references ErrorResponse model."""
        assert SERVICE_UNAVAILABLE_RESPONSE["model"] is ErrorResponse

    def test_internal_server_error_has_model(self) -> None:
        """INTERNAL_SERVER_ERROR_RESPONSE references ErrorResponse model."""
        assert INTERNAL_SERVER_ERROR_RESPONSE["model"] is ErrorResponse


@pytest.mark.unit
class TestStandardErrorResponses:
    """Test STANDARD_ERROR_RESPONSES mapping."""

    def test_contains_422(self) -> None:
        """Map includes 422 status."""
        assert status.HTTP_422_UNPROCESSABLE_CONTENT in STANDARD_ERROR_RESPONSES

    def test_contains_429(self) -> None:
        """Map includes 429 status."""
        assert status.HTTP_429_TOO_MANY_REQUESTS in STANDARD_ERROR_RESPONSES

    def test_contains_500(self) -> None:
        """Map includes 500 status."""
        assert status.HTTP_500_INTERNAL_SERVER_ERROR in STANDARD_ERROR_RESPONSES

    def test_count(self) -> None:
        """Map has exactly 3 entries."""
        assert len(STANDARD_ERROR_RESPONSES) == 3
