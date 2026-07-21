"""Repository port protocols for persistence abstractions.

These protocols define the contracts that infrastructure persistence
adapters must fulfill.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from collections.abc import Sequence
    from uuid import UUID

    from ekko.core.entities import Conversation, Message, Transcript


class ConversationRepositoryPort(Protocol):
    """Port for conversation persistence."""

    async def get_by_id(self, conversation_id: UUID) -> Conversation | None: ...

    async def save(self, conversation: Conversation) -> None: ...

    async def list_recent(self, *, limit: int = 20) -> Sequence[Conversation]: ...


class MessageRepositoryPort(Protocol):
    """Port for message persistence."""

    async def get_by_conversation(self, conversation_id: UUID) -> Sequence[Message]: ...

    async def save(self, message: Message) -> None: ...


class TranscriptRepositoryPort(Protocol):
    """Port for transcript persistence."""

    async def get_by_conversation(self, conversation_id: UUID) -> Sequence[Transcript]: ...

    async def save(self, transcript: Transcript) -> None: ...
