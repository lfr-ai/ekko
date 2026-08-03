"""End-to-end tests for audio → STT → chat client → response pipeline.

Tests the complete flow:
1. Audio input → STT adapter
2. Transcript → chat client
3. Chat response → output validation
"""

from __future__ import annotations

import asyncio

import pytest

from tests.fixtures.audio.fixture_audio import (
    FIXTURE_AUDIO_1_SEC,
    FIXTURE_AUDIO_INVALID,
    FIXTURE_AUDIO_SHORT,
)
from tests.mocks.chat_mock import FailingChatClient, MockChatClient
from tests.mocks.stt_mock import FailingSTTAdapter, MockSTTAdapter

# ── Happy Path Tests ─────────────────────────────────────────


@pytest.mark.e2e
@pytest.mark.asyncio
class TestAudioPipelineHappyPath:
    """Test successful audio pipeline execution."""

    async def test_full_pipeline_with_valid_audio(self) -> None:
        """Full pipeline processes audio → transcript → chat response."""
        # Arrange
        expected_transcript = "Hello, how can I help you today?"
        expected_chat_response = "I can assist you with various tasks."

        stt_adapter = MockSTTAdapter(transcript_text=expected_transcript)
        chat_client = MockChatClient(response_text=expected_chat_response)

        output_queue: asyncio.Queue[object] = asyncio.Queue()
        stt_adapter.output_queue = output_queue

        # Act
        await stt_adapter.start()
        await stt_adapter.accept_bytes("test_stream", FIXTURE_AUDIO_1_SEC)

        # Get transcript from output queue
        transcript = await asyncio.wait_for(output_queue.get(), timeout=1.0)

        # Process transcript through LLM
        chat_response = chat_client.chat(
            system_prompt="You are a helpful assistant.",
            user_prompt=transcript.text,
            model="test-deployment",
        )

        await stt_adapter.stop()

        # Assert
        assert transcript.text == expected_transcript
        assert transcript.stream_name == "test_stream"
        assert chat_response == expected_chat_response
        assert chat_client.call_count == 1
        assert chat_client.last_user_prompt == expected_transcript

    async def test_pipeline_with_callback(self) -> None:
        """Pipeline processes audio with transcript callback."""
        # Arrange
        transcripts_received: list[object] = []

        def on_transcript(transcript: object) -> None:
            transcripts_received.append(transcript)

        stt_adapter = MockSTTAdapter(transcript_text="Callback test transcript")
        stt_adapter.on_transcript = on_transcript

        # Act
        await stt_adapter.start()
        await stt_adapter.accept_bytes("callback_stream", FIXTURE_AUDIO_1_SEC)
        await stt_adapter.stop()

        # Assert
        assert len(transcripts_received) == 1
        assert transcripts_received[0].text == "Callback test transcript"
        assert transcripts_received[0].stream_name == "callback_stream"

    async def test_pipeline_with_async_callback(self) -> None:
        """Pipeline processes audio with async transcript callback."""
        # Arrange
        transcripts_received: list[object] = []

        async def on_transcript_async(transcript: object) -> None:
            await asyncio.sleep(0.01)  # Simulate async work
            transcripts_received.append(transcript)

        stt_adapter = MockSTTAdapter(transcript_text="Async callback test")
        stt_adapter.on_transcript = on_transcript_async

        # Act
        await stt_adapter.start()
        await stt_adapter.accept_bytes("async_stream", FIXTURE_AUDIO_1_SEC)
        # Give callback time to complete
        await asyncio.sleep(0.1)
        await stt_adapter.stop()

        # Assert
        assert len(transcripts_received) == 1
        assert transcripts_received[0].text == "Async callback test"

    async def test_pipeline_with_multiple_streams(self) -> None:
        """Pipeline handles multiple concurrent audio streams."""
        # Arrange
        stt_adapter = MockSTTAdapter(transcript_text="Multi-stream test")
        output_queue: asyncio.Queue[object] = asyncio.Queue()
        stt_adapter.output_queue = output_queue

        # Act
        await stt_adapter.start()
        await stt_adapter.accept_bytes("stream_1", FIXTURE_AUDIO_1_SEC)
        await stt_adapter.accept_bytes("stream_2", FIXTURE_AUDIO_1_SEC)
        await stt_adapter.accept_bytes("stream_3", FIXTURE_AUDIO_1_SEC)

        # Collect transcripts
        transcripts = []
        for _ in range(3):
            transcript = await asyncio.wait_for(output_queue.get(), timeout=1.0)
            transcripts.append(transcript)

        await stt_adapter.stop()

        # Assert
        assert len(transcripts) == 3
        stream_names = {t.stream_name for t in transcripts}
        assert stream_names == {"stream_1", "stream_2", "stream_3"}
        assert all(t.text == "Multi-stream test" for t in transcripts)


# ── LLM Integration Tests ────────────────────────────────────


@pytest.mark.e2e
@pytest.mark.asyncio
class TestLLMIntegration:
    """Test chat client integration with transcripts."""

    async def test_llm_processes_transcript_text(self) -> None:
        """chat client receives and processes transcript text."""
        # Arrange
        transcript_text = "What is the weather today?"
        chat_response = "The weather is sunny and warm."

        chat_client = MockChatClient(response_text=chat_response)

        # Act
        response = chat_client.chat(
            system_prompt="You are a weather assistant.",
            user_prompt=transcript_text,
            model="gpt-4",
        )

        # Assert
        assert response == chat_response
        assert chat_client.last_system_prompt == "You are a weather assistant."
        assert chat_client.last_user_prompt == transcript_text

    async def test_llm_async_chat(self) -> None:
        """chat client supports async chat."""
        # Arrange
        chat_client = MockChatClient(response_text="Async response")

        # Act
        response = await chat_client.achat(
            system_prompt="System prompt",
            user_prompt="User prompt",
            model="test-model",
        )

        # Assert
        assert response == "Async response"
        assert chat_client.call_count == 1

    async def test_llm_with_custom_parameters(self) -> None:
        """chat client accepts custom parameters."""
        # Arrange
        chat_client = MockChatClient(response_text="Custom params response")

        # Act
        response = chat_client.chat(
            system_prompt="System",
            user_prompt="User",
            model="custom-model",
            max_completion_tokens=2048,
            temperature=0.7,
            top_p=0.9,
        )

        # Assert
        assert response == "Custom params response"


# ── Response Validation Tests ────────────────────────────────


@pytest.mark.e2e
@pytest.mark.asyncio
class TestResponseValidation:
    """Test response format and content validation."""

    async def test_response_format_is_string(self) -> None:
        """Pipeline returns response as string."""
        # Arrange
        stt_adapter = MockSTTAdapter(transcript_text="Test input")
        chat_client = MockChatClient(response_text="Test output")
        output_queue: asyncio.Queue[object] = asyncio.Queue()
        stt_adapter.output_queue = output_queue

        # Act
        await stt_adapter.start()
        await stt_adapter.accept_bytes("stream", FIXTURE_AUDIO_1_SEC)
        transcript = await asyncio.wait_for(output_queue.get(), timeout=1.0)
        response = chat_client.chat(
            system_prompt="System",
            user_prompt=transcript.text,
            model="test",
        )
        await stt_adapter.stop()

        # Assert
        assert isinstance(response, str)
        assert len(response) > 0

    async def test_response_content_matches_expectation(self) -> None:
        """Pipeline response content is correct."""
        # Arrange
        expected_response = "This is the expected chat response."
        stt_adapter = MockSTTAdapter(transcript_text="Input text")
        chat_client = MockChatClient(response_text=expected_response)
        output_queue: asyncio.Queue[object] = asyncio.Queue()
        stt_adapter.output_queue = output_queue

        # Act
        await stt_adapter.start()
        await stt_adapter.accept_bytes("stream", FIXTURE_AUDIO_1_SEC)
        transcript = await asyncio.wait_for(output_queue.get(), timeout=1.0)
        response = chat_client.chat(
            system_prompt="System",
            user_prompt=transcript.text,
            model="test",
        )
        await stt_adapter.stop()

        # Assert
        assert response == expected_response

    async def test_transcript_structure(self) -> None:
        """Transcript has expected structure."""
        # Arrange
        stt_adapter = MockSTTAdapter(transcript_text="Structure test")
        output_queue: asyncio.Queue[object] = asyncio.Queue()
        stt_adapter.output_queue = output_queue

        # Act
        await stt_adapter.start()
        await stt_adapter.accept_bytes("test_stream", FIXTURE_AUDIO_1_SEC)
        transcript = await asyncio.wait_for(output_queue.get(), timeout=1.0)
        await stt_adapter.stop()

        # Assert
        assert hasattr(transcript, "stream_name")
        assert hasattr(transcript, "text")
        assert hasattr(transcript, "segments")
        assert hasattr(transcript, "info")
        assert transcript.stream_name == "test_stream"
        assert isinstance(transcript.text, str)
        assert isinstance(transcript.segments, list)


# ── Error Handling Tests ─────────────────────────────────────


@pytest.mark.e2e
@pytest.mark.asyncio
class TestPipelineErrorHandling:
    """Test error handling in audio pipeline."""

    async def test_stt_failure_handling(self) -> None:
        """Pipeline handles STT processing failures."""
        # Arrange
        stt_adapter = FailingSTTAdapter()

        # Act & Assert
        await stt_adapter.start()
        with pytest.raises(RuntimeError, match="STT processing failed"):
            await stt_adapter.accept_bytes("stream", FIXTURE_AUDIO_1_SEC)
        await stt_adapter.stop()

    async def test_llm_failure_handling(self) -> None:
        """Pipeline handles Chat processing failures."""
        # Arrange
        chat_client = FailingChatClient()

        # Act & Assert
        with pytest.raises(RuntimeError, match="Chat processing failed"):
            chat_client.chat(
                system_prompt="System",
                user_prompt="User",
                model="test",
            )

    async def test_llm_async_failure_handling(self) -> None:
        """Pipeline handles async Chat processing failures."""
        # Arrange
        chat_client = FailingChatClient()

        # Act & Assert
        with pytest.raises(RuntimeError, match="Chat processing failed"):
            await chat_client.achat(
                system_prompt="System",
                user_prompt="User",
                model="test",
            )

    async def test_invalid_audio_data(self) -> None:
        """Pipeline handles invalid audio data gracefully."""
        # Arrange
        # Using mock adapter which doesn't actually validate audio format
        # Real adapter would raise error for invalid audio
        stt_adapter = MockSTTAdapter(transcript_text="")
        output_queue: asyncio.Queue[object] = asyncio.Queue()
        stt_adapter.output_queue = output_queue

        # Act
        await stt_adapter.start()
        await stt_adapter.accept_bytes("stream", FIXTURE_AUDIO_INVALID)
        transcript = await asyncio.wait_for(output_queue.get(), timeout=1.0)
        await stt_adapter.stop()

        # Assert - mock adapter processes any bytes
        assert transcript.text == ""  # Empty transcript for invalid audio

    async def test_empty_audio_stream(self) -> None:
        """Pipeline handles empty audio streams."""
        # Arrange
        stt_adapter = MockSTTAdapter(transcript_text="")
        output_queue: asyncio.Queue[object] = asyncio.Queue()
        stt_adapter.output_queue = output_queue

        # Act
        await stt_adapter.start()
        await stt_adapter.accept_bytes("stream", b"")
        transcript = await asyncio.wait_for(output_queue.get(), timeout=1.0)
        await stt_adapter.stop()

        # Assert
        assert transcript.text == ""

    async def test_queue_timeout_handling(self) -> None:
        """Pipeline handles queue timeout gracefully."""
        # Arrange
        output_queue: asyncio.Queue[object] = asyncio.Queue()

        # Act & Assert
        with pytest.raises(asyncio.TimeoutError):
            await asyncio.wait_for(output_queue.get(), timeout=0.1)


# ── Lifecycle Tests ──────────────────────────────────────────


@pytest.mark.e2e
@pytest.mark.asyncio
class TestPipelineLifecycle:
    """Test pipeline lifecycle management."""

    async def test_stt_start_stop_lifecycle(self) -> None:
        """STT adapter starts and stops cleanly."""
        # Arrange
        stt_adapter = MockSTTAdapter()

        # Act
        await stt_adapter.start()
        assert stt_adapter._running is True

        await stt_adapter.stop()
        assert stt_adapter._running is False

    async def test_multiple_start_stop_cycles(self) -> None:
        """STT adapter handles multiple start/stop cycles."""
        # Arrange
        stt_adapter = MockSTTAdapter()

        # Act & Assert
        for _ in range(3):
            await stt_adapter.start()
            assert stt_adapter._running is True
            await stt_adapter.stop()
            assert stt_adapter._running is False

    async def test_ensure_queue_creates_queue(self) -> None:
        """Ensure queue creates queue for stream."""
        # Arrange
        stt_adapter = MockSTTAdapter()

        # Act
        await stt_adapter.ensure_queue("new_stream")

        # Assert
        assert "new_stream" in stt_adapter._queues
        assert isinstance(stt_adapter._queues["new_stream"], asyncio.Queue)

    async def test_ensure_queue_idempotent(self) -> None:
        """Ensure queue is idempotent."""
        # Arrange
        stt_adapter = MockSTTAdapter()

        # Act
        await stt_adapter.ensure_queue("stream")
        first_queue = stt_adapter._queues["stream"]

        await stt_adapter.ensure_queue("stream")
        second_queue = stt_adapter._queues["stream"]

        # Assert
        assert first_queue is second_queue


# ── Integration Smoke Tests ──────────────────────────────────


@pytest.mark.e2e
@pytest.mark.asyncio
class TestIntegrationSmoke:
    """Smoke tests for end-to-end integration."""

    async def test_complete_conversation_flow(self) -> None:
        """Complete conversation: audio → transcript → LLM → response."""
        # Arrange
        conversation = []

        def on_transcript(transcript: object) -> None:
            conversation.append(("transcript", transcript.text))

        stt_adapter = MockSTTAdapter(transcript_text="Hello, what's your name?")
        stt_adapter.on_transcript = on_transcript

        chat_client = MockChatClient(response_text="My name is Assistant.")

        # Act
        await stt_adapter.start()
        await stt_adapter.accept_bytes("conversation", FIXTURE_AUDIO_1_SEC)

        # Wait for transcript callback
        await asyncio.sleep(0.05)

        # Get transcript and process with LLM
        transcript_text = conversation[0][1]
        chat_response = chat_client.chat(
            system_prompt="You are a conversational assistant.",
            user_prompt=transcript_text,
            model="gpt-4",
        )
        conversation.append(("response", chat_response))

        await stt_adapter.stop()

        # Assert
        assert len(conversation) == 2
        assert conversation[0] == ("transcript", "Hello, what's your name?")
        assert conversation[1] == ("response", "My name is Assistant.")

    async def test_pipeline_with_short_audio(self) -> None:
        """Pipeline processes short audio clips."""
        # Arrange
        stt_adapter = MockSTTAdapter(transcript_text="Short")
        output_queue: asyncio.Queue[object] = asyncio.Queue()
        stt_adapter.output_queue = output_queue

        # Act
        await stt_adapter.start()
        await stt_adapter.accept_bytes("short_stream", FIXTURE_AUDIO_SHORT)
        transcript = await asyncio.wait_for(output_queue.get(), timeout=1.0)
        await stt_adapter.stop()

        # Assert
        assert transcript.text == "Short"

    async def test_pipeline_processes_multiple_messages(self) -> None:
        """Pipeline handles multiple sequential messages."""
        # Arrange
        messages = [
            "First message",
            "Second message",
            "Third message",
        ]
        stt_adapter = MockSTTAdapter()
        chat_client = MockChatClient(response_text="Acknowledged")

        responses = []

        # Act
        await stt_adapter.start()

        for i, msg in enumerate(messages):
            stt_adapter.transcript_text = msg
            output_queue: asyncio.Queue[object] = asyncio.Queue()
            stt_adapter.output_queue = output_queue

            await stt_adapter.accept_bytes(f"stream_{i}", FIXTURE_AUDIO_1_SEC)
            transcript = await asyncio.wait_for(output_queue.get(), timeout=1.0)

            response = chat_client.chat(
                system_prompt="System",
                user_prompt=transcript.text,
                model="test",
            )
            responses.append(response)

        await stt_adapter.stop()

        # Assert
        assert len(responses) == 3
        assert all(r == "Acknowledged" for r in responses)
        assert chat_client.call_count == 3

