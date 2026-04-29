"""Shared type aliases and value objects."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TranscriptionEntry:
    """A single transcription segment with offset."""

    text: str
    offset: float


Transcription = list[TranscriptionEntry]
