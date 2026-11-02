"""Azure Cognitive Services Speech-to-Text adapter.

This module provides a streaming STT service using Azure Speech Services SDK
with continuous recognition for real-time transcription.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, Final, Protocol, runtime_checkable

from ekko.core.enums import AudioQueueName
from ekko.core.value_objects import SOURCE_MICROPHONE, SOURCE_SYSTEM, TranscriptSegment

if TYPE_CHECKING:
    from collections.abc import Callable

    from pydantic import SecretStr


class _AzureSpeechConfig(Protocol):
    """Configuration fields required by Azure speech recognition."""

    azure_speech_key: SecretStr | None
    azure_speech_region: str
    azure_speech_language: str
    azure_speech_recognition_mode: str


# Azure Speech SDK is a required runtime dependency for STT
speechsdk: object = None
try:
    import azure.cognitiveservices.speech as speechsdk  # type: ignore[import-untyped]

    AZURE_SPEECH_AVAILABLE: Final[bool] = True
except ImportError:  # pragma: no cover - optional runtime dependency
    AZURE_SPEECH_AVAILABLE: Final[bool] = False

_logger = logging.getLogger(__name__)


@runtime_checkable
class _Signal(Protocol):
    def connect(self, callback: Callable[[object], None]) -> object: ...


class _Recognizer(Protocol):
    recognized: _Signal
    recognizing: _Signal
    canceled: _Signal
    session_stopped: _Signal

    def start_continuous_recognition(self) -> object: ...

    def stop_continuous_recognition(self) -> object: ...


class _PushStream(Protocol):
    def write(self, data: bytes) -> object: ...

    def close(self) -> object: ...


class AzureSpeechSTT:
    """Azure Cognitive Services streaming STT service.

    Provides real-time continuous speech recognition with low latency using
    Azure Speech Services. Each audio queue gets its own recognizer instance
    with dedicated push audio input stream.

    **Architecture:**
    - Implements the 'STTPort' protocol from core.ports
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
        settings: _AzureSpeechConfig,
        on_transcript: Callable[[TranscriptSegment], object] | None = None,
        output_queue: asyncio.Queue[TranscriptSegment] | None = None,
        emit_interim: bool = False,
    ):
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
            msg = "azure-cognitiveservices-speech is not installed. Install with: uv add azure-cognitiveservices-speech"
            raise RuntimeError(msg)

        self._settings: Final = settings
        self._on_transcript: Final = on_transcript
        self._output_queue: Final = output_queue
        self._emit_interim: Final = emit_interim

        # Per-queue recognizer state
        self._recognizers: dict[str, _Recognizer] = {}
        self._push_streams: dict[str, _PushStream] = {}
        self._emission_tasks: set[asyncio.Task[None]] = set()
        self._started_at: datetime | None = None
        self._event_loop: asyncio.AbstractEventLoop | None = None
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
            msg = "EKKO_AZURE_SPEECH_KEY environment variable is required for Azure STT"
            raise RuntimeError(msg)

        if not self._settings.azure_speech_region:
            msg = "EKKO_AZURE_SPEECH_REGION environment variable is required for Azure STT"
            raise RuntimeError(msg)

        _logger.info(
            "Starting Azure speech-to-text",
            extra={
                "region": self._settings.azure_speech_region,
                "language": self._settings.azure_speech_language,
                "mode": self._settings.azure_speech_recognition_mode,
            },
        )

        async with self._lock:
            self._event_loop = asyncio.get_running_loop()
            self._started_at = datetime.now(UTC)
            self._running = True

        _logger.info("Azure speech-to-text started")

    async def stop(self) -> None:
        """Stop all recognizers and clean up resources."""
        _logger.info("Stopping Azure speech-to-text")

        async with self._lock:
            self._running = False

            # Stop all recognizers
            for queue_name, recognizer in list(self._recognizers.items()):
                try:
                    stop_method = _require_method(recognizer, method_name="stop_continuous_recognition")
                    await asyncio.to_thread(stop_method)
                except Exception:
                    _logger.exception("Failed to stop recognizer", extra={"queue_name": queue_name})

            # Close push streams
            for queue_name, push_stream in list(self._push_streams.items()):
                try:
                    push_stream.close()
                except Exception:
                    _logger.exception("Failed to close audio stream", extra={"queue_name": queue_name})

            self._recognizers.clear()
            self._push_streams.clear()

        emission_tasks = tuple(self._emission_tasks)
        for task in emission_tasks:
            task.cancel()
        if emission_tasks:
            await asyncio.gather(*emission_tasks, return_exceptions=True)
        self._emission_tasks.clear()
        self._event_loop = None
        self._started_at = None

        _logger.info("Azure speech-to-text stopped")

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
            msg = "STT service not started. Call start() first."
            raise RuntimeError(msg)

        async with self._lock:
            if queue_name in self._recognizers:
                return  # Already exists

            _logger.info("Creating recognizer", extra={"queue_name": queue_name})

            sdk = _require_speech_sdk()
            speech_config_factory = _require_callable_attr(sdk, attr_name="SpeechConfig")
            audio_namespace = _require_attr(sdk, attr_name="audio")
            push_stream_factory = _require_callable_attr(audio_namespace, attr_name="PushAudioInputStream")
            stream_format_factory = _require_callable_attr(audio_namespace, attr_name="AudioStreamFormat")
            audio_config_factory = _require_callable_attr(audio_namespace, attr_name="AudioConfig")
            recognizer_factory = _require_callable_attr(sdk, attr_name="SpeechRecognizer")

            # Create Azure Speech config
            # start() guarantees azure_speech_key is not None before we reach here
            assert self._settings.azure_speech_key is not None
            speech_config = await asyncio.to_thread(
                speech_config_factory,
                subscription=self._settings.azure_speech_key.get_secret_value(),
                region=self._settings.azure_speech_region,
            )
            _set_speech_recognition_language(speech_config=speech_config, language=self._settings.azure_speech_language)

            # Create push audio input stream
            push_stream_obj = push_stream_factory(
                stream_format=stream_format_factory(
                    samples_per_second=self._SAMPLE_RATE_HZ,
                    bits_per_sample=self._BITS_PER_SAMPLE,
                    channels=self._CHANNELS,
                )
            )
            audio_config = audio_config_factory(stream=push_stream_obj)

            # Create recognizer
            recognizer_obj = recognizer_factory(
                speech_config=speech_config,
                audio_config=audio_config,
            )

            recognizer = _require_recognizer(recognizer_obj)
            push_stream = _require_push_stream(push_stream_obj)

            # Wire event handlers
            self._connect_callbacks(recognizer, queue_name)

            # Store state
            self._recognizers[queue_name] = recognizer
            self._push_streams[queue_name] = push_stream

            # Start continuous recognition
            await asyncio.to_thread(recognizer.start_continuous_recognition)

            _logger.info("Recognizer started", extra={"queue_name": queue_name})

    def _connect_callbacks(self, recognizer: object, queue_name: str) -> None:
        """Wire Azure Speech recognizer event callbacks.

        Args:
            recognizer: Azure SpeechRecognizer instance.
            queue_name: Queue name for logging context.
        """

        def _on_recognized(evt: object) -> None:
            """Handle final recognized speech."""
            result = _event_result(evt)
            if result is None:
                return
            self._handle_recognized_result(queue_name=queue_name, result=result)

        def _on_recognizing(evt: object) -> None:
            """Handle interim recognition (partial results)."""
            if not self._emit_interim:
                return

            result = _event_result(evt)
            if result is None:
                return
            self._handle_interim_result(queue_name=queue_name, result=result)

        def _on_canceled(evt: object) -> None:
            """Handle recognition cancellation."""
            _logger.warning(
                "Recognition canceled",
                extra={
                    "queue_name": queue_name,
                    "reason": getattr(evt, "reason", "unknown"),
                    "error_details": getattr(evt, "error_details", None),
                },
            )

        def _on_session_stopped(_evt: object) -> None:
            """Handle session stopped."""
            _logger.info("Recognition session stopped", extra={"queue_name": queue_name})

        _require_signal(getattr(recognizer, "recognized", None), signal_name="recognized").connect(_on_recognized)
        _require_signal(getattr(recognizer, "recognizing", None), signal_name="recognizing").connect(_on_recognizing)
        _require_signal(getattr(recognizer, "canceled", None), signal_name="canceled").connect(_on_canceled)
        _require_signal(getattr(recognizer, "session_stopped", None), signal_name="session_stopped").connect(
            _on_session_stopped
        )

    def _handle_recognized_result(self, *, queue_name: str, result: object) -> None:
        """Process recognized result and emit final transcript when applicable."""
        if _result_reason_equals(result=result, reason_name="RecognizedSpeech"):
            transcript = TranscriptSegment(
                text=_result_text(result),
                start_seconds=_ticks_to_seconds(_result_offset(result)),
                end_seconds=_ticks_to_seconds(_result_offset(result) + _result_duration(result)),
                source=_source_name(queue_name=queue_name),
                timestamp=self._transcript_timestamp(offset_ticks=_result_offset(result)),
            )
            self._schedule_emit_transcript(transcript=transcript)
            return

        if _result_reason_equals(result=result, reason_name="NoMatch"):
            _logger.debug("No speech recognized", extra={"queue_name": queue_name})

    def _handle_interim_result(self, *, queue_name: str, result: object) -> None:
        """Process recognizing result and emit interim transcript when text exists."""
        transcript_text = _result_text(result)
        if not transcript_text:
            return

        transcript = TranscriptSegment(
            text=transcript_text,
            start_seconds=_ticks_to_seconds(_result_offset(result)),
            end_seconds=_ticks_to_seconds(_result_offset(result) + _result_duration(result)),
            source=_source_name(queue_name=queue_name),
            timestamp=self._transcript_timestamp(offset_ticks=_result_offset(result)),
        )
        self._schedule_emit_transcript(transcript=transcript)

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
            msg = f"No recognizer for queue '{queue_name}'. Call ensure_queue() first."
            raise RuntimeError(msg)

        # Push bytes to Azure Speech SDK
        # This is non-blocking — SDK buffers internally
        try:
            push_stream.write(data)
        except Exception:
            _logger.exception("Failed to push audio to recognizer", extra={"queue_name": queue_name})

    def _transcript_timestamp(self, *, offset_ticks: int) -> datetime:
        """Resolve transcript time relative to recognition startup."""
        started_at = self._started_at or datetime.now(UTC)
        return started_at + timedelta(seconds=_ticks_to_seconds(offset_ticks))

    def _schedule_emit_transcript(self, *, transcript: TranscriptSegment) -> None:
        """Schedule asynchronous transcript emission and surface task exceptions."""
        event_loop = self._event_loop
        if not self._running or event_loop is None or event_loop.is_closed():
            return
        event_loop.call_soon_threadsafe(self._create_emission_task, transcript)

    def _create_emission_task(self, transcript: TranscriptSegment) -> None:
        """Create and retain an emission task on the service event loop."""
        if not self._running:
            return
        task = asyncio.create_task(self._emit_transcript(transcript))
        self._emission_tasks.add(task)
        task.add_done_callback(self._finish_emission_task)

    def _finish_emission_task(self, task: asyncio.Task[None]) -> None:
        """Release a completed emission task and observe unexpected failures."""
        self._emission_tasks.discard(task)
        if not task.cancelled() and (error := task.exception()) is not None:
            _logger.error("Transcript emission task failed", extra={"error": str(error)})

    async def _emit_transcript(self, transcript: TranscriptSegment) -> None:
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
                _logger.exception("Transcript callback error")

        # Push to output queue if provided
        if self._output_queue is not None:
            try:
                await self._output_queue.put(transcript)
            except Exception:
                _logger.exception("Transcript queue error")


def _ticks_to_seconds(ticks: int) -> float:
    return ticks / 10_000_000


def _source_name(*, queue_name: str) -> str:
    if queue_name == AudioQueueName.SYSTEM:
        return SOURCE_SYSTEM
    if queue_name == AudioQueueName.MICROPHONE:
        return SOURCE_MICROPHONE
    return queue_name


def _require_attr(value: object, *, attr_name: str) -> object:
    attr_value = getattr(value, attr_name, None)
    if attr_value is None:
        msg = f"Azure Speech SDK missing attribute '{attr_name}'"
        raise RuntimeError(msg)
    return attr_value


def _require_callable_attr(value: object, *, attr_name: str) -> Callable[..., object]:
    attr_value = _require_attr(value, attr_name=attr_name)
    if not callable(attr_value):
        msg = f"Azure Speech SDK attribute '{attr_name}' is not callable"
        raise TypeError(msg)
    return attr_value


def _set_speech_recognition_language(*, speech_config: object, language: str) -> None:
    language_attribute = "speech_recognition_language"
    if not hasattr(speech_config, language_attribute):
        msg = "Azure Speech config missing speech_recognition_language attribute"
        raise RuntimeError(msg)
    setattr(speech_config, language_attribute, language)


def _require_method(value: object, *, method_name: str) -> Callable[[], object]:
    method = getattr(value, method_name, None)
    if method is None or not callable(method):
        msg = f"Recognizer missing required method '{method_name}'"
        raise RuntimeError(msg)
    return method


def _require_signal(value: object, *, signal_name: str) -> _Signal:
    if not isinstance(value, _Signal):
        msg = f"Recognizer missing required signal '{signal_name}'"
        raise TypeError(msg)
    return value


def _require_recognizer(value: object) -> _Recognizer:
    recognized_signal = _require_signal(getattr(value, "recognized", None), signal_name="recognized")
    recognizing_signal = _require_signal(getattr(value, "recognizing", None), signal_name="recognizing")
    canceled_signal = _require_signal(getattr(value, "canceled", None), signal_name="canceled")
    session_stopped_signal = _require_signal(getattr(value, "session_stopped", None), signal_name="session_stopped")
    _require_method(value, method_name="start_continuous_recognition")
    _require_method(value, method_name="stop_continuous_recognition")
    return _TypedRecognizer(
        recognized=recognized_signal,
        recognizing=recognizing_signal,
        canceled=canceled_signal,
        session_stopped=session_stopped_signal,
        source=value,
    )


def _require_push_stream(value: object) -> _PushStream:
    write_method = getattr(value, "write", None)
    close_method = getattr(value, "close", None)
    if write_method is None or close_method is None or not callable(write_method) or not callable(close_method):
        msg = "Push stream missing required write/close methods"
        raise RuntimeError(msg)
    return _TypedPushStream(source=value)


def _event_result(event: object) -> object | None:
    return getattr(event, "result", None)


def _require_speech_sdk() -> object:
    if speechsdk is None:
        msg = "Azure Speech SDK not available"
        raise RuntimeError(msg)
    return speechsdk


def _result_reason_equals(*, result: object, reason_name: str) -> bool:
    sdk = _require_speech_sdk()
    reason_enum = getattr(sdk, "ResultReason", None)
    expected_reason = None if reason_enum is None else getattr(reason_enum, reason_name, None)
    if expected_reason is None:
        return False
    return getattr(result, "reason", None) == expected_reason


def _result_text(result: object) -> str:
    text_value = getattr(result, "text", "")
    return text_value if isinstance(text_value, str) else str(text_value)


def _result_offset(result: object) -> int:
    offset_value = getattr(result, "offset", 0)
    return offset_value if isinstance(offset_value, int) else 0


def _result_duration(result: object) -> int:
    duration_value = getattr(result, "duration", 0)
    return duration_value if isinstance(duration_value, int) else 0


@dataclass(frozen=True, kw_only=True, slots=True)
class _TypedRecognizer:
    recognized: _Signal
    recognizing: _Signal
    canceled: _Signal
    session_stopped: _Signal
    source: object

    def start_continuous_recognition(self) -> object:
        return _require_method(self.source, method_name="start_continuous_recognition")()

    def stop_continuous_recognition(self) -> object:
        return _require_method(self.source, method_name="stop_continuous_recognition")()


@dataclass(frozen=True, kw_only=True, slots=True)
class _TypedPushStream:
    source: object

    def write(self, data: bytes) -> object:
        write_method = getattr(self.source, "write", None)
        if write_method is None or not callable(write_method):
            msg = "Push stream write method missing"
            raise RuntimeError(msg)
        return write_method(data)

    def close(self) -> object:
        close_method = getattr(self.source, "close", None)
        if close_method is None or not callable(close_method):
            msg = "Push stream close method missing"
            raise RuntimeError(msg)
        return close_method()
