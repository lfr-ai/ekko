"""Health-check endpoint."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response, status

from ekko.application.services import ReadinessService
from ekko.config.runtime import get_config
from ekko.core.enums import ServiceStatus
from ekko.core.registry_constants import ROUTE_HEALTH, ROUTE_READY
from ekko.presentation.api.dependencies import get_readiness_service
from ekko.presentation.api.schemas.health import DependencyHealth, ReadinessResponse
from ekko.presentation.api.schemas.responses import HealthResponse

_HEALTH_TAG = "health"

router = APIRouter(tags=[_HEALTH_TAG])

type ReadinessServiceDependency = Annotated[
    ReadinessService,
    Depends(get_readiness_service),
]


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
    settings = get_config()
    details["sqlite_database_present"] = settings.resolved_db_path.exists()
    if not details["sqlite_database_present"]:
        ok = False

    return HealthResponse(ok=ok, details=details)


@router.get(
    ROUTE_READY,
    response_model=ReadinessResponse,
    responses={status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ReadinessResponse}},
)
async def ready(response: Response, service: ReadinessServiceDependency) -> ReadinessResponse:
    """Check external dependency readiness."""
    database = await service.check_database()
    redis = await service.check_redis()
    dependencies = [
        DependencyHealth(name=database.name, healthy=database.healthy, detail=database.detail),
        DependencyHealth(name=redis.name, healthy=redis.healthy, detail=redis.detail),
    ]
    all_healthy = database.healthy and redis.healthy
    readiness_status = ServiceStatus.HEALTHY if all_healthy else ServiceStatus.DEGRADED
    if not all_healthy:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return ReadinessResponse(status=readiness_status, dependencies=dependencies)
