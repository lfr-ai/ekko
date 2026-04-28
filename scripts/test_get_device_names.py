import sys

sys.path.insert(0, 'src')
import asyncio

from voice.config.config import Config
from voice.models.audio_streamer.audio_streamer_controller import (
    AudioStreamerController,
)


async def main():
    cfg = Config()
    c = AudioStreamerController(cfg)
    names = await c._get_device_names()
    print('DEVICE NAMES:', names)

asyncio.run(main())
