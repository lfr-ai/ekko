"""API rate-limiting configuration."""

from typing import Final

from slowapi import Limiter
from slowapi.util import get_remote_address

RATE_LIMIT_DEFAULT: Final[str] = "30/second"

limiter = Limiter(key_func=get_remote_address)
