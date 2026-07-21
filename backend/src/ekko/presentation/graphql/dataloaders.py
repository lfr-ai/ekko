"""DataLoader factories for N+1 prevention in GraphQL resolvers."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


async def load_conversations(keys: list[str]) -> list[Any]:
    """Batch load conversations by ID.

    This is a placeholder — wire to actual repository when persistence is ready.
    """
    logger.debug("Batch loading %d conversations", len(keys))
    return [None] * len(keys)


async def load_transcripts(keys: list[str]) -> list[Any]:
    """Batch load transcripts by conversation ID."""
    logger.debug("Batch loading transcripts for %d conversations", len(keys))
    return [[] for _ in keys]


def create_dataloaders() -> dict[str, Any]:
    """Create DataLoader instances for a single request."""
    from strawberry.dataloader import DataLoader

    return {
        "conversation_loader": DataLoader(load_fn=load_conversations),
        "transcript_loader": DataLoader(load_fn=load_transcripts),
    }
