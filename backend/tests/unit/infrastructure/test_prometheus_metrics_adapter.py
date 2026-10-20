"""Tests for the infrastructure Prometheus metrics adapter."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

import ekko.infrastructure.prometheus_metrics_adapter as metrics_module


class TestPrometheusMetricsAdapter:
    @pytest.mark.unit
    def test_request_observations_record_status_and_duration(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        requests = MagicMock()
        duration = MagicMock()
        monkeypatch.setattr(metrics_module, "LLM_REQUESTS_TOTAL", requests)
        monkeypatch.setattr(metrics_module, "LLM_REQUEST_DURATION_SECONDS", duration)
        adapter = metrics_module.PrometheusMetricsAdapter()

        adapter.record_request_success(operation="chat", duration_seconds=0.25)
        adapter.record_request_failure(operation="achat", duration_seconds=0.5)

        requests.labels.assert_any_call(operation="chat", status="ok")
        requests.labels.assert_any_call(operation="achat", status="error")
        duration.labels.assert_any_call(operation="chat")
        duration.labels.assert_any_call(operation="achat")
        requests.labels.return_value.inc.assert_called()
        duration.labels.return_value.observe.assert_called()

    @pytest.mark.unit
    def test_token_and_cost_observations_record_values(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        tokens = MagicMock()
        cost = MagicMock()
        monkeypatch.setattr(metrics_module, "LLM_REQUEST_TOKENS_TOTAL", tokens)
        monkeypatch.setattr(metrics_module, "LLM_REQUEST_COST_TOTAL", cost)
        adapter = metrics_module.PrometheusMetricsAdapter()

        adapter.record_token_usage(
            operation="achat",
            input_tokens=7,
            output_tokens=3,
        )
        adapter.record_cost(operation="achat", cost_usd=0.01)

        tokens.labels.assert_any_call(operation="achat", token_type="input")
        tokens.labels.assert_any_call(operation="achat", token_type="output")
        tokens.labels.return_value.inc.assert_called()
        cost.labels.assert_called_once_with(operation="achat")
        cost.labels.return_value.inc.assert_called_once_with(0.01)
