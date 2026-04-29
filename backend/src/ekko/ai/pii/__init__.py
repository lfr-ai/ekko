"""PII anonymization module for Ekko.

Scrubs personally identifiable information before sending data to LLM/HMAS.
Supports Danish PII patterns (CPR numbers, phone numbers) plus common patterns.
"""

from ekko.ai.pii.anonymizer import PIIAnonymizer
from ekko.ai.pii.patterns import PII_PATTERNS

__all__ = ["PII_PATTERNS", "PIIAnonymizer"]
