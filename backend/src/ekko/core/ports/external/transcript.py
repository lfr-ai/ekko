"""Transcript protocol."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from collections.abc import Sequence

    from ekko.core.value_objects import TranscriptionInfo, TranscriptSegment


class TranscriptProtocol(Protocol):
    """Protocol for a completed transcript with segments and metadata."""

    stream_name: str
    text: str
    segments: Sequence[TranscriptSegment]
    info: TranscriptionInfo
