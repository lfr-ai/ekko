from voice.config.config import Config
from voice.core.protocols import AudioStreamerControllerProtocol
from voice.infrastructure.audio_streamer.audio_streamer_controller import (
    AudioStreamerController,
)


def create_audio_streamer_controller(
    cfg: Config,
) -> AudioStreamerControllerProtocol:
    return AudioStreamerController(cfg)
