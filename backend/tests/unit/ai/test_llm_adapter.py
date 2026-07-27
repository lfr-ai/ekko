"""Tests for LLM adapter."""

import pytest

from ekko.ai.llm.adapter import LLMAdapter


class TestLLMAdapter:
    def test_default_deployment_from_settings(self):
        adapter = LLMAdapter()
        # Should resolve from settings without error
        assert isinstance(adapter.default_deployment, str)
        assert len(adapter.default_deployment) > 0

    def test_chat_adapter_raises_when_none(self):
        adapter = LLMAdapter()
        with pytest.raises(RuntimeError, match="requires a chat_adapter"):
            _ = adapter.chat_adapter

    def test_chat_adapter_property(self):
        class FakeChat:
            def chat(self, **kwargs):
                return "response"

        adapter = LLMAdapter(chat_adapter=FakeChat())
        assert adapter.chat_adapter is not None

    def test_chat_delegates_to_adapter(self):
        calls = []

        class TrackingChat:
            def chat(self, **kwargs):
                calls.append(kwargs)
                return "tracked"

        adapter = LLMAdapter(chat_adapter=TrackingChat())
        result = adapter.chat("system", "user")
        assert result == "tracked"
        assert len(calls) == 1
        assert calls[0]["system_prompt"] == "system"
        assert calls[0]["user_prompt"] == "user"

    def test_chat_uses_default_model(self):
        calls = []

        class TrackingChat:
            def chat(self, **kwargs):
                calls.append(kwargs)
                return "ok"

        adapter = LLMAdapter(chat_adapter=TrackingChat())
        adapter.chat("sys", "usr")
        assert calls[0]["model"] == adapter.default_deployment

    def test_chat_uses_explicit_model(self):
        calls = []

        class TrackingChat:
            def chat(self, **kwargs):
                calls.append(kwargs)
                return "ok"

        adapter = LLMAdapter(chat_adapter=TrackingChat())
        adapter.chat("sys", "usr", model="custom-model")
        assert calls[0]["model"] == "custom-model"

    @pytest.mark.asyncio
    async def test_async_chat_raises_when_no_adapter(self):
        adapter = LLMAdapter()
        with pytest.raises(RuntimeError):
            await adapter.async_chat("sys", "usr")
