"""Root GraphQL queries."""

from __future__ import annotations

from typing import Final

import strawberry
from sqlalchemy import text
from strawberry.types import Info

from ekko.config.settings import get_settings
from ekko.core.enums import ServiceStatus
from ekko.presentation.graphql.pii_policy import PIIPolicySettings, apply_pii_policy
from ekko.presentation.graphql.types import (
    ConversationType,
    DependencyHealthType,
    DomainErrorType,
    HealthType,
    InsuranceConditionOptionType,
    PIIResultType,
)

_DEFAULT_PAGINATION_LIMIT: Final[int] = 20

_INSURANCE_CONDITION_OPTIONS: Final[tuple[InsuranceConditionOptionType, ...]] = (
    InsuranceConditionOptionType(id="p-basic", code="P_BASIC", label="Basic Protection"),
    InsuranceConditionOptionType(id="p-plus", code="P_PLUS", label="Plus Protection"),
    InsuranceConditionOptionType(id="p-premium", code="P_PREMIUM", label="Premium Protection"),
)


@strawberry.type
class Query:
    """Root query type."""

    @strawberry.field
    async def health(self, _info: Info) -> HealthType:
        """Basic health check."""
        settings = get_settings()
        return HealthType(
            status=ServiceStatus.HEALTHY,
            environment=settings.environment.value,
            dependencies=[],
        )

    @strawberry.field
    async def health_ready(self, info: Info) -> HealthType:
        """Deep health check with dependency probes."""
        settings = get_settings()
        deps: list[DependencyHealthType] = []

        # Database probe via context-injected engine
        db_engine = info.context.get("db_engine")
        if db_engine is not None:
            try:
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
        _ = id
        return None

    @strawberry.field
    async def conversations(self, limit: int = _DEFAULT_PAGINATION_LIMIT, offset: int = 0) -> list[ConversationType]:
        """List conversations with pagination."""
        _ = (limit, offset)
        return []

    @strawberry.field
    async def check_pii(self, info: Info, text: str) -> PIIResultType:
        """Check text for PII without modifying it."""
        context = info.context
        anonymizer = None if context is None else context.get("pii_anonymizer")

        settings = get_settings()
        outcome = apply_pii_policy(
            text=text,
            anonymizer=anonymizer,
            settings=PIIPolicySettings(profile=settings.pii_policy_profile),
        )

        if outcome.errors:
            domain_errors = [
                DomainErrorType(
                    code=str(error.code),
                    message=str(error.message),
                )
                for error in outcome.errors
            ]
            return PIIResultType(
                anonymized_text=text,
                pii_found=False,
                match_count=0,
                errors=domain_errors,
            )

        return PIIResultType(
            anonymized_text=outcome.anonymized_text,
            pii_found=outcome.pii_found,
            match_count=outcome.match_count,
        )

    @strawberry.field
    async def insurance_condition_options(self, _info: Info) -> list[InsuranceConditionOptionType]:
        """List insurance condition options available for claim intake selection."""
        return list(_INSURANCE_CONDITION_OPTIONS)
