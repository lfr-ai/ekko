import subprocess
import sys

code = (
    "import json\n"
    "import pyaudiowpatch as pyaudio\n"
    "pa = getattr(pyaudio, 'Pyaudio', None) or pyaudio.PyAudio()\n"
    "sys_name = pa.get_default_wasapi_loopback().get('name','loopback_default')\n"
    "mic_name = pa.get_default_input_device_info().get('name','mic_default')\n"
    "pa.terminate()\n"
    "print(json.dumps({'sys_name': sys_name,'mic_name': mic_name}))"
)

r = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)  # nosec B603
print("RC=", r.returncode)
print("STDOUT=", repr(r.stdout))
print("STDERR=", repr(r.stderr))
