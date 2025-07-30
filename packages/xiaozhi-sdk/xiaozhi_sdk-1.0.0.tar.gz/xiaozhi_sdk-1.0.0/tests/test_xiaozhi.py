import asyncio
import os
import sys
import time

import numpy as np
import pytest
import sounddevice as sd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from xiaozhi_sdk import XiaoZhiWebsocket
from xiaozhi_sdk.utils import read_audio_file


async def assistant_audio_play(audio_queue):
    # 创建一个持续播放的流
    stream = sd.OutputStream(samplerate=16000, channels=1, dtype=np.int16)
    stream.start()
    last_time = None
    while True:
        if not audio_queue:
            await asyncio.sleep(0.01)
            if last_time and time.time() - last_time > 1:
                break

            continue

        pcm_data = audio_queue.popleft()
        stream.write(pcm_data)
        last_time = time.time()

    stream.stop()
    stream.close()


def mcp_tool_func():
    def mcp_take_photo(data):
        return open("./file/leijun.jpg", "rb")

    def mcp_get_device_status(data):
        return {
            "audio_speaker": {"volume": 80},
            "screen": {"brightness": 75, "theme": "light"},
            "network": {"type": "wifi", "ssid": "wifi名称", "signal": "strong"},
        }

    def mcp_set_volume(data):
        return {}

    mcp_tool_func = {
        "set_volume": mcp_set_volume,
        "get_device_status": mcp_get_device_status,
        "take_photo": mcp_take_photo,
    }
    return mcp_tool_func


async def message_handler_callback(message):
    print("message received:", message)


MAC_ADDR = "fc:01:2c:c9:2b:31"
# URL = "ws://120.79.156.134:8380"
URL = None


@pytest.mark.asyncio
async def test_main():
    xiaozhi = XiaoZhiWebsocket(message_handler_callback, url=URL)
    await xiaozhi.set_mcp_tool_callback(mcp_tool_func())
    await xiaozhi.init_connection(MAC_ADDR)

    # say hellow
    for pcm in read_audio_file("./file/say_hello.wav"):
        await xiaozhi.send_audio(pcm)
    await xiaozhi.send_silence_audio()
    await assistant_audio_play(xiaozhi.audio_queue)

    # say take photo
    for pcm in read_audio_file("./file/take_photo.wav"):
        await xiaozhi.send_audio(pcm)
    await xiaozhi.send_silence_audio()
    await assistant_audio_play(xiaozhi.audio_queue)

    await xiaozhi.close()
