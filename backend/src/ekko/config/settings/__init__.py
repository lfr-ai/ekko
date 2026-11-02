"""Application settings facets.

Each facet owns one cohesive group of ``EKKO_`` environment fields and composes
into :class:`ekko.config.base.BaseAppConfig`.
"""

from ekko.config.settings._shared import ConfiguredSettings
from ekko.config.settings.audio import AudioSettings
from ekko.config.settings.database import DatabaseSettings
from ekko.config.settings.general import GeneralSettings
from ekko.config.settings.graphql import GraphQLSettings
from ekko.config.settings.llm import LLMSettings
from ekko.config.settings.paths import PathSettings
from ekko.config.settings.prompts import PromptSettings
from ekko.config.settings.redis import RedisSettings
from ekko.config.settings.server import ServerSettings
from ekko.config.settings.speech import SpeechSettings

__all__ = [
    "AudioSettings",
    "ConfiguredSettings",
    "DatabaseSettings",
    "GeneralSettings",
    "GraphQLSettings",
    "LLMSettings",
    "PathSettings",
    "PromptSettings",
    "RedisSettings",
    "ServerSettings",
    "SpeechSettings",
]
