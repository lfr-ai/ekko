"""Production environment configuration."""

from typing import final

from pydantic_settings import SettingsConfigDict

from ekko.config.enums import DatabaseBackend, Environment
from ekko.config.runtime import ROOT_DIR
from ekko.config.settings.base import BaseAppConfig


@final
class ProductionConfig(BaseAppConfig):
    """Settings for production deployments."""

    model_config = SettingsConfigDict(
        env_file=(
            ROOT_DIR / ".env",
            ROOT_DIR / ".env.prod",
        ),
    )

    environment: Environment = Environment.PROD
    debug: bool = False
    log_level: str = "WARNING"
    database_backend: DatabaseBackend = DatabaseBackend.POSTGRESQL
    graphql_enable_ide: bool = False
    graphql_enable_introspection: bool = False
    graphql_enable_legacy_ws_protocol: bool = False
    graphql_subscription_auth_required: bool = True
    pii_policy_profile: str = "strict"
