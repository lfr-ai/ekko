"""GraphQL transport settings for a trusted local client."""

from ekko.config.settings._shared import ConfiguredSettings


class GraphQLSettings(ConfiguredSettings):
    """GraphQL IDE and HTTP transport toggles."""

    graphql_allow_get_queries: bool = False
    graphql_enable_ide: bool = True
