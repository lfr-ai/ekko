"""Summarizer orchestration service."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol, final

from ekko.core.enums import Prompt
from ekko.core.exceptions import PIIPolicyViolationError
from ekko.core.ports.external.prompt_registry import PromptRegistryError
from ekko.core.types import MaxTokens, ModelDeploymentName, Temperature

if TYPE_CHECKING:
    from collections.abc import Iterable

    from ekko.core.policies.pii_policy import PIIPolicyOutcome
    from ekko.core.ports import ChatPort, PromptRegistryPort


_logger = logging.getLogger(__name__)
_FALLBACK_SUMMARY_TEMPLATE = "Summarize the following content concisely:\n{content}"
_SUMMARIZER_SYSTEM_PROMPT = "Summarizer"

_DEFAULT_SUMMARIZER_MODEL = "gpt-4o-mini"
_SUMMARIZER_MAX_TOKENS = MaxTokens(512)
_SUMMARIZER_TEMPERATURE = Temperature(0.0)


class _PIITextPolicy(Protocol):
    """Structural dependency: anonymize one text payload per the PII policy."""

    def anonymize(self, text: str) -> PIIPolicyOutcome:
        """Apply the configured PII policy to *text*."""
        ...


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class SummarizerService:
    """Orchestrates multi-chunk summarization via the prompt registry."""

    gateway: ChatPort
    prompt_registry: PromptRegistryPort
    pii_service: _PIITextPolicy
    model: ModelDeploymentName = _DEFAULT_SUMMARIZER_MODEL

    def summarize(self, chunks: Iterable[str]) -> str:
        """Summarize a list of text chunks into a single summary.

        Every chunk is passed through the PII policy first; raw text never
        reaches the ChatPort gateway. Keeps orchestration at application
        level (PII enforcement, chunking, prompt assembly).

        Args:
            chunks (Iterable[str]): Transcript or other text chunks to summarize.

        Returns:
            str: Combined summary of the anonymized chunks.
        """
        materialized_chunks = tuple(chunks)
        safe_chunks = tuple(self._anonymize(chunk) for chunk in materialized_chunks)

        system_prompt = _SUMMARIZER_SYSTEM_PROMPT
        try:
            template = self.prompt_registry.load_prompt(Prompt.SUMMARY_CHUNKS)
        except PromptRegistryError as exc:
            _logger.warning(
                "Summary prompt unavailable; using fallback",
                extra={"prompt_key": Prompt.SUMMARY_CHUNKS, "error": str(exc)},
            )
            template = _FALLBACK_SUMMARY_TEMPLATE

        payload = "\n\n".join(safe_chunks)
        user_prompt = template.replace("{content}", payload)

        summary = self.gateway.chat(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            model=self.model,
            temperature=_SUMMARIZER_TEMPERATURE,
            max_completion_tokens=_SUMMARIZER_MAX_TOKENS,
        )
        _logger.info(
            "Summarization completed",
            extra={"chunk_count": len(materialized_chunks), "summary_length": len(summary)},
        )
        return summary

    def _anonymize(self, chunk: str) -> str:
        """Apply the PII policy to one chunk, failing closed on policy errors."""
        outcome = self.pii_service.anonymize(chunk)
        if outcome.errors:
            message = "; ".join(error.message for error in outcome.errors)
            raise PIIPolicyViolationError(message)
        return outcome.anonymized_text
