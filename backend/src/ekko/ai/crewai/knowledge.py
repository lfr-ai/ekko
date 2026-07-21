"""CrewAI knowledge integration layer.

Bridges Ekko's domain knowledge sources (transcripts, conversation
history, external documents) into formats consumable by CrewAI agents.

The ``KnowledgeProvider`` loads and indexes content so agents can
retrieve context during task execution.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, final

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class KnowledgeChunk:
    """A single chunk of knowledge available to agents."""

    id: str
    content: str
    source: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    relevance_score: float = 0.0


@final
class KnowledgeProvider:
    """Manages knowledge chunks for CrewAI agent context.

    Serves as the adapter between Ekko's domain data and CrewAI's
    knowledge/memory system. Chunks can be added from transcripts,
    conversation summaries, or external sources.

    Usage::

        provider = KnowledgeProvider()
        provider.add_chunks([
            KnowledgeChunk(id="t1", content="...", source="transcript"),
        ])
        relevant = provider.search("user intent", top_k=3)
    """

    def __init__(self) -> None:
        self._chunks: dict[str, KnowledgeChunk] = {}

    @property
    def chunk_count(self) -> int:
        """Number of indexed chunks."""
        return len(self._chunks)

    def add_chunk(self, chunk: KnowledgeChunk) -> None:
        """Index a single knowledge chunk."""
        self._chunks[chunk.id] = chunk

    def add_chunks(self, chunks: list[KnowledgeChunk]) -> None:
        """Index multiple knowledge chunks."""
        for chunk in chunks:
            self._chunks[chunk.id] = chunk
        logger.info("Indexed %d knowledge chunks (total: %d)", len(chunks), self.chunk_count)

    def get_chunk(self, chunk_id: str) -> KnowledgeChunk | None:
        """Retrieve a chunk by ID."""
        return self._chunks.get(chunk_id)

    def search(self, query: str, *, top_k: int = 5) -> list[KnowledgeChunk]:
        """Search chunks by keyword relevance.

        This is a simple keyword-overlap scorer. For production use,
        plug in an embedding-based retriever via the ``EmbeddingProtocol``.
        """
        scored: list[tuple[float, KnowledgeChunk]] = []
        query_tokens = set(query.lower().split())

        for chunk in self._chunks.values():
            content_tokens = set(chunk.content.lower().split())
            overlap = len(query_tokens & content_tokens)
            if overlap > 0:
                score = overlap / max(len(query_tokens), 1)
                scored.append((score, chunk))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [chunk for _, chunk in scored[:top_k]]

    def clear(self) -> None:
        """Remove all indexed chunks."""
        self._chunks.clear()
        logger.info("Knowledge store cleared")

    def as_context_string(self, query: str, *, top_k: int = 5) -> str:
        """Return a formatted string of relevant knowledge for agent context."""
        results = self.search(query, top_k=top_k)
        if not results:
            return ""

        parts = [f"[{chunk.source}] {chunk.content}" for chunk in results]
        return "\n---\n".join(parts)
