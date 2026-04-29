"""Application-layer command/query handlers."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from ekko.application.dtos import ConversationDTO

if TYPE_CHECKING:
    from ekko.application.dtos import SendMessageDTO, StartConversationDTO

logger = logging.getLogger(__name__)


class StartConversationHandler:
    """Handle the start-conversation command."""

    async def execute(self, dto: StartConversationDTO) -> ConversationDTO:  # noqa: ARG002
        now = datetime.now(UTC)
        return ConversationDTO(
            id=str(uuid4()),
            started_at=now,
            is_active=True,
        )


class SendMessageHandler:
    """Handle sending a message to an active conversation."""

    async def execute(self, dto: SendMessageDTO) -> str:
        logger.info("Processing message for conversation %s", dto.conversation_id)
        return f"Acknowledged message in conversation {dto.conversation_id}"
