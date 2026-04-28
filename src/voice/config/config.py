import getpass
import os
import socket
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv
from pyaudiowpatch import paInt16

ROOT_DIR_PATH = Path(__file__).resolve().parents[3]
load_dotenv(ROOT_DIR_PATH / ".env")


@dataclass
class Config:
    """
    Configuration class for storing settings.
    """

    # System info
    USER_ID = getpass.getuser()
    HOSTNAME = socket.gethostname()

    # Paths
    ROOT_DIR_PATH: Path = ROOT_DIR_PATH
    SRC_DIR_PATH: Path = ROOT_DIR_PATH / "src"
    PACKAGE_DIR_PATH: Path = SRC_DIR_PATH / "voice"
    LOGS_DIR_PATH: Path = ROOT_DIR_PATH / "logs"
    PROMPT_DIR_PATH: Path = PACKAGE_DIR_PATH / "prompts"
    INTERACTION_DIR_PATH: Path = PACKAGE_DIR_PATH / "interaction"
    # Use the infrastructure implementation for the audio streamer TCP server
    AUDIO_STREAMER_TCP_SERVER_MODULE_PATH: str = "voice.infrastructure.audio_streamer.audio_streamer_tcp_server"

    # Server settings
    HOST: str = "127.0.0.1"
    PORT: int = 6500
    AUDIO_STREAMER_TCP_PORT: int = 6600

    # OpenAI settings (do not hardcode provider endpoints here)
    # Prefer setting environment variables: OPENAI_API_KEY (or OPENAI_KEY), OPENAI_ENDPOINT, OPENAI_VERSION
    OPENAI_VERSION: str = os.getenv("OPENAI_VERSION", "")

    # Credentials: prefer OPENAI_API_KEY but fall back to OPENAI_KEY for backward compatibility
    OPENAI_KEY: str = os.getenv("OPENAI_KEY", os.getenv("OPENAI_API_KEY", ""))

    # Endpoint: leave empty by default so callers decide whether to use OpenAI or Azure OpenAI
    OPENAI_ENDPOINT: str = os.getenv("OPENAI_ENDPOINT", "")

    # Audio settings
    AUDIO_FORMAT: int = paInt16
    AUDIO_FRAMES_PER_BUFFER: int = 1024

    # Axillary constants
    SLEEP_DELAY_SECONDS: float = 0.1
    WAIT_TIMEOUT_SECONDS: int = 2
    MAX_READ_BYTES: int = 100

    def __post_init__(self) -> None:
        """Populate/override values from the canonical AppSettings `SETTINGS`.

        This provides a backwards-compatible bridge so existing call sites
        that instantiate :class:`Config` continue to work while the codebase
        migrates to the new :mod:`voice.config.settings` usage.
        """
        # Lazily attempt to read the canonical AppSettings. Use get_settings()
        # to avoid importing a module-level `SETTINGS` object which would
        # make assigning ``None`` in the except-block type-unstable for mypy.
        APP_SETTINGS = None
        try:
            from voice.config.settings import get_settings

            APP_SETTINGS = get_settings()
        except Exception:
            APP_SETTINGS = None

        if APP_SETTINGS is None:
            return

        # Map well-known, overlapping settings where present in AppSettings
        try:
            self.HOST = getattr(APP_SETTINGS, "host", self.HOST)
            self.PORT = getattr(APP_SETTINGS, "port", self.PORT)
            # logs_dir_path in AppSettings may be a Path already
            self.LOGS_DIR_PATH = Path(getattr(APP_SETTINGS, "logs_dir_path", self.LOGS_DIR_PATH))
        except Exception:
            # Be forgiving: do not raise if Settings are missing or malformed
            pass

        # OpenAI key may be a SecretStr in AppSettings; convert to plain str when present
        try:
            api_key = getattr(APP_SETTINGS, "openai_api_key", None)
            if api_key is not None:
                if hasattr(api_key, "get_secret_value"):
                    self.OPENAI_KEY = api_key.get_secret_value()
                else:
                    self.OPENAI_KEY = str(api_key)
        except Exception:
            pass

        # Azure/OpenAI API version mapping (if provided)
        try:
            version = getattr(APP_SETTINGS, "azure_openai_version", None)
            if version:
                self.OPENAI_VERSION = version
        except Exception:
            pass
