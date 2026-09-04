"""Tests for the local and frozen application entrypoint."""

from __future__ import annotations

import sys

import pytest

from ekko.cli import run_app


@pytest.mark.unit
def test_main_when_frozen_and_browser_disabled_starts_server_without_opening_browser(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Skip browser launch for automated frozen-application smoke tests."""
    opened_urls: list[str] = []
    run_calls: list[tuple[str, dict[str, object]]] = []

    def record_browser_open(url: str) -> bool:
        opened_urls.append(url)
        return True

    def record_uvicorn_run(app: str, **kwargs: object) -> None:
        run_calls.append((app, kwargs))

    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setenv("EKKO_OPEN_BROWSER", "false")
    monkeypatch.setenv("EKKO_HOST", "127.0.0.1")
    monkeypatch.setenv("EKKO_PORT", "8765")
    monkeypatch.setattr(run_app.webbrowser, "open", record_browser_open)
    monkeypatch.setattr(run_app.uvicorn, "run", record_uvicorn_run)

    run_app.main()

    assert opened_urls == []
    assert run_calls == [
        (
            "ekko.composition.app_factory:create_app",
            {
                "factory": True,
                "host": "127.0.0.1",
                "port": 8765,
                "reload": False,
            },
        )
    ]
