"""Health-check endpoint."""

from __future__ import annotations

from contextlib import suppress
from typing import TYPE_CHECKING, Final

import duckdb
from fastapi import APIRouter, Request

from ekko.config.settings import get_settings
from ekko.core.enums import QueueName
from ekko.core.registry_constants import ROUTE_HEALTH
from ekko.presentation.api.schemas.responses import HealthResponse

if TYPE_CHECKING:
    from pathlib import Path

router = APIRouter(tags=["health"])

_DUCKDB_ALIAS: Final[str] = "source_sqlite"


def _probe_duckdb_sqlite(*, sqlite_path: Path, duckdb_path: Path) -> tuple[bool, str]:
    """Probe DuckDB by attaching the active SQLite database file."""
    if not sqlite_path.exists():
        return False, "sqlite database file not found"

    escaped_path = str(sqlite_path).replace("'", "''")
    attach_statement = f"ATTACH '{escaped_path}' AS {_DUCKDB_ALIAS} (TYPE sqlite)"
    detach_statement = f"DETACH {_DUCKDB_ALIAS}"

    try:
        with duckdb.connect(database=str(duckdb_path), read_only=False) as conn:
            conn.execute("INSTALL sqlite")
            conn.execute("LOAD sqlite")
            with suppress(duckdb.Error):
                conn.execute(detach_statement)
            conn.execute(attach_statement)
            rows = conn.execute(f"SHOW TABLES FROM {_DUCKDB_ALIAS}").fetchall()
            with suppress(duckdb.Error):
                conn.execute(detach_statement)
            return True, f"attached sqlite with {len(rows)} table(s)"
    except duckdb.Error as exc:
        return False, str(exc)


@router.get(ROUTE_HEALTH, response_model=HealthResponse)
async def health(request: Request) -> HealthResponse:
    """Lightweight health check reporting TCP servers and queue status."""
    state = getattr(request.app, "state", None)
    ok = True
    details: dict[str, object] = {}
    if state is None:
        return HealthResponse(ok=False, details={"reason": "app has no state"})

    details["sys_server_listening"] = bool(getattr(state, "sys_server", None))
    details["mic_server_listening"] = bool(getattr(state, "mic_server", None))
    qm = getattr(state, "queue_manager", None)
    if qm is None:
        details["queue_manager"] = "missing"
        ok = False
    else:
        try:
            details["transcripts_queue_present"] = QueueName.TRANSCRIPTS in qm.queues
        except Exception:
            details["transcripts_queue_present"] = False
            ok = False

    settings = get_settings()
    details["duckdb_enabled"] = settings.duckdb_enabled
    if settings.duckdb_enabled:
        duckdb_ok, duckdb_detail = _probe_duckdb_sqlite(
            sqlite_path=settings.resolved_db_path,
            duckdb_path=settings.resolved_duckdb_path,
        )
        details["duckdb_sqlite_probe"] = {
            "ok": duckdb_ok,
            "detail": duckdb_detail,
        }
        if not duckdb_ok:
            ok = False

    return HealthResponse(ok=ok, details=details)
