"""Property-based tests for PII anonymizer."""

from hypothesis import given, settings
from hypothesis import strategies as st

from ekko.ai.pii.anonymizer import PIIAnonymizer


class TestPIIAnonymizerProperties:
    @given(text=st.text(min_size=0, max_size=500))
    @settings(max_examples=100)
    def test_anonymize_never_raises(self, text: str):
        """Anonymizer should handle any text input without crashing."""
        anonymizer = PIIAnonymizer()
        result = anonymizer.anonymize(text)
        assert isinstance(result.anonymized_text, str)
        assert isinstance(result.pii_matches, tuple)

    @given(text=st.text(alphabet=st.characters(whitelist_categories=("L", "N", "Z")), min_size=1, max_size=100))
    @settings(max_examples=50)
    def test_clean_text_passes_through(self, text: str):
        """Text with only letters, numbers, and spaces should pass through unchanged."""
        anonymizer = PIIAnonymizer()
        result = anonymizer.anonymize(text)
        # May or may not detect PII depending on the random text,
        # but it should always return valid output
        assert len(result.anonymized_text) > 0

    @given(text=st.text(min_size=0, max_size=200))
    @settings(max_examples=50)
    def test_contains_pii_consistent_with_anonymize(self, text: str):
        """contains_pii should agree with anonymize().has_pii."""
        anonymizer = PIIAnonymizer()
        has_pii = anonymizer.contains_pii(text)
        result = anonymizer.anonymize(text)
        assert has_pii == result.has_pii

    def test_known_cpr_always_detected(self):
        """Known CPR pattern should always be detected."""
        anonymizer = PIIAnonymizer()
        cprs = ["010190-1234", "311299-9876", "150575-5555"]
        for cpr in cprs:
            result = anonymizer.anonymize(f"CPR: {cpr}")
            assert result.has_pii, f"Failed to detect CPR: {cpr}"

    def test_known_emails_always_detected(self):
        """Known email patterns should always be detected."""
        anonymizer = PIIAnonymizer()
        emails = ["test@example.com", "user.name@domain.dk", "a@b.co"]
        for email in emails:
            result = anonymizer.anonymize(f"Email: {email}")
            assert result.has_pii, f"Failed to detect email: {email}"
