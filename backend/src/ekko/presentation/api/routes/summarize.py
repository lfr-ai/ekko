"""Transcript summarization endpoint."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from ekko.application.services.summarizer_service import SummarizerService
from ekko.core.registry_constants import ROUTE_SUMMARIZE
from ekko.presentation.api.dependencies import get_summarizer_service
from ekko.presentation.api.schemas.summarize import SummarizeRequest, SummarizeResponse

_SUMMARIZE_TAG = "summarize"

router = APIRouter(tags=[_SUMMARIZE_TAG])

type SummarizerServiceDependency = Annotated[SummarizerService, Depends(get_summarizer_service)]


# Sync def: the LLM call is blocking I/O, so FastAPI runs this in its threadpool
# instead of blocking the event loop.
@router.post(ROUTE_SUMMARIZE, response_model=SummarizeResponse)
def summarize(request: SummarizeRequest, service: SummarizerServiceDependency) -> SummarizeResponse:
    """Summarize submitted transcript chunks.

    Every chunk passes through the PII policy before reaching the LLM gateway;
    a policy violation surfaces as a domain error (HTTP 422).

    Args:
        request (SummarizeRequest): Submitted transcript chunks.
        service (SummarizerServiceDependency): Application summarizer.

    Returns:
        SummarizeResponse: Summary of the anonymized transcript chunks.
    """
    summary = service.summarize(request.chunks)
    return SummarizeResponse(summary=summary)
