"""Core domain exceptions."""


class EkkoError(Exception):
    """Base exception for all Ekko domain errors."""


class ConfigurationError(EkkoError):
    """Invalid or missing application configuration."""


class AudioDeviceError(EkkoError):
    """Audio device cannot be found or initialized."""


class STTError(EkkoError):
    """Speech-to-text processing failure."""


class LLMError(EkkoError):
    """LLM request failure."""


class PIIPolicyViolationError(EkkoError):
    """Text fails the mandatory PII policy check before an LLM call."""


class PromptNotFoundError(EkkoError):
    """Prompt template file cannot be found."""
