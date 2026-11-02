"""Production environment configuration."""

from __future__ import annotations

from typing import final

from pydantic_settings import SettingsConfigDict

from ekko.config.base import BaseAppConfig
from ekko.config.enums import Environment
from ekko.config.runtime import ROOT_DIR_PATH


@final
class ProductionConfig(BaseAppConfig):
    """Settings for production deployments."""

    model_config = SettingsConfigDict(
        env_file=(
            ROOT_DIR_PATH / ".env",
            ROOT_DIR_PATH / ".env.prod",
        ),
    )

    environment: Environment = Environment.PROD
    debug: bool = False
    log_level: str = "WARNING"
    prompt_version_set: str = "production"
    graphql_enable_ide: bool = False
    pii_policy_profile: str = "strict"
