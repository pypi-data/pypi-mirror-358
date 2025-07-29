import asyncio
import json
import os
import sys
import time
import wave

import numpy as np
import sounddevice as sd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from xiaozhi_sdk import XiaoZhiWebsocket
from xiaozhi_sdk.utils import read_audio_file

play_audio_over = asyncio.Event()


async def assistant_audio_play(audio_queue):
    # 创建一个持续播放的流
    stream = sd.OutputStream(samplerate=16000, channels=1, dtype=np.int16)
    stream.start()
    last_time = None
    while True:
        if not audio_queue:
            await asyncio.sleep(0.01)
            if last_time and time.time() - last_time > 3:
                break

            continue

        pcm_data = audio_queue.popleft()
        stream.write(pcm_data)
        last_time = time.time()

    play_audio_over.set()
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





async def main():
    async def message_handler_callback(message):
        print("message received:", message)

    MAC_ADDR = "fc:01:2c:c9:2b:31"
    url = "ws://120.79.156.134:8380"
    url = None
    xiaozhi = XiaoZhiWebsocket(message_handler_callback, url=url)
    await xiaozhi.set_mcp_tool_callback(mcp_tool_func())
    await xiaozhi.init_connection(MAC_ADDR)
    asyncio.create_task(assistant_audio_play(xiaozhi.audio_queue))
    await asyncio.sleep(1)
    
    # 使用新的音频读取函数
    for pcm in read_audio_file("./file/take_photo.wav"):
    # for pcm in read_audio_file("./file/say_hello.wav"):
        await xiaozhi.send_audio(pcm)

    # 发送静音数据
    await xiaozhi.send_silence_audio()
    await asyncio.wait_for(play_audio_over.wait(), timeout=20.0)
    await xiaozhi.close()


if __name__ == "__main__":
    asyncio.run(main())
