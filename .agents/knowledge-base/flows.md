# Main flows

## Audio to transcript

Audio adapter → STT port → transcript queue → REST SSE `/transcripts/stream`
→ frontend client.

## PII

REST `/pii/anonymize` → Core PII policy → anonymizer port → rendered result.
Text is anonymized before crossing an AI boundary.

## Prompt registry

Application service → prompt registry port → AI prompt-registry client → versioned
prompt files and registry metadata.

## Persistence

Composition creates the SQLAlchemy engine/session factory. ORM models stay in
infrastructure; Alembic owns schema history under `backend/alembic/`.
