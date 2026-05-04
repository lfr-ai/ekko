"""Generate fixture audio files for STT testing."""

from __future__ import annotations

import wave
from pathlib import Path


def create_test_audio_file(output_path: Path, duration_seconds: float = 1.0, sample_rate: int = 16000) -> None:
    """Create a simple test audio file (silence) for STT testing.

    Args:
        output_path: Path to write the audio file
        duration_seconds: Duration of the audio in seconds
        sample_rate: Sample rate in Hz
    """
    import numpy as np

    # Generate silence (or a simple sine wave for more realism)
    num_samples = int(duration_seconds * sample_rate)
    # Simple 440Hz sine wave
    frequency = 440.0
    amplitude = 0.3
    t = np.linspace(0, duration_seconds, num_samples)
    audio_data = (amplitude * np.sin(2 * np.pi * frequency * t) * 32767).astype(np.int16)

    # Write to WAV file
    with wave.open(str(output_path), "wb") as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_data.tobytes())


if __name__ == "__main__":
    # Create fixture audio files
    fixtures_dir = Path(__file__).parent
    create_test_audio_file(fixtures_dir / "test_audio_1s.wav", duration_seconds=1.0)
    create_test_audio_file(fixtures_dir / "test_audio_2s.wav", duration_seconds=2.0)
    print("Fixture audio files created successfully")
