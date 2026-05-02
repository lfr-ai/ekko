"""Embedding service using LangChain OpenAI embeddings."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Protocol, cast

if TYPE_CHECKING:
    from ekko.config.settings.base import BaseAppConfig


class EmbeddingModelProtocol(Protocol):
    """Protocol for async embedding models used by this service."""

    async def aembed_query(self, text: str) -> list[float]: ...

    async def aembed_documents(self, texts: list[str]) -> list[list[float]]: ...

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Embedding service backed by LangChain OpenAI embeddings.

    Lazily initializes the embedding model on first use.
    """

    def __init__(self, *, settings: BaseAppConfig) -> None:
        self._settings = settings
        self._model: EmbeddingModelProtocol | None = None

    def _get_model(self) -> EmbeddingModelProtocol:
        if self._model is None:
            from langchain_openai import OpenAIEmbeddings

            if self._settings.openai_api_key:
                model = OpenAIEmbeddings(
                    model=self._settings.rag_embedding_model,
                    api_key=self._settings.openai_api_key,
                )
            else:
                model = OpenAIEmbeddings(model=self._settings.rag_embedding_model)

            self._model = cast("EmbeddingModelProtocol", model)
        return self._model

    async def embed_text(self, text: str) -> list[float]:
        """Embed a single text string."""
        model = self._get_model()
        return await model.aembed_query(text)

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Embed multiple text strings."""
        model = self._get_model()
        return await model.aembed_documents(texts)
