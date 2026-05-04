"""Adapter bridging AudioStreamerController to the AudioStreamerControllerProtocol."""

from ekko.config.settings import BaseAppConfig
from ekko.core.interfaces import AudioStreamerControllerProtocol
from ekko.infrastructure.audio_streamer.audio_streamer_controller import (
    AudioStreamerController,
)


def create_audio_streamer_controller(
    settings: BaseAppConfig,
) -> AudioStreamerControllerProtocol:
    return AudioStreamerController(settings)
