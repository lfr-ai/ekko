"""Pydantic output models for CrewAI tasks."""

from __future__ import annotations

from pydantic import BaseModel, Field


class IntentDetectionOutput(BaseModel):
    """Structured output from the intent detection agent."""

    intent: str = Field(description="Detected intent category")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score")
    entities: dict[str, str] = Field(default_factory=dict, description="Extracted entities")


class ConversationRouteOutput(BaseModel):
    """Structured output from the conversation router agent."""

    strategy: str = Field(description="Selected response strategy")
    reasoning: str = Field(description="Why this strategy was chosen")
    suggested_response_template: str = Field(default="", description="Template for the response")


class ConversationSummaryOutput(BaseModel):
    """Structured output from the summarizer agent."""

    summary: str = Field(description="Conversation summary")
    key_topics: list[str] = Field(default_factory=list, description="Main topics discussed")
    sentiment: str = Field(default="neutral", description="Overall sentiment")
    action_items: list[str] = Field(default_factory=list, description="Action items identified")
    decision_count: int = Field(default=0, description="Number of decisions made")


class TranscriptAnalysisOutput(BaseModel):
    """Structured output from transcript analysis."""

    quality_score: int = Field(ge=1, le=10, description="Quality score")
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    metrics: dict[str, float] = Field(default_factory=dict)
    key_topics: list[str] = Field(default_factory=list)
    sentiment: str = Field(default="neutral")
    action_items: list[str] = Field(default_factory=list)
    follow_up_questions: list[str] = Field(default_factory=list)
    summary: str = Field(default="")


class VoiceResponse(BaseModel):
    """Structured output from voice assistant response."""

    response_text: str = Field(description="The response text")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
