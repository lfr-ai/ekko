"""Conversational chain for RAG-powered dialogue."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ekko.ai.llm.adapter import LLMAdapter

from ekko.ai.prompts.templates import CONVERSATIONAL_SYSTEM
from ekko.core.enums import MessageRole

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class ConversationalChain:
    """Simple conversational chain with context injection.

    Maintains a conversation history and injects relevant context
    into the system prompt for each turn.
    """

    llm: LLMAdapter
    history: list[dict[str, str]] = field(default_factory=list)
    max_history: int = 20

    def _build_context(self) -> str:
        if not self.history:
            return "No prior conversation."
        recent = self.history[-self.max_history :]
        lines = [f"{msg['role']}: {msg['content']}" for msg in recent]
        return "\n".join(lines)

    async def run(self, user_message: str) -> str:
        """Process a user message and return the assistant's response."""
        self.history.append({"role": MessageRole.USER, "content": user_message})

        context = self._build_context()
        system_prompt = CONVERSATIONAL_SYSTEM.format(context=context)

        response = await self.llm.async_chat(
            system_prompt=system_prompt,
            user_prompt=user_message,
        )

        self.history.append({"role": MessageRole.ASSISTANT, "content": response})
        return response

    def clear_history(self) -> None:
        """Clear conversation history."""
        self.history.clear()
