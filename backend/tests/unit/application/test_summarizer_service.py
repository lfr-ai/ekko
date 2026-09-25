"""Unit tests for the summarizer application service."""

import pytest

from ekko.application.services.summarizer_service import SummarizerService
from ekko.core.exceptions import PIIPolicyViolationError
from ekko.core.policies.pii_policy import PIIPolicyError, PIIPolicyOutcome

try:
    from ekko.core.ports import PromptRegistryError
except ImportError:
    from ekko.core.ports.external.prompt_registry import PromptRegistryError


class DummyGateway:
    """LLM gateway test double returning a prompt-derived summary."""

    def chat(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        model: str,
        temperature: float,
        max_completion_tokens: int,
    ) -> str:
        """Summarize the beginning of the submitted user prompt."""
        _ = (system_prompt, model, temperature, max_completion_tokens)
        return "summary:" + user_prompt[:20]


class DummyPromptRegistryPort:
    """Prompt registry test double returning configured text."""

    def __init__(self, text: str = "Summarize:\n{content}"):
        self._text = text

    def load_prompt(self, prompt_key: str) -> str:
        """Load the configured prompt text."""
        _ = prompt_key
        return self._text


class FailingPromptRegistryPort:
    """Prompt registry test double that simulates a missing prompt."""

    def load_prompt(self, prompt_key: str) -> str:
        """Raise a prompt registry lookup error."""
        _ = prompt_key
        msg = "not found"
        raise PromptRegistryError(msg)


class PassthroughPIIService:
    """Chunk-preserving PII service test double."""

    def anonymize(self, text: str) -> PIIPolicyOutcome:
        """Preserve the supplied text unchanged."""
        return PIIPolicyOutcome(anonymized_text=text, pii_found=False, match_count=0)


class RedactingPIIService:
    """Replaces every chunk with a fixed redacted marker."""

    def anonymize(self, text: str) -> PIIPolicyOutcome:
        """Replace the supplied text with a marker."""
        _ = text
        return PIIPolicyOutcome(anonymized_text="[REDACTED]", pii_found=True, match_count=1)


class BlockingPIIService:
    """Fails the PII policy for every chunk (e.g. strict mode, no anonymizer)."""

    def anonymize(self, text: str) -> PIIPolicyOutcome:
        """Produce a blocking PII policy outcome."""
        _ = text
        return PIIPolicyOutcome(
            anonymized_text="",
            pii_found=False,
            match_count=0,
            errors=(PIIPolicyError(code="PII_POLICY_VIOLATION", message="blocked"),),
        )


@pytest.mark.unit
def test_summarizer_basic() -> None:
    """Summarize chunks with the default test doubles."""
    svc = SummarizerService(
        gateway=DummyGateway(),
        prompt_registry=DummyPromptRegistryPort(),
        pii_service=PassthroughPIIService(),
    )
    chunks = ["This is a first chunk.", "Second chunk with more details."]
    s = svc.summarize(chunks)
    assert s.startswith("summary:")


@pytest.mark.unit
def test_summarizer_file_not_found_uses_fallback() -> None:
    """Missing prompt lookup falls back to the default template."""
    gateway = DummyGateway()
    svc = SummarizerService(
        gateway=gateway,
        prompt_registry=FailingPromptRegistryPort(),
        pii_service=PassthroughPIIService(),
    )
    chunks = ["Test chunk"]

    result = svc.summarize(chunks)

    assert result.startswith("summary:")


@pytest.mark.unit
def test_summarizer_sends_anonymized_text_to_gateway() -> None:
    """PII service output is sent to the gateway instead of raw text."""
    svc = SummarizerService(
        gateway=DummyGateway(),
        prompt_registry=DummyPromptRegistryPort(),
        pii_service=RedactingPIIService(),
    )

    result = svc.summarize(["Ring mig på 12345678"])

    assert "12345678" not in result
    assert "[REDACT" in result


@pytest.mark.unit
def test_summarizer_raises_on_pii_policy_violation() -> None:
    """Blocking PII policy outcomes raise an application error."""
    svc = SummarizerService(
        gateway=DummyGateway(),
        prompt_registry=DummyPromptRegistryPort(),
        pii_service=BlockingPIIService(),
    )

    with pytest.raises(PIIPolicyViolationError):
        svc.summarize(["Some text"])
