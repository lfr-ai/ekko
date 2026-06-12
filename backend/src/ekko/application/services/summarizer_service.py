"""Summarizer orchestration service."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

from ekko.core.interfaces.services.prompts import PromptProviderError

if TYPE_CHECKING:
    from collections.abc import Iterable

    from ekko.core.interfaces import ChatPort, PromptProvider


logger = logging.getLogger(__name__)
FALLBACK_SUMMARY_TEMPLATE = "Summarize the following content concisely:\n{content}"
PROMPT_KEY_SUMMARY_CHUNKS = "summary_chunks"


@dataclass(slots=True)
class SummarizerService:
    gateway: ChatPort
    prompt_provider: PromptProvider

    def summarize(self, chunks: Iterable[str]) -> str:
        """Summarize a list of text chunks into a single summary.

        Uses the OpenAI gateway to perform summarization. Keeps orchestration
        at application level (chunking, prompt assembly).
        """
        system_prompt = "Summarizer"
        try:
            template = self.prompt_provider.get_prompt_text(PROMPT_KEY_SUMMARY_CHUNKS)
        except PromptProviderError:
            logger.exception("Falling back to built-in summarization prompt template")
            template = FALLBACK_SUMMARY_TEMPLATE

        payload = "\n\n".join(chunks)
        user_prompt = template.replace("{content}", payload)

        return self.gateway.chat(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            model="gpt-4o-mini",
            temperature=0.0,
            max_completion_tokens=512,
        )
