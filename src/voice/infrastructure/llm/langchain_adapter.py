"""Compatibility shim: re-export the canonical ChatModelAdapter.

Historically this repository had multiple implementations in different
locations. Preserve the import path while delegating the implementation
to the single canonical adapter in ``chat_adapter.py``.
"""

from __future__ import annotations

from voice.infrastructure.llm.chat_adapter import ChatModelAdapter


# Backwards compatibility name
LangChainChatAdapter = ChatModelAdapter

__all__ = ["LangChainChatAdapter", "ChatModelAdapter"]
