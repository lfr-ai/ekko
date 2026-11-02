"""Development environment configuration."""

from __future__ import annotations

from typing import final

from pydantic_settings import SettingsConfigDict

from ekko.config.base import BaseAppConfig
from ekko.config.enums import Environment
from ekko.config.runtime import ROOT_DIR_PATH


@final
class DevelopmentConfig(BaseAppConfig):
    """Settings for shared development environments."""

    model_config = SettingsConfigDict(
        env_file=(
            ROOT_DIR_PATH / ".env",
            ROOT_DIR_PATH / ".env.dev",
        ),
    )

    environment: Environment = Environment.DEV
    debug: bool = True
    log_level: str = "INFO"
    prompt_version_set: str = "development"
    graphql_enable_ide: bool = True
