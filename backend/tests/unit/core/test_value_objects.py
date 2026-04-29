"""Tests for core value objects."""

from ekko.core.value_objects import (
    AnonymizedText,
    AudioChunk,
    ConversationSummary,
    IntentClassification,
    PIIMatch,
    TranscriptSegment,
)


class TestAudioChunk:
    def test_default(self):
        chunk = AudioChunk()
        assert chunk.data == b""
        assert chunk.sample_rate == 48000
        assert chunk.channels == 2

    def test_with_data(self):
        chunk = AudioChunk(data=b"\x00\x01", source="microphone")
        assert len(chunk.data) == 2
        assert chunk.source == "microphone"


class TestTranscriptSegment:
    def test_default(self):
        seg = TranscriptSegment()
        assert seg.text == ""
        assert seg.confidence == 0.0

    def test_with_timing(self):
        seg = TranscriptSegment(text="hello", start_seconds=1.0, end_seconds=2.5, confidence=0.95)
        assert seg.end_seconds - seg.start_seconds == 1.5


class TestPIIMatch:
    def test_frozen(self):
        match = PIIMatch(entity_type="email", start=0, end=5, text="x@y.z", score=1.0)
        assert match.entity_type == "email"


class TestAnonymizedText:
    def test_no_pii(self):
        result = AnonymizedText(original_text="hello", anonymized_text="hello")
        assert not result.has_pii

    def test_with_pii(self):
        match = PIIMatch(entity_type="email", start=0, end=10, text="a@b.com", score=1.0)
        result = AnonymizedText(
            original_text="a@b.com test",
            anonymized_text="[REDACTED] test",
            pii_matches=(match,),
        )
        assert result.has_pii
        assert len(result.pii_matches) == 1


class TestConversationSummary:
    def test_default(self):
        summary = ConversationSummary()
        assert summary.sentiment == "neutral"
        assert summary.key_topics == ()

    def test_with_data(self):
        summary = ConversationSummary(
            text="Discussion about pensions",
            key_topics=("pensions", "retirement"),
            action_items=("Follow up on plan details",),
        )
        assert len(summary.key_topics) == 2


class TestIntentClassification:
    def test_default(self):
        intent = IntentClassification()
        assert intent.intent == "unknown"
        assert intent.confidence == 0.0

    def test_with_data(self):
        intent = IntentClassification(intent="question", confidence=0.95, entities={"topic": "pension"})
        assert intent.entities["topic"] == "pension"
