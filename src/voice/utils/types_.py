from collections import namedtuple
from enum import Enum, auto
from typing import Type

TranscriptionEntry = namedtuple("TranscriptionEntry", ["text", "offset"])
Transcription = list[TranscriptionEntry]


class RecognitionMode(Enum):
    """
    Enumeration of recognition modes.
    """

    ADVISOR = auto()
    CUSTOMER = auto()

    @classmethod
    def from_stream_type(cls: Type["RecognitionMode"], stream_type: str):
        """
        Map stream type string to RecognitionMode enumeration.

        Args:
            stream_type (str): Type of stream.

        Returns:
            RecognitionMode: Corresponding RecognitionMode enumeration.
        """
        if stream_type not in ("sys", "mic"):
            raise ValueError(f"Invalid stream type: {stream_type}. Expected 'sys' or 'mic'.")

        mapping = {
            "sys": cls.CUSTOMER,
            "mic": cls.ADVISOR,
        }

        return mapping[stream_type]
