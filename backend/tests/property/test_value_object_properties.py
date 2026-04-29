"""Property-based tests for core value objects."""

from hypothesis import given, settings
from hypothesis import strategies as st

from ekko.core.value_objects import (
    AnonymizedText,
    AudioChunk,
    IntentClassification,
    PIIMatch,
    TranscriptSegment,
)


class TestAudioChunkProperties:
    @given(
        data=st.binary(min_size=0, max_size=4096),
        sample_rate=st.sampled_from([8000, 16000, 44100, 48000]),
        channels=st.sampled_from([1, 2]),
    )
    @settings(max_examples=50)
    def test_audio_chunk_construction(self, data: bytes, sample_rate: int, channels: int):
        chunk = AudioChunk(data=data, sample_rate=sample_rate, channels=channels)
        assert chunk.data == data
        assert chunk.sample_rate == sample_rate
        assert chunk.channels == channels


class TestTranscriptSegmentProperties:
    @given(
        text=st.text(min_size=0, max_size=200),
        start=st.floats(min_value=0, max_value=3600),
        confidence=st.floats(min_value=0, max_value=1),
    )
    @settings(max_examples=50)
    def test_segment_construction(self, text: str, start: float, confidence: float):
        seg = TranscriptSegment(text=text, start_seconds=start, confidence=confidence)
        assert seg.text == text
        assert seg.start_seconds == start


class TestAnonymizedTextProperties:
    @given(text=st.text(min_size=0, max_size=200))
    @settings(max_examples=50)
    def test_no_pii_when_no_matches(self, text: str):
        result = AnonymizedText(original_text=text, anonymized_text=text)
        assert not result.has_pii

    @given(text=st.text(min_size=1, max_size=200))
    @settings(max_examples=50)
    def test_has_pii_when_matches_present(self, text: str):
        match = PIIMatch(entity_type="test", start=0, end=1, text="x", score=1.0)
        result = AnonymizedText(original_text=text, anonymized_text=text, pii_matches=(match,))
        assert result.has_pii


class TestIntentClassificationProperties:
    @given(
        intent=st.sampled_from(["question", "request", "greeting", "unknown"]),
        confidence=st.floats(min_value=0, max_value=1),
    )
    @settings(max_examples=50)
    def test_classification_construction(self, intent: str, confidence: float):
        ic = IntentClassification(intent=intent, confidence=confidence)
        assert ic.intent == intent
        assert 0 <= ic.confidence <= 1
