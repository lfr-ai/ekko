"""Probe the default Windows loopback and microphone audio devices."""

from __future__ import annotations

import subprocess
import sys

_PROBE_CODE = (
    "import json\n"
    "import pyaudiowpatch as pyaudio\n"
    "pa = getattr(pyaudio, 'Pyaudio', None) or pyaudio.PyAudio()\n"
    "sys_name = pa.get_default_wasapi_loopback().get('name','loopback_default')\n"
    "mic_name = pa.get_default_input_device_info().get('name','mic_default')\n"
    "pa.terminate()\n"
    "print(json.dumps({'sys_name': sys_name,'mic_name': mic_name}))"
)


def main() -> int:
    """Run the isolated device probe and return its process status."""
    result = subprocess.run(  # nosec B603
        [sys.executable, "-c", _PROBE_CODE],
        capture_output=True,
        text=True,
        check=False,
    )
    print("RC=", result.returncode)
    print("STDOUT=", repr(result.stdout))
    print("STDERR=", repr(result.stderr))
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
