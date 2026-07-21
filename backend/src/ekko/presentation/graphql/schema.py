"""Strawberry GraphQL schema assembly.

Follows the golden-standard pattern: Query + Mutation + Subscription with
extensions for caching, rate limiting, and session lifecycle management.

Security extensions (MaxAliasesLimiter, MaxTokensLimiter) prevent abuse
via deeply nested or overly complex queries.
"""

from __future__ import annotations

from collections.abc import Callable

import strawberry
from graphql.validation.rules.custom.no_schema_introspection import NoSchemaIntrospectionCustomRule
from strawberry.extensions import ParserCache, SchemaExtension, ValidationCache
from strawberry.extensions.add_validation_rules import AddValidationRules
from strawberry.extensions.max_aliases import MaxAliasesLimiter
from strawberry.extensions.max_tokens import MaxTokensLimiter
from strawberry.extensions.query_depth_limiter import QueryDepthLimiter
from strawberry.schema.config import StrawberryConfig

from ekko.config.settings import get_settings
from ekko.presentation.graphql.extensions import (
    PersistedOperationsExtension,
    QueryCostLimiterExtension,
    QueryTimingExtension,
    RequestContextExtension,
    SessionLifecycleExtension,
)
from ekko.presentation.graphql.mutations import Mutation
from ekko.presentation.graphql.queries import Query
from ekko.presentation.graphql.subscriptions import Subscription

_settings = get_settings()

_SchemaExtensionFactory = Callable[[], SchemaExtension]

_extensions: list[type[SchemaExtension] | _SchemaExtensionFactory] = [
    lambda: ParserCache(maxsize=256),
    lambda: ValidationCache(maxsize=256),
    lambda: QueryDepthLimiter(max_depth=_settings.graphql_max_query_depth),
    lambda: MaxAliasesLimiter(max_alias_count=_settings.graphql_max_alias_count),
    lambda: MaxTokensLimiter(max_token_count=_settings.graphql_max_token_count),
    lambda: QueryCostLimiterExtension(max_cost=_settings.graphql_max_query_cost),
    QueryTimingExtension,
    RequestContextExtension,
    SessionLifecycleExtension,
]

if _settings.graphql_enable_persisted_operations:
    _extensions.append(
        lambda: PersistedOperationsExtension(
            trusted_operation_hashes=set(_settings.graphql_trusted_operation_hashes),
            require_trusted_documents=_settings.graphql_require_trusted_documents,
        )
    )

if not _settings.graphql_enable_introspection:
    _extensions.append(lambda: AddValidationRules([NoSchemaIntrospectionCustomRule]))

schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    subscription=Subscription,
    extensions=_extensions,
    config=StrawberryConfig(
        batching_config={"max_operations": _settings.graphql_batch_max_operations},
    ),
)
