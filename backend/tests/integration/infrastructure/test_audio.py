"""Integration tests for audio streamer controller."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

if TYPE_CHECKING:
    from ekko.config.settings import BaseAppConfig

pytestmark = pytest.mark.integration


@pytest.fixture
def mock_audio_streamer():
    """Mock AudioStreamer for testing."""
    with patch("ekko.infrastructure.audio_streamer.audio_streamer_controller.AudioStreamer") as mock:
        yield mock.return_value


@pytest.mark.asyncio
async def test_audio_controller_start_stop(
    integration_settings: BaseAppConfig,
    mock_audio_streamer: MagicMock,
) -> None:
    """Test starting and stopping the audio controller."""
    from ekko.infrastructure.audio_streamer.audio_streamer_controller import AudioStreamerController

    with (
        patch(
            "ekko.infrastructure.audio_streamer.audio_streamer_controller.asyncio.create_subprocess_exec"
        ) as mock_exec,
        patch.object(AudioStreamerController, "_get_device_names", new_callable=AsyncMock) as mock_get_devices,
    ):
        # Mock subprocess
        mock_process = MagicMock()
        mock_process.returncode = None
        mock_process.wait = AsyncMock()
        mock_process.terminate = MagicMock()
        mock_process.kill = MagicMock()
        mock_exec.return_value = mock_process

        # Mock device names
        mock_get_devices.return_value = {"sys_name": "test_system", "mic_name": "test_mic"}

        controller = AudioStreamerController(integration_settings)

        await controller.start()
        assert controller.subprocess is not None
        assert controller.previous_device_names is not None

        await controller.stop()


@pytest.mark.asyncio
async def test_audio_controller_send_command(
    integration_settings: BaseAppConfig,
    mock_audio_streamer: MagicMock,
) -> None:
    """Test sending commands to audio streamer subprocess."""
    from ekko.infrastructure.audio_streamer.audio_streamer_controller import AudioStreamerController

    with (
        patch(
            "ekko.infrastructure.audio_streamer.audio_streamer_controller.asyncio.create_subprocess_exec"
        ) as mock_exec,
        patch.object(AudioStreamerController, "_get_device_names", new_callable=AsyncMock) as mock_get_devices,
        patch("ekko.infrastructure.audio_streamer.audio_streamer_controller.asyncio.open_connection") as mock_conn,
    ):
        # Mock subprocess
        mock_process = MagicMock()
        mock_process.returncode = None
        mock_exec.return_value = mock_process

        # Mock device names
        mock_get_devices.return_value = {"sys_name": "test_system", "mic_name": "test_mic"}

        # Mock TCP connection
        mock_reader = AsyncMock()
        mock_reader.read = AsyncMock(return_value=b"OK")
        mock_writer = MagicMock()
        mock_writer.drain = AsyncMock()
        mock_writer.wait_closed = AsyncMock()
        mock_conn.return_value = (mock_reader, mock_writer)

        controller = AudioStreamerController(integration_settings)
        await controller.start()

        response = await controller.send_command("test_command")

        assert response == "OK"
        mock_writer.write.assert_called_once_with(b"test_command")


@pytest.mark.asyncio
async def test_audio_controller_device_check_no_change(
    integration_settings: BaseAppConfig,
    mock_audio_streamer: MagicMock,
) -> None:
    """Test device check when devices haven't changed."""
    from ekko.infrastructure.audio_streamer.audio_streamer_controller import AudioStreamerController

    with (
        patch(
            "ekko.infrastructure.audio_streamer.audio_streamer_controller.asyncio.create_subprocess_exec"
        ) as mock_exec,
        patch.object(AudioStreamerController, "_get_device_names", new_callable=AsyncMock) as mock_get_devices,
    ):
        # Mock subprocess
        mock_process = MagicMock()
        mock_process.returncode = None
        mock_exec.return_value = mock_process

        # Mock device names (same on both calls)
        mock_get_devices.return_value = {"sys_name": "test_system", "mic_name": "test_mic"}

        controller = AudioStreamerController(integration_settings)
        await controller.start()

        original_subprocess = controller.subprocess

        # Check devices (should not restart)
        await controller.device_check()

        assert controller.subprocess is original_subprocess


@pytest.mark.asyncio
async def test_audio_controller_device_check_with_change(
    integration_settings: BaseAppConfig,
    mock_audio_streamer: MagicMock,
) -> None:
    """Test device check when devices have changed."""
    from ekko.infrastructure.audio_streamer.audio_streamer_controller import AudioStreamerController

    with (
        patch(
            "ekko.infrastructure.audio_streamer.audio_streamer_controller.asyncio.create_subprocess_exec"
        ) as mock_exec,
        patch.object(AudioStreamerController, "_get_device_names", new_callable=AsyncMock) as mock_get_devices,
        patch.object(AudioStreamerController, "send_command", new_callable=AsyncMock) as _mock_send_cmd,
    ):
        # Mock subprocess - create different instances for each call
        mock_process1 = MagicMock()
        mock_process1.returncode = None
        mock_process1.wait = AsyncMock()

        mock_process2 = MagicMock()
        mock_process2.returncode = None
        mock_process2.wait = AsyncMock()

        mock_exec.side_effect = [mock_process1, mock_process2]

        # First call returns original devices, second call returns changed devices
        mock_get_devices.side_effect = [
            {"sys_name": "test_system", "mic_name": "test_mic"},
            {"sys_name": "new_system", "mic_name": "new_mic"},
        ]

        controller = AudioStreamerController(integration_settings)
        await controller.start()

        original_subprocess = controller.subprocess
        assert original_subprocess is mock_process1

        # Check devices (should restart due to change)
        await controller.device_check()

        assert controller.subprocess is mock_process2
        assert controller.subprocess is not original_subprocess
        assert controller.previous_device_names == {"sys_name": "new_system", "mic_name": "new_mic"}


@pytest.mark.asyncio
async def test_audio_controller_get_device_names_fallback(
    integration_settings: BaseAppConfig,
    mock_audio_streamer: MagicMock,
) -> None:
    """Test fallback behavior when device names cannot be queried."""
    from ekko.infrastructure.audio_streamer.audio_streamer_controller import AudioStreamerController

    with patch("ekko.infrastructure.audio_streamer.audio_streamer_controller.subprocess.run") as mock_run:
        # Mock failed subprocess call
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "Error querying devices"
        mock_run.return_value = mock_result

        controller = AudioStreamerController(integration_settings)
        device_names = await controller._get_device_names()

        # Should return defaults
        assert device_names == {"sys_name": "loopback_default", "mic_name": "mic_default"}


@pytest.mark.asyncio
async def test_audio_controller_get_device_names_json_error(
    integration_settings: BaseAppConfig,
    mock_audio_streamer: MagicMock,
) -> None:
    """Test fallback when device query returns invalid JSON."""
    from ekko.infrastructure.audio_streamer.audio_streamer_controller import AudioStreamerController

    with patch("ekko.infrastructure.audio_streamer.audio_streamer_controller.subprocess.run") as mock_run:
        # Mock subprocess with invalid JSON
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "not valid json"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        controller = AudioStreamerController(integration_settings)
        device_names = await controller._get_device_names()

        # Should return defaults
        assert device_names == {"sys_name": "loopback_default", "mic_name": "mic_default"}


@pytest.mark.asyncio
async def test_audio_controller_stop_timeout_graceful(
    integration_settings: BaseAppConfig,
    mock_audio_streamer: MagicMock,
) -> None:
    """Test graceful stop with timeout."""
    from ekko.infrastructure.audio_streamer.audio_streamer_controller import AudioStreamerController

    with (
        patch(
            "ekko.infrastructure.audio_streamer.audio_streamer_controller.asyncio.create_subprocess_exec"
        ) as mock_exec,
        patch.object(AudioStreamerController, "_get_device_names", new_callable=AsyncMock) as mock_get_devices,
        patch.object(AudioStreamerController, "send_command", new_callable=AsyncMock) as mock_send_cmd,
    ):
        # Mock subprocess
        mock_process = MagicMock()
        mock_process.returncode = None
        mock_process.wait = AsyncMock()
        mock_exec.return_value = mock_process

        mock_get_devices.return_value = {"sys_name": "test_system", "mic_name": "test_mic"}

        controller = AudioStreamerController(integration_settings)
        await controller.start()

        await controller.stop()

        # Verify stop command was sent
        mock_send_cmd.assert_called_once_with("stop")
        mock_process.wait.assert_called()


@pytest.mark.asyncio
async def test_audio_controller_stop_timeout_terminate(
    integration_settings: BaseAppConfig,
    mock_audio_streamer: MagicMock,
) -> None:
    """Test forced termination when graceful stop times out."""
    from ekko.infrastructure.audio_streamer.audio_streamer_controller import AudioStreamerController

    with (
        patch(
            "ekko.infrastructure.audio_streamer.audio_streamer_controller.asyncio.create_subprocess_exec"
        ) as mock_exec,
        patch.object(AudioStreamerController, "_get_device_names", new_callable=AsyncMock) as mock_get_devices,
        patch.object(AudioStreamerController, "send_command", new_callable=AsyncMock) as _mock_send_cmd,
        patch("ekko.infrastructure.audio_streamer.audio_streamer_controller.asyncio.wait_for") as mock_wait_for,
    ):
        # Mock subprocess
        mock_process = MagicMock()
        mock_process.returncode = None
        mock_process.terminate = MagicMock()
        mock_process.kill = MagicMock()
        # wait_for is fully mocked in this test, so a sync wait stub avoids
        # creating coroutine objects that would never be awaited.
        mock_process.wait = MagicMock(return_value=None)
        mock_exec.return_value = mock_process

        mock_get_devices.return_value = {"sys_name": "test_system", "mic_name": "test_mic"}

        # First wait_for times out, second one succeeds
        import builtins

        mock_wait_for.side_effect = [builtins.TimeoutError(), None]

        controller = AudioStreamerController(integration_settings)
        await controller.start()

        await controller.stop()

        # Verify terminate was called after timeout
        mock_process.terminate.assert_called_once()
