"""Tests for infrastructure retry policies."""

from __future__ import annotations

import httpx
import litellm
import pytest

from ekko.infrastructure.helpers.retry import api_retry, http_retry


class TestHttpRetry:
    """Test retries for transient HTTP failures."""

    @pytest.mark.unit
    def test_retryable_status_retries_until_success(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr("tenacity.nap.time.sleep", lambda _seconds: None)
        call_count = 0

        @http_retry
        def flaky_request() -> str:
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                request = httpx.Request("GET", "https://example.com")
                response = httpx.Response(503, request=request)
                raise httpx.HTTPStatusError(
                    "service unavailable",
                    request=request,
                    response=response,
                )
            return "ok"

        result = flaky_request()

        assert result == "ok"
        assert call_count == 3

    @pytest.mark.unit
    def test_non_retryable_status_raises_without_retry(self) -> None:
        request = httpx.Request("GET", "https://example.com")
        response = httpx.Response(400, request=request)
        call_count = 0

        @http_retry
        def invalid_request() -> str:
            nonlocal call_count
            call_count += 1
            raise httpx.HTTPStatusError(
                "bad request",
                request=request,
                response=response,
            )

        with pytest.raises(httpx.HTTPStatusError, match="bad request"):
            invalid_request()

        assert call_count == 1

    @pytest.mark.unit
    def test_timeout_raises_after_max_attempts(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr("tenacity.nap.time.sleep", lambda _seconds: None)

        @http_retry
        def timed_out() -> str:
            raise TimeoutError("timeout")

        with pytest.raises(TimeoutError, match="timeout"):
            timed_out()


class TestApiRetry:
    """Test retries for LiteLLM provider failures."""

    @pytest.mark.unit
    def test_transient_provider_error_retries_until_success(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr("tenacity.nap.time.sleep", lambda _seconds: None)
        call_count = 0

        @api_retry
        def rate_limited() -> str:
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise litellm.RateLimitError(
                    message="temporarily unavailable",
                    llm_provider="openai",
                    model="gpt-4o",
                )
            return "ok"

        result = rate_limited()

        assert result == "ok"
        assert call_count == 3

    @pytest.mark.unit
    def test_non_transient_error_is_not_retried(self) -> None:
        call_count = 0

        @api_retry
        def invalid_request() -> str:
            nonlocal call_count
            call_count += 1
            raise ValueError("invalid input")

        with pytest.raises(ValueError, match="invalid input"):
            invalid_request()

        assert call_count == 1
