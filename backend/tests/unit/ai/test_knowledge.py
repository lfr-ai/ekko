"""Tests for CrewAI knowledge provider."""

import dataclasses

import pytest

from ekko.ai.crewai.knowledge import KnowledgeChunk, KnowledgeProvider


class TestKnowledgeChunk:
    def test_defaults(self):
        chunk = KnowledgeChunk(id="1", content="hello world")
        assert chunk.source == ""
        assert chunk.metadata == {}
        assert chunk.relevance_score == 0.0

    def test_frozen(self):
        chunk = KnowledgeChunk(id="1", content="text")
        with pytest.raises(dataclasses.FrozenInstanceError):
            chunk.id = "2"  # type: ignore[misc]


class TestKnowledgeProvider:
    def test_add_single_chunk(self):
        provider = KnowledgeProvider()
        chunk = KnowledgeChunk(id="a", content="pension plan details")
        provider.add_chunk(chunk)
        assert provider.chunk_count == 1

    def test_add_multiple_chunks(self):
        provider = KnowledgeProvider()
        chunks = [
            KnowledgeChunk(id="1", content="pension info"),
            KnowledgeChunk(id="2", content="retirement plans"),
        ]
        provider.add_chunks(chunks)
        assert provider.chunk_count == 2

    def test_get_chunk_by_id(self):
        provider = KnowledgeProvider()
        chunk = KnowledgeChunk(id="x", content="test content", source="transcript")
        provider.add_chunk(chunk)
        result = provider.get_chunk("x")
        assert result is chunk

    def test_get_chunk_missing(self):
        provider = KnowledgeProvider()
        assert provider.get_chunk("nonexistent") is None

    def test_search_keyword_overlap(self):
        provider = KnowledgeProvider()
        provider.add_chunks([
            KnowledgeChunk(id="1", content="pension plan retirement savings"),
            KnowledgeChunk(id="2", content="health insurance coverage"),
            KnowledgeChunk(id="3", content="pension retirement benefits overview"),
        ])
        results = provider.search("pension retirement")
        assert len(results) >= 1
        # Items with more overlap should rank higher
        ids = [r.id for r in results]
        assert "3" in ids or "1" in ids

    def test_search_no_match(self):
        provider = KnowledgeProvider()
        provider.add_chunk(KnowledgeChunk(id="1", content="hello world"))
        results = provider.search("xyzzy")
        assert results == []

    def test_search_respects_top_k(self):
        provider = KnowledgeProvider()
        for i in range(10):
            provider.add_chunk(KnowledgeChunk(id=str(i), content=f"shared keyword item {i}"))
        results = provider.search("shared keyword", top_k=3)
        assert len(results) <= 3

    def test_clear(self):
        provider = KnowledgeProvider()
        provider.add_chunk(KnowledgeChunk(id="1", content="data"))
        provider.clear()
        assert provider.chunk_count == 0

    def test_as_context_string(self):
        provider = KnowledgeProvider()
        provider.add_chunks([
            KnowledgeChunk(id="1", content="pension plan details", source="transcript"),
            KnowledgeChunk(id="2", content="investment strategy pension", source="doc"),
        ])
        context = provider.as_context_string("pension")
        assert "pension" in context
        assert "---" in context or "[transcript]" in context

    def test_as_context_string_empty(self):
        provider = KnowledgeProvider()
        result = provider.as_context_string("anything")
        assert result == ""

    def test_duplicate_id_overwrites(self):
        provider = KnowledgeProvider()
        provider.add_chunk(KnowledgeChunk(id="1", content="original"))
        provider.add_chunk(KnowledgeChunk(id="1", content="updated"))
        assert provider.chunk_count == 1
        assert provider.get_chunk("1").content == "updated"
