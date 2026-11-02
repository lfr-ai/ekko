"""Strawberry GraphQL schema assembly.

Exposes one read-only prompt catalog for learning GraphQL field selection.
Commands and streaming use REST and SSE respectively.
"""

from __future__ import annotations

import strawberry

from ekko.presentation.graphql.extensions import QueryTimingExtension, RequestContextExtension
from ekko.presentation.graphql.queries import Query

schema = strawberry.Schema(
    query=Query,
    extensions=[QueryTimingExtension, RequestContextExtension],
)
