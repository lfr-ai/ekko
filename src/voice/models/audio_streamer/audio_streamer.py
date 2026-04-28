"""Compatibility shim: re-export AudioStreamer from infrastructure.

This keeps the historical import path `voice.models.audio_streamer.audio_streamer`
working for tests and older code while the implementation lives in
`voice.infrastructure.audio_streamer`.
"""

from voice.infrastructure.audio_streamer.audio_streamer import AudioStreamer

__all__ = ["AudioStreamer"]
