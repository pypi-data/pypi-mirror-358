import asyncio
import json
import os
import uuid
import wave
from collections import deque
from typing import Any, Callable, Dict

import websockets

from xiaozhi_sdk.config import INPUT_SERVER_AUDIO_SAMPLE_RATE, WSS_URL
from xiaozhi_sdk.iot import OtaDevice
from xiaozhi_sdk.mcp import McpTool
from xiaozhi_sdk.opus import AudioOpus
from xiaozhi_sdk.utils import get_wav_info, read_audio_file


class XiaoZhiWebsocket(McpTool):

    def __init__(self, message_handler_callback=None, url=None, ota_url=None, audio_sample_rate=16000, audio_channels=1):
        super().__init__()
        self.url = url or WSS_URL
        self.ota_url = ota_url
        self.audio_sample_rate = audio_sample_rate
        self.audio_channels = audio_channels
        self.audio_opus = AudioOpus(audio_sample_rate, audio_channels)
        self.client_id = str(uuid.uuid4())
        self.mac_addr = None
        self.message_handler_callback = message_handler_callback

        self.hello_received = asyncio.Event()
        self.session_id = ""
        self.audio_queue = deque()
        self.websocket = None
        self.message_handler_task = None
        self.ota = None

    async def send_hello(self, aec: bool):
        hello_message = {
            "type": "hello",
            "version": 1,
            "features": {"aec": aec, "mcp": True},
            "transport": "websocket",
            "audio_params": {
                "format": "opus",
                "sample_rate": INPUT_SERVER_AUDIO_SAMPLE_RATE,
                "channels": 1,
                "frame_duration": 60,
            },
        }
        await self.websocket.send(json.dumps(hello_message))
        await asyncio.wait_for(self.hello_received.wait(), timeout=10.0)

    async def start_listen(self):
        listen_message = {"session_id": self.session_id, "type": "listen", "state": "start", "mode": "realtime"}
        await self.websocket.send(json.dumps(listen_message))

    async def set_mcp_tool_callback(self, tool_func: Dict[str, Callable[..., Any]]):
        self.tool_func = tool_func

    async def activate_iot_device(self, ota_info):
        if ota_info.get("activation"):
            await self.send_demo_audio()
            challenge = ota_info["activation"]["challenge"]
            await asyncio.sleep(3)
            for _ in range(10):
                if await self.ota.check_activate(challenge):
                    break
                await asyncio.sleep(3)

    async def init_connection(self, mac_addr: str, aec: bool = False):
        self.mac_addr = mac_addr
        self.ota = OtaDevice(self.mac_addr, self.client_id, self.ota_url)
        ota_info = await self.ota.activate_device()

        headers = {
            "Authorization": "Bearer test-token",
            "Protocol-Version": "1",
            "Device-Id": mac_addr,
            "Client-Id": self.client_id,
        }

        self.websocket = await websockets.connect(uri=self.url, additional_headers=headers)
        self.message_handler_task = asyncio.create_task(self.message_handler())
        await self.send_hello(aec)
        await self.start_listen()
        asyncio.create_task(self.activate_iot_device(ota_info))

    async def send_demo_audio(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        wav_path = os.path.join(current_dir, "../file/greet.wav")
        framerate, nchannels = get_wav_info(wav_path)
        audio_opus = AudioOpus(framerate, nchannels)

        for pcm_data in read_audio_file(wav_path):
            opus_data = await audio_opus.pcm_to_opus(pcm_data)
            await self.websocket.send(opus_data)
        await self.send_silence_audio()

    async def send_silence_audio(self, duration_seconds: float = 1.2):
        # 发送 静音数据
        frames_count = int(duration_seconds * 1000 / 60)
        pcm_frame = b"\x00\x00" * int(INPUT_SERVER_AUDIO_SAMPLE_RATE / 1000 * 60)

        for _ in range(frames_count):
            await self.send_audio(pcm_frame)

    async def send_audio(self, pcm: bytes):
        if not self.websocket:
            return

        state = self.websocket.state
        if state == websockets.protocol.State.OPEN:
            opus_data = await self.audio_opus.pcm_to_opus(pcm)
            await self.websocket.send(opus_data)
        elif state in [websockets.protocol.State.CLOSED, websockets.protocol.State.CLOSING]:
            if self.message_handler_callback:
                await self.message_handler_callback({"type": "websocket", "state": "close", "source": "sdk.send_audio"})
            await asyncio.sleep(0.5)
        else:
            await asyncio.sleep(0.1)

    async def message_handler(self):
        try:
            async for message in self.websocket:
                if isinstance(message, bytes):
                    pcm_array = await self.audio_opus.opus_to_pcm(message)
                    self.audio_queue.extend(pcm_array)
                else:
                    data = json.loads(message)
                    message_type = data["type"]

                    if message_type == "hello":
                        self.hello_received.set()
                        self.session_id = data["session_id"]
                    elif message_type == "mcp":
                        await self.mcp(data)
                    elif self.message_handler_callback:
                        await self.message_handler_callback(data)
        except websockets.ConnectionClosed:
            if self.message_handler_callback:
                await self.message_handler_callback(
                    {"type": "websocket", "state": "close", "source": "sdk.message_handler"}
                )

    async def close(self):
        if self.message_handler_task and not self.message_handler_task.done():
            self.message_handler_task.cancel()
            try:
                await self.message_handler_task
            except asyncio.CancelledError:
                pass

        if self.websocket:
            await self.websocket.close()
