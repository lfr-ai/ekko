"""Infrastructure Prometheus metrics adapter implementing Core MetricsPort."""

from __future__ import annotations

from typing import final, override

from ekko.core.ports.external.metrics import MetricsPort
from ekko.infrastructure.metrics import (
    LLM_REQUEST_COST_TOTAL,
    LLM_REQUEST_DURATION_SECONDS,
    LLM_REQUEST_TOKENS_TOTAL,
    LLM_REQUESTS_TOTAL,
)


@final
class PrometheusMetricsAdapter(MetricsPort):
    """Prometheus adapter for provider-neutral LLM telemetry."""

    @override
    def record_request_success(
        self,
        *,
        operation: str,
        duration_seconds: float,
    ) -> None:
        """Record a successful LLM request."""
        LLM_REQUESTS_TOTAL.labels(operation=operation, status="ok").inc()
        LLM_REQUEST_DURATION_SECONDS.labels(operation=operation).observe(duration_seconds)

    @override
    def record_request_failure(
        self,
        *,
        operation: str,
        duration_seconds: float,
    ) -> None:
        """Record a failed LLM request."""
        LLM_REQUESTS_TOTAL.labels(operation=operation, status="error").inc()
        LLM_REQUEST_DURATION_SECONDS.labels(operation=operation).observe(duration_seconds)

    @override
    def record_token_usage(
        self,
        *,
        operation: str,
        input_tokens: int,
        output_tokens: int,
    ) -> None:
        """Record LLM token usage (only when cost tracking is enabled)."""
        LLM_REQUEST_TOKENS_TOTAL.labels(
            operation=operation,
            token_type="input",  # noqa: S106 - bounded metric label, not a secret
        ).inc(input_tokens)
        LLM_REQUEST_TOKENS_TOTAL.labels(
            operation=operation,
            token_type="output",  # noqa: S106 - bounded metric label, not a secret
        ).inc(output_tokens)

    @override
    def record_cost(
        self,
        *,
        operation: str,
        cost_usd: float,
    ) -> None:
        """Record LLM request cost in USD (only when cost tracking is enabled)."""
        LLM_REQUEST_COST_TOTAL.labels(operation=operation).inc(cost_usd)
