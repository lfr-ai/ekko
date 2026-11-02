"""Metrics observation port for recording LLM request telemetry."""

from __future__ import annotations

from typing import Protocol


class MetricsPort(Protocol):
    """Protocol for provider-agnostic metrics observation.

    Records LLM request success/failure, duration, tokens, and costs
    without recording prompts or completions.
    """

    def record_request_success(
        self,
        *,
        operation: str,
        duration_seconds: float,
    ) -> None:
        """Record successful chat telemetry.

        Args:
            operation (str): Operation name (chat, achat, achat_structured).
            duration_seconds (float): Elapsed time in seconds.
        """
        ...

    def record_request_failure(
        self,
        *,
        operation: str,
        duration_seconds: float,
    ) -> None:
        """Record failed chat telemetry.

        Args:
            operation (str): Operation name.
            duration_seconds (float): Elapsed time in seconds.
        """
        ...

    def record_token_usage(
        self,
        *,
        operation: str,
        input_tokens: int,
        output_tokens: int,
    ) -> None:
        """Record LLM token usage (only when cost tracking is enabled).

        Args:
            operation (str): Operation name.
            input_tokens (int): Number of input tokens.
            output_tokens (int): Number of output tokens.
        """
        ...

    def record_cost(
        self,
        *,
        operation: str,
        cost_usd: float,
    ) -> None:
        """Record LLM request cost in USD (only when cost tracking is enabled).

        Args:
            operation (str): Operation name.
            cost_usd (float): Cost in USD.
        """
        ...
