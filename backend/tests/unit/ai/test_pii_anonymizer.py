"""Tests for PII anonymizer."""

from ekko.ai.pii.anonymizer import PIIAnonymizer
from ekko.ai.pii.patterns import PII_PATTERNS


class TestPIIAnonymizer:
    def test_detects_danish_cpr(self):
        anonymizer = PIIAnonymizer()
        result = anonymizer.anonymize("Mit CPR er 010190-1234")
        assert result.has_pii
        assert "[CPR-REDACTED]" in result.anonymized_text
        assert any(m.entity_type == "cpr" for m in result.pii_matches)

    def test_detects_email(self):
        anonymizer = PIIAnonymizer()
        result = anonymizer.anonymize("Send til test@example.com")
        assert result.has_pii
        assert "[EMAIL-REDACTED]" in result.anonymized_text

    def test_detects_phone(self):
        anonymizer = PIIAnonymizer()
        result = anonymizer.anonymize("Ring på +45 12 34 56 78")
        assert result.has_pii
        assert "[PHONE-REDACTED]" in result.anonymized_text

    def test_no_pii_in_clean_text(self):
        anonymizer = PIIAnonymizer()
        text = "Hej, hvordan har du det?"
        result = anonymizer.anonymize(text)
        assert not result.has_pii
        assert result.anonymized_text == text

    def test_preserves_non_pii_content(self):
        anonymizer = PIIAnonymizer()
        result = anonymizer.anonymize("Kontakt os på test@example.com for mere info")
        assert "Kontakt os på" in result.anonymized_text
        assert "for mere info" in result.anonymized_text

    def test_enabled_types_filter(self):
        anonymizer = PIIAnonymizer(enabled_types=frozenset({"email"}))
        result = anonymizer.anonymize("CPR: 010190-1234, email: test@example.com")
        # Only email should be redacted
        assert "[EMAIL-REDACTED]" in result.anonymized_text
        # CPR should remain (since only email is enabled)
        assert "010190" in result.anonymized_text

    def test_contains_pii_quick_check(self):
        anonymizer = PIIAnonymizer()
        assert anonymizer.contains_pii("test@example.com")
        assert not anonymizer.contains_pii("Hello world")

    def test_multiple_pii_in_same_text(self):
        anonymizer = PIIAnonymizer()
        text = "CPR: 010190-1234, email: test@example.com"
        result = anonymizer.anonymize(text)
        assert len(result.pii_matches) >= 2

    def test_patterns_are_compiled(self):
        for pattern in PII_PATTERNS:
            assert pattern.name
            assert pattern.pattern
            assert pattern.replacement
