import aiohttp
import json

from xiaozhi_sdk.config import OTA_URL

USER_AGENT = "XiaoXhi-SDK/1.0"


class OtaDevice(object):

    def __init__(self, mac_addr: str, client_id: str, serial_number: str = ""):
        self.mac_addr = mac_addr
        self.client_id = client_id
        self.serial_number = serial_number

    async def activate_device(self):
        header = {
            "user-agent": USER_AGENT,
            "Device-Id": self.mac_addr,
            "Client-Id": self.client_id,
            "Content-Type": "application/json",
            "serial-number": self.serial_number,
        }
        payload = {
            "application": {"version": "1.0.0"},
            "board": {
                "type": "xiaozhi-sdk-box",
                "name": "xiaozhi-sdk-main",
            },
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(OTA_URL, headers=header, data=json.dumps(payload)) as response:
                data = await response.json()
                return data

    async def check_activate(self, challenge: str):
        url = OTA_URL + "/activate"
        header = {
            "user-agent": USER_AGENT,
            "Device-Id": self.mac_addr,
            "Client-Id": self.client_id,
            "Content-Type": "application/json",
        }
        payload = {
            "serial_number": self.serial_number,
            "challenge": challenge,
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=header, data=json.dumps(payload)) as response:
                return response.status == 200
