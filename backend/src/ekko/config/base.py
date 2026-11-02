"""Aggregate application configuration composed from the settings facets.

Combines the per-domain settings facets in :mod:`ekko.config.settings` into the
single :class:`BaseAppConfig` that every environment specializes. Each facet owns
one cohesive area (server, GraphQL, LLM, speech, audio, database, paths, prompts,
redis) and shares the ``EKKO_`` environment binding through ``ConfiguredSettings``.
Environment subclasses live in :mod:`ekko.config.environments`.
"""

from ekko.config.settings import (
    AudioSettings,
    DatabaseSettings,
    GeneralSettings,
    GraphQLSettings,
    LLMSettings,
    PathSettings,
    PromptSettings,
    RedisSettings,
    ServerSettings,
    SpeechSettings,
)


class BaseAppConfig(
    AudioSettings,
    DatabaseSettings,
    GeneralSettings,
    GraphQLSettings,
    LLMSettings,
    PathSettings,
    PromptSettings,
    RedisSettings,
    ServerSettings,
    SpeechSettings,
):
    """Configuration shared by all environments.

    Composes every settings facet; environment subclasses in
    :mod:`ekko.config.environments` add their ``env_file`` sources and overrides.
    """
