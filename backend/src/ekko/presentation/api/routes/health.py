"""Health-check endpoint."""

from __future__ import annotations

from fastapi import APIRouter, Request

from ekko.core.enums import QueueName

router = APIRouter(tags=["health"])


@router.get("/health")
async def health(request: Request) -> dict:
    """Lightweight health check reporting TCP servers and queue status."""
    state = getattr(request.app, "state", None)
    ok = True
    details: dict = {}
    if state is None:
        return {"ok": False, "reason": "app has no state"}

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

    return {"ok": ok, "details": details}
