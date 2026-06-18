"""Root GraphQL queries."""

from __future__ import annotations

import asyncio
from contextlib import suppress
from typing import Final

import duckdb
import strawberry
from sqlalchemy import text
from strawberry.types import Info

from ekko.config.settings import get_settings
from ekko.core.enums import ServiceStatus
from ekko.presentation.graphql.types import (
    ConversationType,
    DependencyHealthType,
    HealthType,
    PIIResultType,
)

_DUCKDB_ALIAS: Final[str] = "source_sqlite"


def _probe_duckdb_sqlite(*, sqlite_path: str, duckdb_path: str) -> tuple[bool, str]:
    """Probe DuckDB by attaching the configured SQLite file."""
    escaped_path = sqlite_path.replace("'", "''")
    attach_statement = f"ATTACH '{escaped_path}' AS {_DUCKDB_ALIAS} (TYPE sqlite)"
    detach_statement = f"DETACH {_DUCKDB_ALIAS}"

    try:
        with duckdb.connect(database=duckdb_path, read_only=False) as conn:
            conn.execute("INSTALL sqlite")
            conn.execute("LOAD sqlite")
            with suppress(duckdb.Error):
                conn.execute(detach_statement)
            conn.execute(attach_statement)
            conn.execute(f"SHOW TABLES FROM {_DUCKDB_ALIAS}")
            with suppress(duckdb.Error):
                conn.execute(detach_statement)
            return True, "duckdb sqlite attach successful"
    except duckdb.Error as exc:
        return False, str(exc)


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

        if settings.duckdb_enabled:
            duckdb_ok, duckdb_detail = await asyncio.to_thread(
                _probe_duckdb_sqlite,
                sqlite_path=str(settings.resolved_db_path),
                duckdb_path=str(settings.resolved_duckdb_path),
            )
            deps.append(DependencyHealthType(name="duckdb", healthy=duckdb_ok, detail=duckdb_detail))

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
    async def conversations(self, limit: int = 20, offset: int = 0) -> list[ConversationType]:
        """List conversations with pagination."""
        _ = (limit, offset)
        return []

    @strawberry.field
    async def check_pii(self, info: Info, text: str) -> PIIResultType:
        """Check text for PII without modifying it."""
        anonymizer = info.context["pii_anonymizer"]
        result = anonymizer.anonymize(text)
        return PIIResultType(
            anonymized_text=result.anonymized_text,
            pii_found=result.has_pii,
            match_count=len(result.pii_matches),
        )
