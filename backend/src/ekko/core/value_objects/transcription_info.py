"""Transcription info value object."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TranscriptionInfo:
    """Metadata returned by the speech-to-text engine."""

    language: str = ""
    language_probability: float = 0.0
    duration: float = 0.0
