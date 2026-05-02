# Ekko Knowledge Graph

## Project Identity
- **Name**: Ekko
- **Type**: AI-powered voice assistant platform
- **Architecture**: Clean Architecture with strict layered boundaries
- **Deployment**: Local desktop application (PyInstaller EXE)

## Technology Stack

### Backend
- Python 3.12, FastAPI, Uvicorn
- SQLAlchemy 2.0+ async, aiosqlite (SQLite)
- Strawberry GraphQL (subscriptions)
- LangChain, CrewAI, faster-whisper
- Pydantic v2, structlog

### Frontend
- React 19, TypeScript 5.8
- Vite 6 + SWC
- shadcn/ui (Radix + Tailwind CSS v4)
- Zustand 5, TanStack React Query 5

### DevOps
- uv (Python), bun (frontend)
- Taskfile.yml
- Docker + Caddy
- GitHub Actions CI
- CodeRabbit AI reviews
- GitNexus code intelligence

## Architecture Layers

### Core (innermost)
- Entities: domain objects
- Value Objects: immutable data
- Interfaces: port protocols
- Exceptions: domain errors
- Enums: domain enumerations
- **Dependencies**: stdlib, utils, config ONLY

### Application
- DTOs: data transfer objects
- Services: use case orchestration
- Handlers: application handlers
- Mappers: entity <-> DTO conversion
- **Dependencies**: core, infrastructure, ai, config, utils

### Infrastructure
- DB: SQLAlchemy models, engine (SQLite)
- Adapters: audio, STT
- Concurrency: queue/thread managers
- LLM: chat adapters
- **Dependencies**: core, config, utils, external libs

### AI
- CrewAI: multi-agent orchestration
- Chains: conversational chains
- Embeddings: RAG embedding service
- PII: regex-based anonymization
- Prompts: template files
- LLM: adapter layer
- **Dependencies**: core, config, utils ONLY

### Presentation (outermost)
- API: FastAPI routes, middleware
- GraphQL: Strawberry schema, subscriptions
- **Dependencies**: application, core, config, utils

### Composition
- Container: DI wiring
- App Factory: FastAPI app creation

## Data Flow
1. Audio captured -> STT transcription -> PII scrubbing
2. Clean text -> AI pipeline (CrewAI agents, chains)
3. Results -> GraphQL subscriptions -> React UI
4. Persisted -> SQLite via SQLAlchemy async

## Key Interfaces (Ports)
- AudioStreamProtocol: audio capture
- ChatProtocol: LLM chat
- EmbeddingProtocol: text embeddings
- PIIProtocol: PII anonymization
- TranscriberProtocol: speech-to-text

## Configuration
- Settings: Pydantic BaseSettings
- Env selector: EKKO_ENVIRONMENT (local/test)
- Dotenv chain: .env -> .env.{stage} -> .env.local
