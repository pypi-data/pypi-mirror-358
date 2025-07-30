import argparse
import asyncio
import logging
import time
from collections import deque
from typing import Optional

import numpy as np
import sounddevice as sd

from xiaozhi_sdk import XiaoZhiWebsocket
from xiaozhi_sdk.config import INPUT_SERVER_AUDIO_SAMPLE_RATE

# 配置logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("xiaozhi_sdk")

# 全局状态
input_audio_buffer: deque[bytes] = deque()
is_playing_audio = False


async def handle_message(message):
    """处理接收到的消息"""
    logger.info("message received: %s", message)


async def play_assistant_audio(audio_queue: deque[bytes]):
    """播放音频流"""
    global is_playing_audio

    stream = sd.OutputStream(samplerate=INPUT_SERVER_AUDIO_SAMPLE_RATE, channels=1, dtype=np.int16)
    stream.start()
    last_audio_time = None

    while True:
        if not audio_queue:
            await asyncio.sleep(0.01)
            if last_audio_time and time.time() - last_audio_time > 1:
                is_playing_audio = False
            continue

        is_playing_audio = True
        pcm_data = audio_queue.popleft()
        stream.write(pcm_data)
        last_audio_time = time.time()


class XiaoZhiClient:
    """小智客户端类"""

    def __init__(self, mac_address: str, url: Optional[str] = None, ota_url: Optional[str] = None):
        self.mac_address = mac_address
        self.xiaozhi: Optional[XiaoZhiWebsocket] = None
        self.url = url
        self.ota_url = ota_url

    async def start(self):
        """启动客户端连接"""
        self.xiaozhi = XiaoZhiWebsocket(handle_message, url=self.url, ota_url=self.ota_url)
        await self.xiaozhi.init_connection(self.mac_address, aec=False)
        asyncio.create_task(play_assistant_audio(self.xiaozhi.output_audio_queue))

    def audio_callback(self, indata, frames, time, status):
        """音频输入回调函数"""
        pcm_data = (indata.flatten() * 32767).astype(np.int16).tobytes()
        input_audio_buffer.append(pcm_data)

    async def process_audio_input(self):
        """处理音频输入"""
        while True:
            if not input_audio_buffer:
                await asyncio.sleep(0.02)
                continue

            pcm_data = input_audio_buffer.popleft()
            if not is_playing_audio:
                await self.xiaozhi.send_audio(pcm_data)


async def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="小智SDK客户端")
    parser.add_argument("device", help="小智设备的MAC地址 (格式: XX:XX:XX:XX:XX:XX)")
    parser.add_argument("--url", help="小智服务websocket地址")
    parser.add_argument("--ota_url", help="小智OTA地址")

    args = parser.parse_args()
    logger.info("Recording... Press Ctrl+C to stop.")

    client = XiaoZhiClient(args.device, args.url, args.ota_url)
    await client.start()

    with sd.InputStream(callback=client.audio_callback, channels=1, samplerate=16000, blocksize=960):
        await client.process_audio_input()


if __name__ == "__main__":
    asyncio.run(main())
