# LangChain Chat Adapter

Location: `src/voice/infrastructure/llm/chat_adapter.py`

This adapter provides a provider-agnostic interface to LangChain chat models.

Usage (example):

```python
from voice.infrastructure.llm.chat_adapter import ChatModelAdapter
from voice.config.settings import get_settings

settings = get_settings()
adapter = ChatModelAdapter.from_settings(settings)
resp = adapter.chat(
    system_prompt="You are a helpful assistant.",
    user_prompt="Hello, what is RAG?",
    deployment_name=settings.llm_default_deployment or "gpt-4",
)
```

Supports both sync (`chat`) and async (`async_chat`) invocation.
# LangChain Adapter

This repository includes a LangChain-based chat adapter located at:

```
src/voice/infrastructure/llm/langchain_adapter.py
```

The adapter implements a simple provider-agnostic interface (`ChatPort` in
`src/voice/core/protocols.py`) and mirrors the pattern used in the
`koda_automation` golden-standard repository.

Design notes:
- Provider selection is driven from `Settings` (`LLM_PROVIDER`).
- The adapter lazily initializes model clients and caches them per deployment.
- `OpenAI` and `Azure OpenAI` are supported; KeyVault is not used — API keys are
  expected in environment variables.

How to use:

1. Configure `OPENAI_API_KEY` and `LLM_MODEL` in `.env` or CI secrets.
2. Create adapter from settings:

```py
from voice.config.settings import settings
from voice.infrastructure.llm.langchain_adapter import LangChainChatAdapter

adapter = LangChainChatAdapter.from_settings(settings)
resp = await adapter.async_chat("system", "hello", deployment_name=settings.LLM_MODEL, max_completion_tokens=256, temperature=0.0)
```
