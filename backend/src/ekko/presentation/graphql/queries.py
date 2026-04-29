"""Root GraphQL queries."""

from __future__ import annotations

import strawberry
from strawberry.types import Info

from ekko.core.enums import ServiceStatus
from ekko.presentation.graphql.types import (
    ConversationType,
    DependencyHealthType,
    HealthType,
    PIIResultType,
)


@strawberry.type
class Query:
    """Root query type."""

    @strawberry.field
    async def health(self, info: Info) -> HealthType:
        """Basic health check."""
        from ekko.config.settings import get_settings

        settings = get_settings()
        return HealthType(
            status=ServiceStatus.HEALTHY,
            environment=settings.environment.value,
            dependencies=[],
        )

    @strawberry.field
    async def health_ready(self, info: Info) -> HealthType:
        """Deep health check with dependency probes."""
        from ekko.config.settings import get_settings

        settings = get_settings()
        deps: list[DependencyHealthType] = []

        # Database probe via context-injected engine
        db_engine = info.context.get("db_engine")
        if db_engine is not None:
            try:
                from sqlalchemy import text

                async with db_engine.connect() as conn:
                    await conn.execute(text("SELECT 1"))
                deps.append(DependencyHealthType(name="database", healthy=True))
            except Exception as exc:
                deps.append(DependencyHealthType(name="database", healthy=False, detail=str(exc)))
        else:
            deps.append(DependencyHealthType(name="database", healthy=False, detail="not configured"))

        all_healthy = all(d.healthy for d in deps)
        return HealthType(
            status=ServiceStatus.HEALTHY if all_healthy else ServiceStatus.DEGRADED,
            environment=settings.environment.value,
            dependencies=deps,
        )

    @strawberry.field
    async def conversation(self, id: str) -> ConversationType | None:  # noqa: A002
        """Get a conversation by ID."""
        return None

    @strawberry.field
    async def conversations(self, limit: int = 20, offset: int = 0) -> list[ConversationType]:
        """List conversations with pagination."""
        return []

    @strawberry.field
    async def check_pii(self, info: Info, text: str) -> PIIResultType:
        """Check text for PII without modifying it."""
        anonymizer = info.context.get("pii_anonymizer")
        if anonymizer is None:
            from ekko.ai.pii.anonymizer import PIIAnonymizer

            anonymizer = PIIAnonymizer()
        result = anonymizer.anonymize(text)
        return PIIResultType(
            anonymized_text=result.anonymized_text,
            pii_found=result.has_pii,
            match_count=len(result.pii_matches),
        )
