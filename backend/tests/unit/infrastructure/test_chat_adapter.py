import asyncio
import sys
from types import ModuleType, SimpleNamespace

from ekko.config.enums import LLMProvider
from ekko.config.settings import BaseAppConfig


class FakeModel:
    def bind(self, **kwargs):
        return self

    def invoke(self, messages):
        return SimpleNamespace(content="sync-ok")

    async def ainvoke(self, messages):
        return SimpleNamespace(content="async-ok")


# Inject lightweight fake langchain modules so tests do not require the real
# langchain packages at runtime. This mirrors what our adapter expects.
fake_langchain_chat = ModuleType("langchain.chat_models")
fake_langchain_chat.init_chat_model = lambda *args, **kwargs: FakeModel()
sys.modules["langchain.chat_models"] = fake_langchain_chat

fake_lc_models = ModuleType("langchain_core.language_models.chat_models")
fake_lc_models.BaseChatModel = object
sys.modules["langchain_core.language_models.chat_models"] = fake_lc_models

fake_msgs = ModuleType("langchain_core.messages")


class BaseMessage:
    def __init__(self, content: str):
        self.content = content


class HumanMessage(BaseMessage):
    pass


class SystemMessage(BaseMessage):
    pass


fake_msgs.BaseMessage = BaseMessage
fake_msgs.HumanMessage = HumanMessage
fake_msgs.SystemMessage = SystemMessage
sys.modules["langchain_core.messages"] = fake_msgs


def test_chat_adapter_sync(monkeypatch):
    from ekko.infrastructure.llm.chat_adapter import ChatModelAdapter

    settings = BaseAppConfig(llm_provider=LLMProvider.AZURE_OPENAI)
    adapter = ChatModelAdapter.from_settings(settings)
    result = adapter.chat(system_prompt="S", user_prompt="U", model="m")
    assert result == "sync-ok"


def test_chat_adapter_async(monkeypatch):
    from ekko.infrastructure.llm.chat_adapter import ChatModelAdapter

    settings = BaseAppConfig(llm_provider=LLMProvider.AZURE_OPENAI)
    adapter = ChatModelAdapter.from_settings(settings)

    async def run():
        return await adapter.async_chat(system_prompt="S", user_prompt="U", model="m")

    result = asyncio.run(run())
    assert result == "async-ok"
