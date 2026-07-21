"""Conversation summary value object."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ConversationSummary:
    """Summary of a conversation produced by the summarizer agent."""

    text: str = ""
    key_topics: tuple[str, ...] = ()
    sentiment: str = "neutral"
    action_items: tuple[str, ...] = ()
