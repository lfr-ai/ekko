"""Core domain exceptions."""


class EkkoError(Exception):
    """Base exception for all Ekko domain errors."""


class ConfigurationError(EkkoError):
    """Raised when configuration is invalid or missing."""


class AudioDeviceError(EkkoError):
    """Raised when an audio device cannot be found or initialized."""


class STTError(EkkoError):
    """Raised when speech-to-text processing fails."""


class LLMError(EkkoError):
    """Raised when an LLM call fails."""


class PromptNotFoundError(EkkoError):
    """Raised when a prompt template file cannot be found."""


class PIIError(EkkoError):
    """Raised when PII anonymization fails."""


class AgentError(EkkoError):
    """Raised when a CrewAI agent execution fails."""


class ConversationNotFoundError(EkkoError):
    """Raised when a conversation ID is not found."""


class AuthenticationError(EkkoError):
    """Raised when authentication fails."""


class AuthorizationError(EkkoError):
    """Raised when authorization fails."""
