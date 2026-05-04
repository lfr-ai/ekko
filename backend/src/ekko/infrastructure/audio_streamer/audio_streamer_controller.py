"""Controller for managing the audio streamer subprocess lifecycle."""

import asyncio
import builtins
import json
import logging
import subprocess  # nosec B404
import sys
from asyncio.subprocess import Process

from ekko.config.settings import BaseAppConfig
from ekko.infrastructure.audio_streamer.audio_streamer import AudioStreamer


class AudioStreamerController:
    """Controller for audio streamer subprocess."""

    def __init__(self, settings: BaseAppConfig):
        self.settings = settings
        self.audio_streamer = AudioStreamer(settings)  # For device info and potential future use
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
        result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, check=False)  # nosec B603 # noqa: S603

        # Log raw probe output for debugging in CI/test environments
        logging.getLogger(__name__).debug(
            "Device probe rc=%s stdout=%r stderr=%r",
            result.returncode,
            result.stdout,
            result.stderr,
        )

        if result.returncode != 0 or not result.stdout:
            logging.getLogger(__name__).debug(
                "Failed to query audio device names; return defaults. rc=%s, stderr=%s",
                result.returncode,
                (result.stderr or "").strip(),
            )
            return {"sys_name": "loopback_default", "mic_name": "mic_default"}

        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            logging.getLogger(__name__).debug("Device probe returned non-json output; using defaults")
            return {"sys_name": "loopback_default", "mic_name": "mic_default"}

    async def start(self) -> None:
        """Start audio streamer subprocess."""
        self.previous_device_names = await self._get_device_names()
        self.subprocess = await self._launch_subprocess()

    async def stop(self) -> None:
        """Stop the audio streamer subprocess."""
        if self.subprocess and self.subprocess.returncode is None:
            try:
                await self.send_command("stop")
            except Exception as e:
                logging.getLogger(__name__).debug("Failed to send stop command: %s", e)
            try:
                await asyncio.wait_for(self.subprocess.wait(), timeout=self.settings.wait_timeout_seconds)
            except builtins.TimeoutError:
                self.subprocess.terminate()
                try:
                    await asyncio.wait_for(self.subprocess.wait(), timeout=self.settings.wait_timeout_seconds)
                except builtins.TimeoutError:
                    self.subprocess.kill()
                    await self.subprocess.wait()

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
        writer.write(cmd.encode())
        await writer.drain()
        response = await reader.read(self.settings.max_read_bytes)
        writer.close()
        await writer.wait_closed()
        return response.decode().strip()
