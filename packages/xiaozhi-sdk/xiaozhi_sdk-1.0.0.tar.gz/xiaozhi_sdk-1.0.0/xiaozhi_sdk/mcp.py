import json

import requests

from xiaozhi_sdk.config import VL_URL
from xiaozhi_sdk.data import mcp_initialize_payload, mcp_tool_conf, mcp_tools_payload


class McpTool(object):

    def __init__(self):
        self.session_id = ""
        self.vl_token = ""
        self.websocket = None
        self.tool_func = {}

    def get_mcp_json(self, payload: dict):
        return json.dumps({"session_id": self.session_id, "type": "mcp", "payload": payload})

    def _build_response(self, request_id: str, content: str, is_error: bool = False):
        return self.get_mcp_json(
            {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [{"type": "text", "text": content}],
                    "isError": is_error,
                },
            }
        )

    async def analyze_image(self, img_byte: bytes, question: str = "这张图片里有什么？"):
        headers = {"Authorization": f"Bearer {self.vl_token}"}
        files = {"file": ("camera.jpg", img_byte, "image/jpeg")}
        payload = {"question": question}

        response = requests.post(VL_URL, files=files, data=payload, headers=headers)
        return response.json()

    async def mcp_tool_call(self, mcp_json: dict):
        tool_name = mcp_json["params"]["name"]
        tool_func = self.tool_func[tool_name]

        if tool_name == "take_photo":
            res = await self.analyze_image(tool_func(None), mcp_json["params"]["arguments"]["question"])
        else:
            res = tool_func(mcp_json["params"]["arguments"])

        content = json.dumps(res, ensure_ascii=False)
        return self._build_response(mcp_json["id"], content)

    async def mcp(self, data: dict):
        payload = data["payload"]
        method = payload["method"]

        if method == "initialize":
            self.vl_token = payload["params"]["capabilities"]["vision"]["token"]
            mcp_initialize_payload["id"] = payload["id"]
            await self.websocket.send(self.get_mcp_json(mcp_initialize_payload))

        elif method == "tools/list":
            mcp_tools_payload["id"] = payload["id"]
            for name, func in self.tool_func.items():
                if func:
                    mcp_tool_conf[name]["name"] = name
                    mcp_tools_payload["result"]["tools"].append(mcp_tool_conf[name])

            await self.websocket.send(self.get_mcp_json(mcp_tools_payload))

        elif method == "tools/call":
            print("tools/call", payload)
            tool_name = payload["params"]["name"]
            if not self.tool_func.get(tool_name):
                raise Exception("Tool not found")

            mcp_res = await self.mcp_tool_call(payload)
            await self.websocket.send(mcp_res)
