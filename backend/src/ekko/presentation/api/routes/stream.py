"""Audio stream control endpoints."""

from __future__ import annotations

from typing import Final

from fastapi import APIRouter, Request, Response

from ekko.config.settings import get_settings
from ekko.core.registry_constants import ROUTE_PAUSE_STREAM, ROUTE_START_STREAM
from ekko.presentation.api.schemas.responses import StreamResponse

router = APIRouter(tags=["stream"])

_DEPRECATION_HEADER_NAME: Final[str] = "Deprecation"
_DEPRECATION_HEADER_VALUE: Final[str] = "true"
_LINK_HEADER_NAME: Final[str] = "Link"
_LINK_HEADER_VALUE: Final[str] = '</graphql>; rel="successor-version"; title="GraphQL endpoint"'
_WARNING_HEADER_NAME: Final[str] = "Warning"
_WARNING_HEADER_VALUE: Final[str] = '299 - "REST stream endpoints are deprecated; use GraphQL mutation controlStream."'
_SUNSET_HEADER_NAME: Final[str] = "Sunset"
_REMOVAL_TARGET_HEADER_NAME: Final[str] = "X-API-Removal-Target"

_settings = get_settings()


def _set_stream_deprecation_headers(*, response: Response) -> None:
    """Add deprecation metadata headers to legacy REST stream endpoints."""
    response.headers[_DEPRECATION_HEADER_NAME] = _DEPRECATION_HEADER_VALUE
    response.headers[_LINK_HEADER_NAME] = _LINK_HEADER_VALUE
    response.headers[_WARNING_HEADER_NAME] = _WARNING_HEADER_VALUE
    response.headers[_SUNSET_HEADER_NAME] = _settings.rest_stream_deprecation_sunset_rfc3339
    response.headers[_REMOVAL_TARGET_HEADER_NAME] = _settings.rest_stream_removal_target_rfc3339


@router.post(ROUTE_START_STREAM, response_model=StreamResponse, deprecated=True)
async def start_stream(request: Request, response: Response) -> StreamResponse:
    """Start audio streaming."""
    _set_stream_deprecation_headers(response=response)
    await request.app.state.controller.device_check()
    await request.app.state.controller.send_command("start_stream")
    return StreamResponse(status="started")


@router.post(ROUTE_PAUSE_STREAM, response_model=StreamResponse, deprecated=True)
async def pause_stream(request: Request, response: Response) -> StreamResponse:
    """Pause audio streaming."""
    _set_stream_deprecation_headers(response=response)
    await request.app.state.controller.send_command("pause_stream")
    return StreamResponse(status="paused")
