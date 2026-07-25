"""Unit tests for FastAPI exception handlers."""

from __future__ import annotations

import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient

from ekko.core.exceptions import (
    AudioDeviceError,
    ConfigurationError,
    EkkoError,
    LLMError,
    PromptNotFoundError,
    STTError,
)
from ekko.presentation.api.exception_handlers import register_exception_handlers


@pytest.fixture
def app() -> FastAPI:
    """Create test FastAPI app with exception handlers registered."""
    app = FastAPI()
    register_exception_handlers(app)
    return app


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    """Create test client."""
    return TestClient(app, raise_server_exceptions=False)


@pytest.mark.unit
class TestRequestValidationError:
    """Test RequestValidationError handler."""

    def test_returns_422(self, app: FastAPI, client: TestClient) -> None:
        """Return 422 for validation errors."""
        from pydantic import BaseModel

        class Body(BaseModel):
            value: int

        @app.post("/test")
        async def _endpoint(body: Body) -> dict:
            return {}

        response = client.post("/test", json={"value": "not_int"})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        assert response.json()["detail"] == "Request validation error"


@pytest.mark.unit
class TestPromptNotFoundError:
    """Test PromptNotFoundError handler."""

    def test_returns_404(self, app: FastAPI, client: TestClient) -> None:
        """Return 404 for missing prompts."""

        @app.get("/test")
        async def _endpoint() -> None:
            raise PromptNotFoundError("prompt_v1 not found")

        response = client.get("/test")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "prompt_v1 not found" in response.json()["detail"]


@pytest.mark.unit
class TestConfigurationError:
    """Test ConfigurationError handler."""

    def test_returns_500_with_masked_message(self, app: FastAPI, client: TestClient) -> None:
        """Return 500 and mask internal configuration details."""

        @app.get("/test")
        async def _endpoint() -> None:
            raise ConfigurationError("Missing EKKO_OPENAI_API_KEY")

        response = client.get("/test")
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.json()["detail"] == "Configuration error"


@pytest.mark.unit
class TestAudioDeviceError:
    """Test AudioDeviceError handler."""

    def test_returns_503(self, app: FastAPI, client: TestClient) -> None:
        """Return 503 for audio device failures."""

        @app.get("/test")
        async def _endpoint() -> None:
            raise AudioDeviceError("No capture device found")

        response = client.get("/test")
        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        assert response.json()["detail"] == "Audio device unavailable"


@pytest.mark.unit
class TestSTTError:
    """Test STTError handler."""

    def test_returns_503(self, app: FastAPI, client: TestClient) -> None:
        """Return 503 for STT service errors."""

        @app.get("/test")
        async def _endpoint() -> None:
            raise STTError("Whisper unavailable")

        response = client.get("/test")
        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        assert response.json()["detail"] == "Speech-to-text service error"


@pytest.mark.unit
class TestLLMError:
    """Test LLMError handler."""

    def test_returns_503(self, app: FastAPI, client: TestClient) -> None:
        """Return 503 for LLM service errors."""

        @app.get("/test")
        async def _endpoint() -> None:
            raise LLMError("Rate limited")

        response = client.get("/test")
        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        assert response.json()["detail"] == "LLM service error"


@pytest.mark.unit
class TestEkkoError:
    """Test generic EkkoError handler."""

    def test_returns_422_with_generic_message(self, app: FastAPI, client: TestClient) -> None:
        """Return 422 and mask domain error internals."""

        @app.get("/test")
        async def _endpoint() -> None:
            raise EkkoError("Internal domain logic detail")

        response = client.get("/test")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        assert response.json()["detail"] == "Request could not be processed"


@pytest.mark.unit
class TestUnhandledException:
    """Test generic Exception handler."""

    def test_returns_500_with_generic_message(self, app: FastAPI, client: TestClient) -> None:
        """Return 500 and mask unhandled exception details."""

        @app.get("/test")
        async def _endpoint() -> None:
            raise RuntimeError("Something unexpected")

        response = client.get("/test")
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.json()["detail"] == "Internal server error"
