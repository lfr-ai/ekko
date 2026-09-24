"""Tests for the REST summarization endpoint."""

from __future__ import annotations

from fastapi import FastAPI, status
from fastapi.testclient import TestClient

from ekko.ai.pii.anonymizer import PIIAnonymizer
from ekko.application.services import PIIService, SummarizerService
from ekko.presentation.api.exception_handlers import register_exception_handlers
from ekko.presentation.api.routes.summarize import router


class _RecordingGateway:
    """Captures the prompt actually sent to the LLM gateway."""

    def __init__(self):
        self.last_user_prompt: str | None = None

    def chat(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        model: str,
        temperature: float,
        max_completion_tokens: int,
    ) -> str:
        """Record the prompt submitted by the service."""
        _ = (system_prompt, model, temperature, max_completion_tokens)
        self.last_user_prompt = user_prompt
        return "summary of: " + user_prompt[:40]


class _StaticPromptRegistry:
    """Static prompt registry test double."""

    def load_prompt(self, prompt_key: str) -> str:
        """Load the fixed summarize template."""
        _ = prompt_key
        return "Summarize:\n{content}"


def _client(*, gateway: _RecordingGateway) -> TestClient:
    app = FastAPI()
    app.include_router(router)
    register_exception_handlers(app)
    pii_service = PIIService(anonymizer=PIIAnonymizer(), profile="standard")
    app.state.summarizer_service = SummarizerService(
        gateway=gateway,
        prompt_registry=_StaticPromptRegistry(),
        pii_service=pii_service,
    )
    return TestClient(app)


def test_summarize_returns_summary() -> None:
    """Summarize submitted chunks and return the generated text."""
    response = _client(gateway=_RecordingGateway()).post(
        "/summarize", json={"chunks": ["First chunk.", "Second chunk."]}
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["summary"].startswith("summary of:")


def test_summarize_rejects_empty_chunks() -> None:
    """Reject an empty chunk list at the HTTP boundary."""
    response = _client(gateway=_RecordingGateway()).post("/summarize", json={"chunks": []})

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_summarize_never_sends_raw_pii_to_the_gateway() -> None:
    """PII in submitted chunks must be anonymized before reaching the LLM gateway."""
    gateway = _RecordingGateway()

    response = _client(gateway=gateway).post("/summarize", json={"chunks": ["Contact me at test@example.com"]})

    assert response.status_code == status.HTTP_200_OK
    assert gateway.last_user_prompt is not None
    assert "test@example.com" not in gateway.last_user_prompt
    assert "[EMAIL-REDACTED]" in gateway.last_user_prompt
