"""Audio capture and IPC streamer settings."""

from ekko.config.settings._shared import ConfiguredSettings

_PYAUDIO_PA_INT16 = 8


class AudioSettings(ConfiguredSettings):
    """Audio capture format and TCP streamer transport knobs."""

    disable_audio: bool = False
    audio_streamer_tcp_port: int = 6600
    audio_streamer_tcp_server_module_path: str = "ekko.infrastructure.audio_streamer.audio_streamer_tcp_server"
    audio_format: int = _PYAUDIO_PA_INT16
    audio_frames_per_buffer: int = 1024
    audio_channels: int = 2
    audio_sample_rate: int = 48000
    max_read_bytes: int = 100
    sleep_delay_seconds: float = 0.1
    wait_timeout_seconds: int = 2
