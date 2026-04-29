"""JWT authentication port protocol."""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class JWTPort(Protocol):
    """Port for JWT token operations.

    Implementations handle signing, encoding, and decoding of JWT tokens.
    """

    def create_access_token(self, subject: str) -> str:
        """Create a signed JWT access token for the given subject."""
        ...

    def decode_token(self, token: str) -> object | None:
        """Decode and validate a JWT token. Returns None on failure."""
        ...
