from __future__ import annotations

from enum import Enum, auto
from typing import NewType

# Lightweight type aliases used across the chat/LLM integration
ModelDeploymentName = NewType("ModelDeploymentName", str)
PromptContent = NewType("PromptContent", str)
MaxTokens = NewType("MaxTokens", int)
Temperature = NewType("Temperature", float)


class LLMProvider(Enum):
    OPENAI = auto()
    AZURE_OPENAI = auto()

    @classmethod
    def from_str(cls, value: str) -> "LLMProvider":
        v = value.lower()
        if v in ("openai", "open_ai"):
            return cls.OPENAI
        if v in ("azure_openai", "azure"):
            return cls.AZURE_OPENAI
        raise ValueError(f"Unknown LLM provider: {value}")
