"""Root GraphQL mutations."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

import strawberry

from ekko.presentation.graphql.types import (
    AnonymizeTextInput,
    ConversationType,
    PIIResultType,
    SendMessageInput,
    StartConversationInput,
    StreamCommandInput,
    StreamStatusType,
)


@strawberry.type
class Mutation:
    """Root mutation type."""

    @strawberry.mutation
    async def control_stream(self, command: StreamCommandInput) -> StreamStatusType:
        """Start or pause the audio stream."""
        if command.action not in {"start", "pause"}:
            return StreamStatusType(active=False, message=f"Unknown action: {command.action}")
        return StreamStatusType(
            active=command.action == "start",
            message=f"Stream {command.action}ed",
        )

    @strawberry.mutation
    async def start_conversation(self, input: StartConversationInput | None = None) -> ConversationType:  # noqa: A002
        """Start a new conversation session."""
        now = datetime.now(UTC)
        return ConversationType(
            id=str(uuid4()),
            started_at=now,
            is_active=True,
        )

    @strawberry.mutation
    async def end_conversation(self, conversation_id: str) -> ConversationType:
        """End an active conversation."""
        now = datetime.now(UTC)
        return ConversationType(
            id=conversation_id,
            started_at=now,  # placeholder
            ended_at=now,
            is_active=False,
        )

    @strawberry.mutation
    async def send_message(self, input: SendMessageInput) -> str:  # noqa: A002
        """Send a message in a conversation."""
        return f"Message received in conversation {input.conversation_id}"

    @strawberry.mutation
    async def anonymize_text(self, input: AnonymizeTextInput) -> PIIResultType:  # noqa: A002
        """Anonymize PII in the given text."""
        from ekko.ai.pii.anonymizer import PIIAnonymizer

        enabled = frozenset(input.enabled_types) if input.enabled_types else None
        anonymizer = PIIAnonymizer(enabled_types=enabled)
        result = anonymizer.anonymize(input.text)
        return PIIResultType(
            anonymized_text=result.anonymized_text,
            pii_found=result.has_pii,
            match_count=len(result.pii_matches),
        )
