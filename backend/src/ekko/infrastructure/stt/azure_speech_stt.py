"""Azure Cognitive Services Speech-to-Text adapter.

This module provides a streaming STT service using Azure Speech Services SDK
with continuous recognition for real-time transcription.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Final

import structlog

if TYPE_CHECKING:
    from collections.abc import Callable

    from ekko.config.settings import BaseAppConfig

# Azure Speech SDK is a required runtime dependency for STT
speechsdk: Any = None
try:
    import azure.cognitiveservices.speech as speechsdk  # type: ignore[import-untyped]

    AZURE_SPEECH_AVAILABLE: Final[bool] = True
except ImportError:  # pragma: no cover - optional runtime dependency
    AZURE_SPEECH_AVAILABLE: Final[bool] = False

logger = structlog.get_logger(__name__)


@dataclass(slots=True, frozen=True)
class Transcript:
    """Immutable transcript result from Azure Speech recognition."""

    stream_name: str
    text: str
    reason: str  # Recognition result reason (e.g. 'RecognizedSpeech')
    offset_ticks: int  # Audio offset in 100-nanosecond units
    duration_ticks: int  # Duration in 100-nanosecond units


class AzureSpeechSTT:
    """Azure Cognitive Services streaming STT service.

    Provides real-time continuous speech recognition with low latency using
    Azure Speech Services. Each audio queue gets its own recognizer instance
    with dedicated push audio input stream.

    **Architecture:**
    - Implements 'STTService' protocol from core.ports.external.audio
    - Zero outward dependencies (infrastructure layer)
    - Uses asyncio for concurrency, azure.cognitiveservices.speech for recognition

    **Usage:**
    ::

        stt = AzureSpeechSTT(settings=config, on_transcript=callback)
        await stt.start()
        await stt.ensure_queue("mic")
        await stt.accept_bytes("mic", audio_chunk)
        # ... continuous recognition happens in background
        await stt.stop()

    **Configuration:**
    Requires EKKO_AZURE_SPEECH_KEY and EKKO_AZURE_SPEECH_REGION env vars.

    **Audio Format:**
    - Sample rate: 16 kHz (Azure recommendation for speech)
    - Channels: Mono (Azure requires mono)
    - Sample width: 16-bit PCM
    - If source audio is different, must be converted before passing to 'accept_bytes'

    **Performance:**
    - Latency: ~300ms from speech to recognized text
    - Interim results: Partial transcriptions available (recognizing event)
    - Continuous recognition: Automatic endpointing and segmentation

    **Error Handling:**
    - Missing credentials: Raises RuntimeError on start()
    - Network failures: Logged, recognition continues when connection restored
    - SDK errors: Logged via error callbacks
    """

    _SAMPLE_RATE_HZ: Final[int] = 16000
    _CHANNELS: Final[int] = 1
    _BITS_PER_SAMPLE: Final[int] = 16

    def __init__(
        self,
        *,
        settings: BaseAppConfig,
        on_transcript: Callable[[Transcript], Any] | None = None,
        output_queue: asyncio.Queue[Transcript] | None = None,
        emit_interim: bool = False,
    ) -> None:
        """Initialize Azure Speech STT service.

        Args:
            settings: Application configuration with Azure credentials.
            on_transcript: Optional callback invoked on each recognized transcript.
                          Can be sync or async function.
            output_queue: Optional asyncio queue to push transcripts into.
            emit_interim: If True, emit partial recognitions (recognizing event).
                         If False, emit only final recognitions (recognized event).

        Raises:
            RuntimeError: If Azure Speech SDK is not installed.
        """
        if not AZURE_SPEECH_AVAILABLE:
            raise RuntimeError(
                "azure-cognitiveservices-speech is not installed. Install with: uv add azure-cognitiveservices-speech"
            )

        self._settings: Final = settings
        self._on_transcript: Final = on_transcript
        self._output_queue: Final = output_queue
        self._emit_interim: Final = emit_interim

        # Per-queue recognizer state
        self._recognizers: dict[str, Any] = {}  # queue_name -> SpeechRecognizer
        self._push_streams: dict[str, Any] = {}  # queue_name -> PushAudioInputStream
        self._running: bool = False
        self._lock: Final = asyncio.Lock()

    async def start(self) -> None:
        """Start the STT service and initialize Azure Speech config.

        Validates credentials and prepares for recognition. Does not start
        recognizers immediately — those are created per-queue in 'ensure_queue'.

        Raises:
            RuntimeError: If Azure credentials are missing or invalid.
        """
        if self._settings.azure_speech_key is None:
            raise RuntimeError("EKKO_AZURE_SPEECH_KEY environment variable is required for Azure STT")

        if not self._settings.azure_speech_region:
            raise RuntimeError("EKKO_AZURE_SPEECH_REGION environment variable is required for Azure STT")

        logger.info(
            "azure_stt_starting",
            region=self._settings.azure_speech_region,
            language=self._settings.azure_speech_language,
            mode=self._settings.azure_speech_recognition_mode,
        )

        async with self._lock:
            self._running = True

        logger.info("azure_stt_started")

    async def stop(self) -> None:
        """Stop all recognizers and clean up resources."""
        logger.info("azure_stt_stopping")

        async with self._lock:
            self._running = False

            # Stop all recognizers
            for queue_name, recognizer in list(self._recognizers.items()):
                try:
                    await asyncio.to_thread(recognizer.stop_continuous_recognition)
                except Exception:
                    logger.exception("failed_to_stop_recognizer", queue_name=queue_name)

            # Close push streams
            for queue_name, push_stream in list(self._push_streams.items()):
                try:
                    push_stream.close()
                except Exception:
                    logger.exception("failed_to_close_stream", queue_name=queue_name)

            self._recognizers.clear()
            self._push_streams.clear()

        logger.info("azure_stt_stopped")

    async def ensure_queue(self, queue_name: str) -> None:
        """Ensure a recognizer exists for the named audio queue.

        Creates a dedicated Azure Speech recognizer with push audio stream
        for the given queue if one doesn't exist. Starts continuous recognition.

        Args:
            queue_name: Identifier for the audio source (e.g. 'mic', 'system').

        Raises:
            RuntimeError: If service not started or credentials invalid.
        """
        if not self._running:
            raise RuntimeError("STT service not started. Call start() first.")

        async with self._lock:
            if queue_name in self._recognizers:
                return  # Already exists

            logger.info("creating_recognizer", queue_name=queue_name)

            # Create Azure Speech config
            # start() guarantees azure_speech_key is not None before we reach here
            assert self._settings.azure_speech_key is not None
            speech_config = await asyncio.to_thread(
                speechsdk.SpeechConfig,
                subscription=self._settings.azure_speech_key.get_secret_value(),
                region=self._settings.azure_speech_region,
            )
            speech_config.speech_recognition_language = self._settings.azure_speech_language

            # Create push audio input stream
            push_stream = speechsdk.audio.PushAudioInputStream(
                stream_format=speechsdk.audio.AudioStreamFormat(
                    samples_per_second=self._SAMPLE_RATE_HZ,
                    bits_per_sample=self._BITS_PER_SAMPLE,
                    channels=self._CHANNELS,
                )
            )
            audio_config = speechsdk.audio.AudioConfig(stream=push_stream)

            # Create recognizer
            recognizer = speechsdk.SpeechRecognizer(
                speech_config=speech_config,
                audio_config=audio_config,
            )

            # Wire event handlers
            self._connect_callbacks(recognizer, queue_name)

            # Store state
            self._recognizers[queue_name] = recognizer
            self._push_streams[queue_name] = push_stream

            # Start continuous recognition
            await asyncio.to_thread(recognizer.start_continuous_recognition)

            logger.info("recognizer_started", queue_name=queue_name)

    async def accept_bytes(self, queue_name: str, data: bytes) -> None:
        """Push raw audio bytes into the recognizer for the given queue.

        Audio must be 16 kHz, mono, 16-bit PCM. If source audio is different
        format, it must be converted before calling this method.

        Args:
            queue_name: Audio source identifier.
            data: Raw PCM audio bytes.

        Raises:
            RuntimeError: If queue doesn't exist (call ensure_queue first).
        """
        push_stream = self._push_streams.get(queue_name)
        if push_stream is None:
            raise RuntimeError(f"No recognizer for queue '{queue_name}'. Call ensure_queue() first.")

        # Push bytes to Azure Speech SDK
        # This is non-blocking — SDK buffers internally
        try:
            push_stream.write(data)
        except Exception:
            logger.exception("failed_to_push_audio", queue_name=queue_name)

    def _connect_callbacks(self, recognizer: Any, queue_name: str) -> None:
        """Wire Azure Speech recognizer event callbacks.

        Args:
            recognizer: Azure SpeechRecognizer instance.
            queue_name: Queue name for logging context.
        """

        def _on_recognized(evt: Any) -> None:
            """Handle final recognized speech."""
            result = evt.result
            if result.reason == speechsdk.ResultReason.RecognizedSpeech:
                transcript = Transcript(
                    stream_name=queue_name,
                    text=result.text,
                    reason="RecognizedSpeech",
                    offset_ticks=result.offset,
                    duration_ticks=result.duration,
                )
                # Fire-and-forget background task for transcript emission
                task = asyncio.create_task(self._emit_transcript(transcript))
                task.add_done_callback(lambda t: t.exception() if not t.cancelled() else None)
            elif result.reason == speechsdk.ResultReason.NoMatch:
                logger.debug("no_speech_recognized", queue_name=queue_name)

        def _on_recognizing(evt: Any) -> None:
            """Handle interim recognition (partial results)."""
            if not self._emit_interim:
                return

            result = evt.result
            if result.text:
                transcript = Transcript(
                    stream_name=queue_name,
                    text=result.text,
                    reason="Recognizing",
                    offset_ticks=result.offset,
                    duration_ticks=result.duration,
                )
                # Fire-and-forget background task for transcript emission
                task = asyncio.create_task(self._emit_transcript(transcript))
                task.add_done_callback(lambda t: t.exception() if not t.cancelled() else None)

        def _on_canceled(evt: Any) -> None:
            """Handle recognition cancellation."""
            logger.warning(
                "recognition_canceled",
                queue_name=queue_name,
                reason=evt.reason,
                error_details=getattr(evt, "error_details", None),
            )

        def _on_session_stopped(_evt: Any) -> None:
            """Handle session stopped."""
            logger.info("recognition_session_stopped", queue_name=queue_name)

        # Connect events
        recognizer.recognized.connect(_on_recognized)
        recognizer.recognizing.connect(_on_recognizing)
        recognizer.canceled.connect(_on_canceled)
        recognizer.session_stopped.connect(_on_session_stopped)

    async def _emit_transcript(self, transcript: Transcript) -> None:
        """Emit transcript to callback and/or output queue.

        Args:
            transcript: Recognized transcript to emit.
        """
        # Invoke callback if provided
        if self._on_transcript is not None:
            try:
                result = self._on_transcript(transcript)
                if asyncio.iscoroutine(result):
                    await result
            except Exception:
                logger.exception("transcript_callback_error")

        # Push to output queue if provided
        if self._output_queue is not None:
            try:
                await self._output_queue.put(transcript)
            except Exception:
                logger.exception("transcript_queue_error")
