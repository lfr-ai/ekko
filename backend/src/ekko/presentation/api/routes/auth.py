"""Authentication endpoints."""

from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends

from ekko.presentation.api.dependencies import get_jwt_adapter
from ekko.presentation.api.schemas.auth import TokenRequest, TokenResponse

if TYPE_CHECKING:
    from ekko.core.interfaces.auth import JWTPort

auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post("/token", response_model=TokenResponse)
async def create_token(
    body: TokenRequest,
    jwt: JWTPort = Depends(get_jwt_adapter),  # noqa: B008
) -> TokenResponse:
    """Issue a JWT access token.

    In production, this would validate credentials against a user store.
    For development, any username/password combination is accepted.
    """
    token = jwt.create_access_token(subject=body.username)
    return TokenResponse(access_token=token, token_type="bearer")
