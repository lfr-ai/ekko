"""Strawberry GraphQL schema assembly.

Follows the golden-standard pattern: Query + Mutation + Subscription with
extensions for caching, rate limiting, and session lifecycle management.

Security extensions (MaxAliasesLimiter, MaxTokensLimiter) prevent abuse
via deeply nested or overly complex queries.
"""

from __future__ import annotations

import strawberry
from strawberry.extensions import ParserCache, ValidationCache
from strawberry.extensions.max_aliases import MaxAliasesLimiter
from strawberry.extensions.max_tokens import MaxTokensLimiter
from strawberry.extensions.query_depth_limiter import QueryDepthLimiter

from ekko.presentation.graphql.extensions import (
    QueryTimingExtension,
    RequestContextExtension,
    SessionLifecycleExtension,
)
from ekko.presentation.graphql.mutations import Mutation
from ekko.presentation.graphql.queries import Query
from ekko.presentation.graphql.subscriptions import Subscription

schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    subscription=Subscription,
    extensions=[
        lambda: ParserCache(maxsize=256),
        lambda: ValidationCache(maxsize=256),
        lambda: QueryDepthLimiter(max_depth=10),
        lambda: MaxAliasesLimiter(max_alias_count=25),
        lambda: MaxTokensLimiter(max_token_count=2500),
        QueryTimingExtension,
        RequestContextExtension,
        SessionLifecycleExtension,
    ],
)
