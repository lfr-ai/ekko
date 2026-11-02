"""General cross-cutting application settings."""

from ekko.config.enums import Environment
from ekko.config.settings._shared import ConfiguredSettings


class GeneralSettings(ConfiguredSettings):
    """Cross-cutting application settings that belong to no single domain facet."""

    environment: Environment = Environment.LOCAL
    debug: bool = False
    log_level: str = "INFO"
    sentry_dsn: str | None = None
    metrics_enabled: bool = True
