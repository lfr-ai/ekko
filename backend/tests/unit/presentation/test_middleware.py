"""Tests for API middleware stack."""

import dataclasses

import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from ekko.presentation.api.middleware.authentication import (
    AuthenticationMiddleware,
    UserProfile,
)
from ekko.presentation.api.middleware.request_id import RequestIdMiddleware
from ekko.presentation.api.middleware.security_headers import SecurityHeadersMiddleware
from ekko.presentation.api.middleware.timing import TimingMiddleware


def _make_app(*middleware_classes):
    """Create a minimal FastAPI app with given middleware for testing."""
    app = FastAPI()

    @app.get("/test")
    async def test_endpoint():
        return {"ok": True}

    @app.get("/health")
    async def health_endpoint():
        return {"status": "ok"}

    for mw in reversed(middleware_classes):
        if isinstance(mw, tuple):
            app.add_middleware(mw[0], **mw[1])
        else:
            app.add_middleware(mw)
    return app


class TestRequestIdMiddleware:
    def test_generates_request_id(self):
        app = _make_app(RequestIdMiddleware)
        client = TestClient(app)
        response = client.get("/test")
        assert "X-Request-ID" in response.headers
        # UUID format
        assert len(response.headers["X-Request-ID"]) == 36

    def test_forwards_existing_request_id(self):
        app = _make_app(RequestIdMiddleware)
        client = TestClient(app)
        response = client.get("/test", headers={"X-Request-ID": "custom-id-123"})
        assert response.headers["X-Request-ID"] == "custom-id-123"


class TestSecurityHeadersMiddleware:
    def test_security_headers_present(self):
        app = _make_app(SecurityHeadersMiddleware)
        client = TestClient(app)
        response = client.get("/test")
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        assert response.headers["X-Frame-Options"] == "DENY"
        assert response.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"
        assert "camera=()" in response.headers["Permissions-Policy"]
        assert "default-src 'self'" in response.headers["Content-Security-Policy"]
        assert "frame-ancestors 'none'" in response.headers["Content-Security-Policy"]


class TestTimingMiddleware:
    def test_timing_header_present(self):
        app = _make_app(TimingMiddleware)
        client = TestClient(app)
        response = client.get("/test")
        assert "Server-Timing" in response.headers
        timing = response.headers["Server-Timing"]
        assert timing.startswith("total;dur=")
        # Duration should be a float
        dur = float(timing.split("=")[1])
        assert dur >= 0


class TestAuthenticationMiddleware:
    def test_attaches_dev_user_on_non_public_path(self):
        app = FastAPI()

        @app.get("/api/data")
        async def data_endpoint(request: Request):
            return {"user": request.state.user.username}

        app.add_middleware(AuthenticationMiddleware)
        client = TestClient(app)
        response = client.get("/api/data")
        assert response.status_code == 200
        assert response.json()["user"] == "dev-user"

    def test_custom_user_id(self):
        app = FastAPI()

        @app.get("/api/check")
        async def check(request: Request):
            return {"user": request.state.user.username}

        app.add_middleware(AuthenticationMiddleware, default_user_id="test-user")
        client = TestClient(app)
        response = client.get("/api/check")
        assert response.json()["user"] == "test-user"


class TestUserProfile:
    def test_defaults(self):
        profile = UserProfile(username="alice")
        assert profile.roles == frozenset()

    def test_frozen(self):
        profile = UserProfile(username="bob", roles=frozenset({"admin"}))
        with pytest.raises(dataclasses.FrozenInstanceError):
            profile.username = "eve"  # type: ignore[misc]
