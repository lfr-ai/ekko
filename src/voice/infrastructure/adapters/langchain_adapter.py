"""Thin shim re-exporting the canonical LangChain chat adapter.

This module preserves the historical import path for code that expected a
``LangChainOpenAIAdapter`` class while delegating the implementation to the
single canonical adapter located under ``infrastructure.llm.chat_adapter``.
"""

from __future__ import annotations

from voice.infrastructure.llm.chat_adapter import ChatModelAdapter


# Provide the historical name for backwards compatibility
LangChainOpenAIAdapter = ChatModelAdapter

__all__ = ["LangChainOpenAIAdapter", "ChatModelAdapter"]
