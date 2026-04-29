"""JWT authentication adapter."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Final

import jwt

logger = logging.getLogger(__name__)

ALGORITHM: Final[str] = "HS256"
_DEFAULT_EXPIRE_MINUTES: Final[int] = 30


@dataclass(frozen=True, slots=True)
class TokenPayload:
    """Decoded JWT token payload."""

    sub: str
    exp: datetime


class JWTAdapter:
    """JWT token generation and verification."""

    def __init__(self, *, secret_key: str, expire_minutes: int = _DEFAULT_EXPIRE_MINUTES) -> None:
        self._secret_key = secret_key
        self._expire_minutes = expire_minutes

    def create_access_token(self, subject: str) -> str:
        """Create a signed JWT access token."""
        expire = datetime.now(UTC) + timedelta(minutes=self._expire_minutes)
        payload = {"sub": subject, "exp": expire}
        return jwt.encode(payload, self._secret_key, algorithm=ALGORITHM)

    def decode_token(self, token: str) -> TokenPayload | None:
        """Decode and validate a JWT token. Returns None on failure."""
        try:
            data = jwt.decode(token, self._secret_key, algorithms=[ALGORITHM])
            return TokenPayload(
                sub=data["sub"],
                exp=datetime.fromtimestamp(data["exp"], tz=UTC),
            )
        except jwt.PyJWTError:
            logger.warning("Failed to decode JWT token")
            return None
