# Ekko

[![CI](https://github.com/lfr-ai/ekko/actions/workflows/ci.yml/badge.svg)](https://github.com/lfr-ai/ekko/actions/workflows/ci.yml)
[![CodeQL](https://github.com/lfr-ai/ekko/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/lfr-ai/ekko/actions/workflows/codeql-analysis.yml)
[![codecov](https://codecov.io/gh/lfr-ai/ekko/branch/master/graph/badge.svg)](https://codecov.io/gh/lfr-ai/ekko)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Voice assistant platform: real-time transcription, LLM summarization, and PII
anonymization. Ships as a local Windows EXE.

> Ekko is a local desktop tool — see [SECURITY.md](SECURITY.md) before
> exposing it to any network. The UI covers one flow today (paste a
> transcript, get a summary); everything else is on the
> [roadmap](docs/modernization-roadmap.md).

## Features

- Real-time desktop audio capture and speech-to-text
- LLM summarization via LiteLLM, exposed over REST (`POST /summarize`);
  every request is PII-anonymized before it reaches the LLM
- Regex-based PII anonymization
- REST API for health, PII, summarization, and stream control, plus SSE
  transcript streaming
- One read-only GraphQL query for the prompt catalog

## Quick start

Requires Python 3.14, Node 20+, [uv](https://astral.sh/uv), [Bun](https://bun.sh), and [Task](https://taskfile.dev).

```bash
task install
cp .env.example .env.local   # add your API keys
task db:migrate
task dev                     # backend on :8000, frontend on :3000
```

## Documentation

- [Architecture](docs/architecture.md) — layers, stack, and testing
- [Roadmap](docs/modernization-roadmap.md) — shipped, in progress, and planned
- [Contributing](CONTRIBUTING.md) — setup, conventions, and pull requests
- [Security policy](SECURITY.md)

## License

MIT — see [LICENSE](LICENSE).
