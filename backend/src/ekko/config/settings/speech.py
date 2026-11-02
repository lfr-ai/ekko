"""Azure Speech (speech-to-text) settings."""

from pydantic import SecretStr

from ekko.config.settings._shared import ConfiguredSettings


class SpeechSettings(ConfiguredSettings):
    """Azure Speech Services credentials and recognition settings."""

    azure_speech_key: SecretStr | None = None
    azure_speech_region: str = "northeurope"
    azure_speech_language: str = "da-DK"
    azure_speech_recognition_mode: str = "continuous"
    stt_device: str = "cpu"
    stt_compute_type: str = "default"
