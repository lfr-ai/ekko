# Environment & Configuration

This document describes the environment variable layout and recommended
process for managing multiple environments (dev/test/staging/prod).

Key variables (see `.env.example`):

- `ENV` - one of `dev`, `test`, `staging`, `prod`.
- `DATABASE_URL`, `DATABASE_URL_TEST`, `DATABASE_URL_STAGING`, `DATABASE_URL_PROD` - SQLAlchemy async DB URLs.
- `OPENAI_API_KEY` - OpenAI API key used by LangChain adapter.
- `LLM_PROVIDER`, `LLM_MODEL`, `EMBEDDING_MODEL` - LLM and embedding configuration.

Usage:

1. Copy `.env.example` to `.env` in local development and fill secrets.
2. For CI, set environment variables in the pipeline (do not commit secrets).
3. Use `Settings` in `src/voice/config/settings.py` to access typed configuration.
