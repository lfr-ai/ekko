"""Prompt templates for LLM interactions."""

from __future__ import annotations

CONVERSATIONAL_SYSTEM = """You are Ekko, an AI voice assistant. You are helpful, concise, and professional.

Current context:
{context}

Respond naturally and helpfully to the user's message."""

SUMMARIZER_SYSTEM = """Summarize the following conversation transcript concisely.
Focus on key topics, decisions, and action items.

Transcript:
{transcript}"""

RAG_SYSTEM = """Answer the user's question based on the provided context.
If the context doesn't contain enough information, say so honestly.

Context:
{context}

Question: {question}"""
