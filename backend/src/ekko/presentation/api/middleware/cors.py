"""CORS configuration."""

from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi.middleware.cors import CORSMiddleware

if TYPE_CHECKING:
    from fastapi import FastAPI

    from ekko.config.settings.base import BaseAppConfig

_LOCAL_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
]


def setup_cors(app: FastAPI, *, settings: BaseAppConfig) -> None:
    """Add CORS middleware allowing localhost origins (local-only app)."""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=_LOCAL_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
    )
