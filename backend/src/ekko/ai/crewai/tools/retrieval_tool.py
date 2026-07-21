"""Retrieval tool for CrewAI agents."""

from __future__ import annotations

from crewai.tools import BaseTool


class RetrievalTool(BaseTool):
    """Tool for retrieving relevant context from the knowledge base.

    This is a scaffold — the actual retrieval logic (e.g. vector store query)
    should be wired in when a vector store backend is configured.
    """

    name: str = "knowledge_retrieval"
    description: str = "Search the knowledge base for information relevant to a query."

    def _run(self, query: str) -> str:
        """Synchronous retrieval (placeholder)."""
        return f"[No knowledge base configured. Query was: {query}]"
