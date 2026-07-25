"""Tests for infrastructure retry utilities."""

import pytest
from httpx import HTTPStatusError, Request, Response
from openai import RateLimitError

from ekko.infrastructure.helpers.retry import (
    _RETRYABLE_HTTP_STATUS_CODES,
    _is_retryable_http_error,
    api_retry,
    http_retry,
)


class TestIsRetryableHttpError:
    def test_retryable_500(self):
        request = Request("GET", "http://test")
        response = Response(500, request=request)
        exc = HTTPStatusError("err", request=request, response=response)
        assert _is_retryable_http_error(exc) is True

    def test_retryable_502(self):
        request = Request("GET", "http://test")
        response = Response(502, request=request)
        exc = HTTPStatusError("err", request=request, response=response)
        assert _is_retryable_http_error(exc) is True

    def test_retryable_503(self):
        request = Request("GET", "http://test")
        response = Response(503, request=request)
        exc = HTTPStatusError("err", request=request, response=response)
        assert _is_retryable_http_error(exc) is True

    def test_retryable_504(self):
        request = Request("GET", "http://test")
        response = Response(504, request=request)
        exc = HTTPStatusError("err", request=request, response=response)
        assert _is_retryable_http_error(exc) is True

    def test_non_retryable_400(self):
        request = Request("GET", "http://test")
        response = Response(400, request=request)
        exc = HTTPStatusError("err", request=request, response=response)
        assert _is_retryable_http_error(exc) is False

    def test_non_retryable_404(self):
        request = Request("GET", "http://test")
        response = Response(404, request=request)
        exc = HTTPStatusError("err", request=request, response=response)
        assert _is_retryable_http_error(exc) is False

    def test_non_http_error(self):
        assert _is_retryable_http_error(ValueError("random")) is False


class TestRetryableStatusCodeSet:
    def test_expected_codes(self):
        assert 500 in _RETRYABLE_HTTP_STATUS_CODES
        assert 502 in _RETRYABLE_HTTP_STATUS_CODES
        assert 503 in _RETRYABLE_HTTP_STATUS_CODES
        assert 504 in _RETRYABLE_HTTP_STATUS_CODES
        assert 400 not in _RETRYABLE_HTTP_STATUS_CODES
        assert 401 not in _RETRYABLE_HTTP_STATUS_CODES


class TestHttpRetryDecorator:
    def test_retries_on_connection_error(self):
        call_count = 0

        @http_retry
        def flaky():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ConnectionError("refused")
            return "ok"

        result = flaky()
        assert result == "ok"
        assert call_count == 3

    def test_raises_after_max_attempts(self):
        @http_retry
        def always_fails():
            raise TimeoutError("timeout")

        with pytest.raises(TimeoutError):
            always_fails()

    def test_no_retry_on_non_retryable(self):
        call_count = 0

        @http_retry
        def bad_request():
            nonlocal call_count
            call_count += 1
            raise ValueError("not retryable")

        with pytest.raises(ValueError, match="not retryable"):
            bad_request()
        assert call_count == 1


class TestApiRetryDecorator:
    def test_retries_on_rate_limit(self):
        call_count = 0

        @api_retry
        def rate_limited():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise RateLimitError(
                    message="rate limited",
                    response=Response(429, request=Request("POST", "http://test")),
                    body=None,
                )
            return "ok"

        result = rate_limited()
        assert result == "ok"
        assert call_count == 3

    def test_retries_on_connection_error(self):
        call_count = 0

        @api_retry
        def connection_issue():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ConnectionError("network")
            return "recovered"

        result = connection_issue()
        assert result == "recovered"
