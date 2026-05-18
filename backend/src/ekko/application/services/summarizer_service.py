"""Summarizer orchestration service."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

from ekko.ai.prompts import PROMPT_KEY_SUMMARY_CHUNKS, PromptRegistryError, get_prompt_text
from ekko.config.settings import BaseAppConfig, get_settings

if TYPE_CHECKING:
    from collections.abc import Iterable

    from ekko.core.interfaces import OpenAIGateway


logger = logging.getLogger(__name__)
FALLBACK_SUMMARY_TEMPLATE = "Summarize the following content concisely:\n{content}"


@dataclass(slots=True)
class SummarizerService:
    gateway: OpenAIGateway
    settings: BaseAppConfig | None = None

    def summarize(self, chunks: Iterable[str]) -> str:
        """Summarize a list of text chunks into a single summary.

        Uses the OpenAI gateway to perform summarization. Keeps orchestration
        at application level (chunking, prompt assembly).
        """
        settings = self.settings or get_settings()

        system_prompt = "Summarizer"
        try:
            template = get_prompt_text(PROMPT_KEY_SUMMARY_CHUNKS, settings=settings)
        except PromptRegistryError:
            logger.exception("Falling back to built-in summarization prompt template")
            template = FALLBACK_SUMMARY_TEMPLATE

        payload = "\n\n".join(chunks)
        user_prompt = template.replace("{content}", payload)
        model = settings.rag_llm_model

        return self.gateway.chat(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            model=model,
            temperature=0.0,
            max_completion_tokens=512,
        )
