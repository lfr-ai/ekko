"""Presentation layer (API adapters, FastAPI app).

Presentation contains transport-layer adapters such as FastAPI routers and
CLI entrypoints. This layer should depend on ``application`` only and
translate external input/output to application-level DTOs.
"""

__all__: list[str] = []
