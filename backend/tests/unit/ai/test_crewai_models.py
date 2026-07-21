"""Tests for CrewAI Pydantic output models."""

from ekko.ai.crewai.models import (
    ConversationRouteOutput,
    ConversationSummaryOutput,
    IntentDetectionOutput,
    TranscriptAnalysisOutput,
    VoiceResponse,
)


class TestIntentDetectionOutput:
    def test_valid(self):
        output = IntentDetectionOutput(intent="question", confidence=0.9, entities={"topic": "pension"})
        assert output.intent == "question"
        assert output.confidence == 0.9

    def test_default_entities(self):
        output = IntentDetectionOutput(intent="greeting", confidence=0.8)
        assert output.entities == {}


class TestConversationRouteOutput:
    def test_valid(self):
        output = ConversationRouteOutput(strategy="direct_answer", reasoning="High confidence question")
        assert output.strategy == "direct_answer"


class TestConversationSummaryOutput:
    def test_valid(self):
        output = ConversationSummaryOutput(
            summary="Discussed pensions",
            key_topics=["pension", "retirement"],
            sentiment="positive",
            action_items=["Follow up"],
            decision_count=1,
        )
        assert len(output.key_topics) == 2
        assert output.decision_count == 1


class TestTranscriptAnalysisOutput:
    def test_valid(self):
        output = TranscriptAnalysisOutput(quality_score=8, strengths=["clear"], weaknesses=["slow"])
        assert output.quality_score == 8

    def test_defaults(self):
        output = TranscriptAnalysisOutput(quality_score=5)
        assert output.sentiment == "neutral"
        assert output.summary == ""


class TestVoiceResponse:
    def test_valid(self):
        output = VoiceResponse(response_text="Hello, how can I help?")
        assert output.confidence == 1.0
