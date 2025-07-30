import os
import sys
import uuid

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from xiaozhi_sdk.iot import OtaDevice


@pytest.mark.asyncio
async def test_main():
    serial_number = ""
    license_key = ""
    mac_address = "00:22:44:66:88:00"
    ota = OtaDevice(mac_addr=mac_address, client_id=str(uuid.uuid4()), serial_number=serial_number)
    res = await ota.activate_device()
    await ota.check_activate(res["activation"]["challenge"], license_key)
