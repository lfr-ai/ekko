"""PII anonymization endpoint."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from ekko.application.services import PIIService
from ekko.core.registry_constants import ROUTE_PII_ANONYMIZE
from ekko.presentation.api.dependencies import get_pii_service
from ekko.presentation.api.schemas.pii import PIIAnonymizeRequest, PIIAnonymizeResponse

_PII_TAG = "pii"

router = APIRouter(tags=[_PII_TAG])

type PIIServiceDependency = Annotated[PIIService, Depends(get_pii_service)]


@router.post(ROUTE_PII_ANONYMIZE, response_model=PIIAnonymizeResponse)
async def anonymize_pii(request: PIIAnonymizeRequest, service: PIIServiceDependency) -> PIIAnonymizeResponse:
    """Anonymize PII in submitted text."""
    outcome = service.anonymize(request.text)
    if outcome.errors:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=outcome.errors[0].message,
        )

    return PIIAnonymizeResponse(
        anonymized_text=outcome.anonymized_text,
        pii_found=outcome.pii_found,
        match_count=outcome.match_count,
    )
