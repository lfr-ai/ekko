"""Controller for managing the audio streamer subprocess lifecycle."""

from __future__ import annotations

import asyncio
import builtins
import json
import logging
import subprocess  # nosec B404
import sys
from typing import TYPE_CHECKING

from ekko.infrastructure.metrics import AUDIO_STREAMS_ACTIVE

if TYPE_CHECKING:
    from asyncio.subprocess import Process

    from ekko.config.base import BaseAppConfig

_logger = logging.getLogger(__name__)


class AudioStreamerController:
    """Controller for audio streamer subprocess."""

    def __init__(self, settings: BaseAppConfig):
        self.settings = settings
        self.subprocess: Process | None = None
        self.previous_device_names: dict[str, str] | None = None

    async def _launch_subprocess(self) -> Process:
        """Launch the audio-streamer TCP server subprocess."""
        return await asyncio.create_subprocess_exec(
            sys.executable, "-m", self.settings.audio_streamer_tcp_server_module_path
        )

    async def _get_device_names(self) -> dict[str, str]:
        """Detect system and microphone device names for change checking."""
        code = (
            "import json\n"
            "import pyaudiowpatch as pyaudio\n"
            "pa = getattr(pyaudio, 'Pyaudio', None) or pyaudio.PyAudio()\n"
            "sys_name = pa.get_default_wasapi_loopback().get('name','loopback_default')\n"
            "mic_name = pa.get_default_input_device_info().get('name','mic_default')\n"
            "pa.terminate()\n"
            "print(json.dumps({'sys_name': sys_name,'mic_name': mic_name}))"
        )
        # Running a short subprocess to query device names; this is executed
        # with a list of args (no shell) to avoid shell injection risks.  # nosec B603
        result = await asyncio.to_thread(
            subprocess.run,  # nosec B603
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode != 0 or not result.stdout:
            _logger.debug(
                "Device probe failed",
                extra={"return_code": result.returncode, "stderr": (result.stderr or "").strip()},
            )
            return {"sys_name": "loopback_default", "mic_name": "mic_default"}

        try:
            device_names = json.loads(result.stdout)
        except json.JSONDecodeError:
            _logger.debug("Device probe returned invalid JSON", extra={"stdout": result.stdout})
            return {"sys_name": "loopback_default", "mic_name": "mic_default"}

        _logger.debug(
            "Device probe completed",
            extra={"sys_name": device_names.get("sys_name"), "mic_name": device_names.get("mic_name")},
        )
        return device_names

    async def start(self) -> None:
        """Start audio streamer subprocess."""
        self.previous_device_names = await self._get_device_names()
        self.subprocess = await self._launch_subprocess()
        AUDIO_STREAMS_ACTIVE.inc()

    async def stop(self) -> None:
        """Stop the audio streamer subprocess."""
        if self.subprocess and self.subprocess.returncode is None:
            try:
                await self.send_command("stop")
            except Exception as exc:  # noqa: BLE001  # best-effort stop before force-terminate
                _logger.debug("Failed to send stop command", extra={"error": str(exc)})
            try:
                await asyncio.wait_for(self.subprocess.wait(), timeout=self.settings.wait_timeout_seconds)
            except builtins.TimeoutError:
                self.subprocess.terminate()
                try:
                    await asyncio.wait_for(self.subprocess.wait(), timeout=self.settings.wait_timeout_seconds)
                except builtins.TimeoutError:
                    self.subprocess.kill()
                    await self.subprocess.wait()
            AUDIO_STREAMS_ACTIVE.dec()

    async def device_check(self) -> None:
        """Restart subprocess if system/mic devices have changed."""
        current_device_names = await self._get_device_names()
        if current_device_names != self.previous_device_names:
            await self.stop()
            self.subprocess = await self._launch_subprocess()
            self.previous_device_names = current_device_names

    async def send_command(self, cmd: str) -> str:
        """Send a command to the audio-streamer subprocess via TCP."""
        reader, writer = await asyncio.open_connection(self.settings.host, self.settings.audio_streamer_tcp_port)
        try:
            writer.write(cmd.encode())
            await writer.drain()
            response = await reader.read(self.settings.max_read_bytes)
            return response.decode().strip()
        finally:
            writer.close()
            await writer.wait_closed()
