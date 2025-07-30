import argparse
import asyncio
import re
import time
from collections import deque

import numpy as np
import sounddevice as sd

from xiaozhi_sdk import XiaoZhiWebsocket
from xiaozhi_sdk.config import INPUT_SERVER_AUDIO_SAMPLE_RATE

input_audio: deque[bytes] = deque()

is_play_audio = False


async def message_handler_callback(message):
    print("message received:", message)


async def assistant_audio_play(audio_queue):
    global is_play_audio
    # 创建一个持续播放的流
    stream = sd.OutputStream(samplerate=INPUT_SERVER_AUDIO_SAMPLE_RATE, channels=1, dtype=np.int16)
    stream.start()
    last_time = None

    while True:

        if not audio_queue:
            await asyncio.sleep(0.01)
            if last_time and time.time() - last_time > 1:
                is_play_audio = False
            continue

        is_play_audio = True
        pcm_data = audio_queue.popleft()
        stream.write(pcm_data)
        last_time = time.time()


class Client:
    def __init__(self, mac_address, url=None, ota_url=None):
        self.mac_address = mac_address
        self.xiaozhi = None
        self.url = url
        self.ota_url = ota_url

    async def start(self):
        self.xiaozhi = XiaoZhiWebsocket(message_handler_callback, url=self.url, ota_url=self.ota_url)
        await self.xiaozhi.init_connection(self.mac_address, aec=False)
        asyncio.create_task(assistant_audio_play(self.xiaozhi.audio_queue))

    def callback_func(self, indata, frames, time, status):
        pcm = (indata.flatten() * 32767).astype(np.int16).tobytes()
        input_audio.append(pcm)

    async def process_audio(self):
        while True:
            if not input_audio:
                await asyncio.sleep(0.02)
                continue
            pcm = input_audio.popleft()
            if not is_play_audio:
                await self.xiaozhi.send_audio(pcm)


def mac_address(string):
    """验证是否为有效的MAC地址"""
    if re.fullmatch(r"([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}", string):
        return string
    else:
        raise argparse.ArgumentTypeError(f"无效的MAC地址格式: '{string}'")


async def main():
    parser = argparse.ArgumentParser(description="这是一个小智SDK。")
    parser.add_argument("device", type=mac_address, help="你的小智设备的MAC地址 (格式: XX:XX:XX:XX:XX:XX)")
    parser.add_argument("--url", help="小智服务 websocket 地址")
    parser.add_argument("--ota_url", help="小智 OTA 地址")

    args = parser.parse_args()
    client = Client(args.device, args.url, args.ota_url)
    await client.start()
    await asyncio.sleep(2)

    with sd.InputStream(callback=client.callback_func, channels=1, samplerate=16000, blocksize=960):
        print("Recording... Press Ctrl+C to stop.")
        await client.process_audio()  # 持续处理音频


if __name__ == "__main__":
    asyncio.run(main())
