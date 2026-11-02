"""Repository port protocols for persistence abstractions.

These protocols define the contracts that infrastructure persistence adapters
must fulfill. They are declared ahead of their adapters: the persistence
vertical (conversation/message/transcript storage) is intentionally deferred,
so these are forward contracts rather than dead code. Implement adapters under
``infrastructure/db/`` and wire them through ``composition.Container`` when the
persistence feature lands.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from collections.abc import Sequence
    from uuid import UUID

    from ekko.core.entities import Conversation, Message, Transcript


class ConversationRepositoryPort(Protocol):
    """Port for conversation persistence."""

    async def get_by_id(self, conversation_id: UUID) -> Conversation | None:
        """Load a conversation by identifier."""
        ...

    async def save(self, conversation: Conversation) -> None:
        """Persist a conversation."""
        ...

    async def list_recent(self, *, limit: int = 20) -> Sequence[Conversation]:
        """List the most recent conversations."""
        ...


class MessageRepositoryPort(Protocol):
    """Port for message persistence."""

    async def get_by_conversation(self, conversation_id: UUID) -> Sequence[Message]:
        """List messages belonging to a conversation."""
        ...

    async def save(self, message: Message) -> None:
        """Persist a message."""
        ...


class TranscriptRepositoryPort(Protocol):
    """Port for transcript persistence."""

    async def get_by_conversation(self, conversation_id: UUID) -> Sequence[Transcript]:
        """List transcripts belonging to a conversation."""
        ...

    async def save(self, transcript: Transcript) -> None:
        """Persist a transcript."""
        ...
