"""PII scrubbing tool for CrewAI agents."""

from __future__ import annotations

from crewai.tools import BaseTool

from ekko.ai.pii.anonymizer import PIIAnonymizer


class PIIScrubTool(BaseTool):
    """Tool that scrubs PII from text before processing."""

    name: str = "pii_scrub"
    description: str = (
        "Remove personally identifiable information (PII) from text. Use before processing sensitive content."
    )

    def _run(self, text: str) -> str:
        anonymizer = PIIAnonymizer()
        result = anonymizer.anonymize(text)
        return result.anonymized_text
