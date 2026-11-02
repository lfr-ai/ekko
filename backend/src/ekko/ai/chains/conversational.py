"""Conversational chain for RAG-powered dialogue."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ekko.core.ports import ChatPort
    from ekko.core.types import ModelDeploymentName

from ekko.ai.prompts import get_prompt_text
from ekko.core.enums import MessageRole, Prompt
from ekko.core.registry_constants import FIELD_CONTENT, FIELD_ROLE

_DEFAULT_MODEL = "gpt-4o"
_MAX_HISTORY = 20
_EMPTY_CONTEXT = "No prior conversation."


@dataclass(kw_only=True, slots=True)
class ConversationalChain:
    """Simple conversational chain with context injection.

    Maintains a conversation history and injects relevant context
    into the system prompt for each turn.
    """

    chat_client: ChatPort
    default_model: ModelDeploymentName = _DEFAULT_MODEL
    history: list[dict[str, str]] = field(default_factory=list)
    max_history: int = _MAX_HISTORY

    async def run(self, user_message: str) -> str:
        """Process a user message and return the assistant's response."""
        self.history.append({FIELD_ROLE: MessageRole.USER, FIELD_CONTENT: user_message})

        context = self._build_context()
        template = get_prompt_text(Prompt.CONVERSATIONAL_SYSTEM)
        system_prompt = template.format(context=context)

        response = await self.chat_client.achat(
            system_prompt=system_prompt,
            user_prompt=user_message,
            model=self.default_model,
        )

        self.history.append({FIELD_ROLE: MessageRole.ASSISTANT, FIELD_CONTENT: response})
        return response

    def _build_context(self) -> str:
        """Build conversation context from recent history."""
        if not self.history:
            return _EMPTY_CONTEXT
        recent = self.history[-self.max_history :]
        lines = [f"{msg[FIELD_ROLE]}: {msg[FIELD_CONTENT]}" for msg in recent]
        return "\n".join(lines)

    def clear_history(self) -> None:
        """Clear conversation history."""
        self.history.clear()
