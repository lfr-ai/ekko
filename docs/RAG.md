# Retrieval-Augmented Generation (RAG)

This project uses an optional RAG stack powered by LangChain. The implementation
is provided as an adapter under `src/voice/infrastructure/adapters/langchain_adapter.py`.

Install RAG extras:

```bash
uv sync --all-extras --group rag
```

## Usage

1. Configure OpenAI credentials via environment variables (see `.env.example`).
1. Use the `LangChainOpenAIAdapter` as an implementation of the
   `voice.core.gateways.openai_gateway.OpenAIGateway` protocol.
