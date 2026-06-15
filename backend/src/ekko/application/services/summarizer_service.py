"""Summarizer orchestration service."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Final, final

from ekko.core.interfaces.services.prompts import PromptProviderError

if TYPE_CHECKING:
    from collections.abc import Iterable

    from ekko.core.interfaces import ChatPort, PromptProvider


logger = logging.getLogger(__name__)
_FALLBACK_SUMMARY_TEMPLATE: Final[str] = "Summarize the following content concisely:\n{content}"
_PROMPT_KEY_SUMMARY_CHUNKS: Final[str] = "summary_chunks"


_DEFAULT_SUMMARIZER_MODEL: Final[str] = "gpt-4o-mini"


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class SummarizerService:
    gateway: ChatPort
    prompt_provider: PromptProvider
    model: str = _DEFAULT_SUMMARIZER_MODEL

    def summarize(self, chunks: Iterable[str]) -> str:
        """Summarize a list of text chunks into a single summary.

        Uses the OpenAI gateway to perform summarization. Keeps orchestration
        at application level (chunking, prompt assembly).
        """
        system_prompt = "Summarizer"
        try:
            template = self.prompt_provider.get_prompt_text(_PROMPT_KEY_SUMMARY_CHUNKS)
        except PromptProviderError:
            logger.exception("Falling back to built-in summarization prompt template")
            template = _FALLBACK_SUMMARY_TEMPLATE

        payload = "\n\n".join(chunks)
        user_prompt = template.replace("{content}", payload)

        return self.gateway.chat(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            model=self.model,
            temperature=0.0,
            max_completion_tokens=512,
        )
