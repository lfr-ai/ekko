"""Ekko — AI-powered voice assistant platform.

This project uses the ``src/`` layout. Short package metadata and exports live
here. Keep this file minimal and stable; avoid importing heavy dependencies.
"""

from pathlib import Path
from typing import Final

__all__: list[str] = []
__version__ = "0.1.0"

APP_NAME: Final[str] = Path(__file__).resolve().parent.name
TITLE: Final[str] = "Ekko"
SUMMARY: Final[str] = "AI-powered voice assistant platform for desktop audio capture and transcription"
