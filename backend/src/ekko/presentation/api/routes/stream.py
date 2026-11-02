"""Audio stream control endpoints."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from ekko.core.ports import AudioStreamerControllerPort
from ekko.core.registry_constants import ROUTE_PAUSE_STREAM, ROUTE_START_STREAM
from ekko.presentation.api.dependencies import get_stream_controller
from ekko.presentation.api.schemas.responses import StreamResponse

_STREAM_TAG = "stream"

router = APIRouter(tags=[_STREAM_TAG])

type StreamControllerDependency = Annotated[
    AudioStreamerControllerPort,
    Depends(get_stream_controller),
]


@router.post(ROUTE_START_STREAM, response_model=StreamResponse)
async def start_stream(controller: StreamControllerDependency) -> StreamResponse:
    """Start audio streaming."""
    await controller.device_check()
    await controller.send_command("start_stream")
    return StreamResponse(status="started")


@router.post(ROUTE_PAUSE_STREAM, response_model=StreamResponse)
async def pause_stream(controller: StreamControllerDependency) -> StreamResponse:
    """Pause audio streaming."""
    await controller.send_command("pause_stream")
    return StreamResponse(status="paused")
