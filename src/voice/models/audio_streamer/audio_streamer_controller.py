"""Compatibility shim for historical import path.

Use `voice.infrastructure.audio_streamer.audio_streamer_controller` as source of truth.
"""

from voice.infrastructure.audio_streamer.audio_streamer_controller import (
    AudioStreamerController,
)

__all__ = ["AudioStreamerController"]
