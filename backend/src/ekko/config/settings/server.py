"""HTTP server binding settings."""

from ekko.config.settings._shared import ConfiguredSettings


class ServerSettings(ConfiguredSettings):
    """Uvicorn/HTTP server binding settings."""

    host: str = "127.0.0.1"
    port: int = 8000
    reload: bool = False
