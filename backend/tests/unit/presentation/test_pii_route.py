"""Tests for the REST PII endpoint."""

from __future__ import annotations

from fastapi import FastAPI, status
from fastapi.testclient import TestClient

from ekko.ai.pii.anonymizer import PIIAnonymizer
from ekko.application.services import PIIService
from ekko.presentation.api.routes.pii import router


def _client() -> TestClient:
    app = FastAPI()
    app.include_router(router)
    app.state.pii_service = PIIService(anonymizer=PIIAnonymizer(), profile="strict")
    return TestClient(app)


def test_anonymize_pii_returns_redacted_text() -> None:
    """Expose PII anonymization through canonical REST semantics."""
    response = _client().post("/pii/anonymize", json={"text": "Email test@example.com"})

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "anonymized_text": "Email [EMAIL-REDACTED]",
        "pii_found": True,
        "match_count": 1,
    }


def test_anonymize_pii_rejects_empty_text() -> None:
    """Reject empty request text at the HTTP boundary."""
    response = _client().post("/pii/anonymize", json={"text": ""})

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
