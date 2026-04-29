from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from ekko.config.settings import BaseAppConfig, get_settings

if TYPE_CHECKING:
    from collections.abc import Iterable

    from ekko.core.interfaces import OpenAIGateway


@dataclass(slots=True)
class SummarizerService:
    gateway: OpenAIGateway
    settings: BaseAppConfig | None = None

    def summarize(self, chunks: Iterable[str]) -> str:
        """Summarize a list of text chunks into a single summary.

        Uses the OpenAI gateway to perform summarization. Keeps orchestration
        at application level (chunking, prompt assembly).
        """
        settings = self.settings or get_settings()
        prompt_path = settings.prompt_dir_path / "summary_prompt_chunks.txt"

        system_prompt = "Summarizer"
        try:
            template = Path(prompt_path).read_text(encoding="utf-8")
        except Exception:
            template = "Summarize the following content concisely:\n{content}"

        payload = "\n\n".join(chunks)
        user_prompt = template.replace("{content}", payload)
        model = settings.rag_llm_model

        return self.gateway.chat(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            model=model,
            temperature=0.0,
            max_completion_tokens=512,
        )
