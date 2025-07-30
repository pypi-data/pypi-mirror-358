import json
import logging

import requests

from xiaozhi_sdk.data import mcp_initialize_payload, mcp_tool_conf, mcp_tools_payload

logger = logging.getLogger("xiaozhi_sdk")


class McpTool(object):

    def __init__(self):
        self.session_id = ""
        self.explain_url = ""
        self.explain_token = ""
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
        headers = {"Authorization": f"Bearer {self.explain_token}"}
        files = {"file": ("camera.jpg", img_byte, "image/jpeg")}
        payload = {"question": question}
        try:
            response = requests.post(self.explain_url, files=files, data=payload, headers=headers, timeout=5)
            res_json = response.json()
        except Exception as e:
            return "网络异常", True
        if res_json.get("error"):
            return res_json, True
        return res_json, False

    async def mcp_tool_call(self, mcp_json: dict):
        tool_name = mcp_json["params"]["name"]
        tool_func = self.tool_func[tool_name]
        try:
            tool_res, is_error = tool_func(mcp_json["params"]["arguments"])
        except Exception as e:
            logger.error("tool_func error: %s", e)
            return

        if tool_name == "take_photo":
            tool_res, is_error = await self.analyze_image(tool_res, mcp_json["params"]["arguments"]["question"])

        content = json.dumps(tool_res, ensure_ascii=False)
        return self._build_response(mcp_json["id"], content, is_error)

    async def mcp(self, data: dict):
        payload = data["payload"]
        method = payload["method"]

        if method == "initialize":
            self.explain_url = payload["params"]["capabilities"]["vision"]["url"]
            self.explain_token = payload["params"]["capabilities"]["vision"]["token"]

            mcp_initialize_payload["id"] = payload["id"]
            await self.websocket.send(self.get_mcp_json(mcp_initialize_payload))

        elif method == "notifications/initialized":
            # print("\nMCP 工具初始化")
            pass

        elif method == "notifications/cancelled":
            logger.error("MCP 工具加载失败")

        elif method == "tools/list":
            mcp_tools_payload["id"] = payload["id"]
            tool_list = []
            for name, func in self.tool_func.items():
                if func:
                    tool_list.append(name)
                    mcp_tool_conf[name]["name"] = name
                    mcp_tools_payload["result"]["tools"].append(mcp_tool_conf[name])
            await self.websocket.send(self.get_mcp_json(mcp_tools_payload))
            if tool_list:
                logger.info("MCP 加载成功，当前可用工具列表为：%s", tool_list)

        elif method == "tools/call":
            tool_name = payload["params"]["name"]
            if not self.tool_func.get(tool_name):
                raise Exception("Tool not found")
            mcp_res = await self.mcp_tool_call(payload)
            await self.websocket.send(mcp_res)
        else:
            logger.warning("unknown method %s: %s", method, payload)
