"""Tests for application lifespan composition."""

from __future__ import annotations

from dataclasses import dataclass

import pytest
from fastapi import FastAPI

from ekko.composition.lifespan import create_lifespan
from ekko.config.base import BaseAppConfig


@dataclass(frozen=True, slots=True)
class DisabledAudioContainer:
    """Container stub that exposes only disabled-audio settings."""

    settings: BaseAppConfig

    @property
    def audio_controller(self) -> object:
        """Reject unexpected audio-controller construction."""
        raise AssertionError("audio controller must not be constructed when audio is disabled")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_lifespan_when_audio_disabled_skips_audio_and_stt_construction(tmp_path) -> None:
    """Start the application without native audio or speech dependencies."""
    settings = BaseAppConfig(
        disable_audio=True,
        database_path=str(tmp_path / "ekko.db"),
    )
    app = FastAPI()
    app.state.container = DisabledAudioContainer(settings=settings)

    async with create_lifespan(app):
        assert not hasattr(app.state, "queue_manager")
        assert not hasattr(app.state, "controller")
        assert not hasattr(app.state, "stt")
