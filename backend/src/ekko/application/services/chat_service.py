"""Chat orchestration service."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ekko.config.enums import ChatModel

if TYPE_CHECKING:
    from ekko.core.interfaces import ChatPort


@dataclass(slots=True)
class ChatService:
    """Application service for chat-related use-cases.

    Depends only on the ChatPort protocol (in `core`).
    """

    gateway: ChatPort

    def chat(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        model: str = ChatModel.GPT_4O,
        temperature: float = 0.0,
        max_completion_tokens: int = 1024,
    ) -> str:
        """Compose a chat request via the gateway and return assistant text.

        This method contains business orchestration and simple validation only.
        """
        if not user_prompt:
            raise ValueError("user_prompt must not be empty")

        return self.gateway.chat(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            model=model,
            temperature=temperature,
            max_completion_tokens=max_completion_tokens,
        )
