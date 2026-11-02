"""Factory constructing the audio streamer controller port implementation."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ekko.infrastructure.audio_streamer.audio_streamer_controller import (
    AudioStreamerController,
)

if TYPE_CHECKING:
    from ekko.config.base import BaseAppConfig
    from ekko.core.ports import AudioStreamerControllerPort


def create_audio_streamer_controller(
    settings: BaseAppConfig,
) -> AudioStreamerControllerPort:
    """Create an audio streamer controller bound to the given settings."""
    return AudioStreamerController(settings)
