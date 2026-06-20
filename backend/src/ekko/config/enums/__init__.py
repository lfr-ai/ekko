"""Configuration and deployment enumerations."""

from enum import StrEnum, auto, unique


@unique
class Environment(StrEnum):
    """Deployment environments.

    Members:
        LOCAL (str): Local environment on developer machines.
        TEST (str): Testing environment for CI and test suites.
        DEV (str): Shared development environment.
        PROD (str): Production environment serving end users.
    """

    LOCAL = auto()
    TEST = auto()
    DEV = auto()
    PROD = auto()


@unique
class DatabaseBackend(StrEnum):
    """Supported runtime database backends."""

    SQLITE = auto()
    POSTGRESQL = auto()


@unique
class LLMProvider(StrEnum):
    """LLM provider options."""

    OPENAI = auto()
    AZURE_OPENAI = auto()
    ANTHROPIC = auto()
    COHERE = auto()
    GOOGLE = auto()
    OTHER = auto()


@unique
class ChatModel(StrEnum):
    """LLM deployment model identifiers."""

    GPT_4O = "gpt-4o"
    GPT_4O_MINI = "gpt-4o-mini"
    GPT_5 = "gpt-5"
    GPT_5_4_MINI = "gpt-5.4-mini"
    GPT_5_5 = "gpt-5.5"


__all__ = ["ChatModel", "DatabaseBackend", "Environment", "LLMProvider"]
