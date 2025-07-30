from __future__ import annotations

import functools
import logging
from typing import Any, Dict, List

import httpx

from .tools import ToolInterface

log = logging.getLogger("phoenix.services")

class MCPRemoteTool(ToolInterface):
    """A live wrapper around an MCP (phoenix_ai_services) endpoint."""
    def __init__(
        self,
        name: str,
        base_url: str,
        description: str = "",
        method: str = "POST",
        timeout: float = 20.0,
    ):
        self.name = name
        self.base_url = base_url.rstrip("/")
        self.description = description or f"MCP remote tool {name}"
        self.method = method.upper()
        self.timeout = timeout

    # ─── ToolInterface ---------------------------------------------------------
    def execute(self, input: str | Dict[str, Any], **kwargs) -> Any:
        url = f"{self.base_url}/tool/{self.name}"
        log.debug("MCPRemoteTool %s %s", self.method, url)
        client = httpx.Client(timeout=self.timeout)
        if self.method == "GET":
            r = client.get(url, params={"input": input})
        else:  # POST
            r = client.post(url, json={"input": input})
        r.raise_for_status()
        return r.json()

    # ─── Optional OpenAI Agent SDK adapter ------------------------------------
    def to_openai_tool(self):
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                # very generic signature; refine if you expose JSONSchema in MCP
                "parameters": {
                    "type": "object",
                    "properties": {"input": {"type": "string"}},
                    "required": ["input"],
                },
            },
        }

# ──────────────────────────────────────────────────────────────────────────────
class ServicesRegistryClient:
    """Fetch MCP registry and materialise `MCPRemoteTool` objects."""
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self._client = httpx.Client(timeout=5.0)

    def list_tools(self) -> List[Dict[str, Any]]:
        # Adjust if your service exposes a different route or shapes the payload
        r = self._client.get(f"{self.base_url}/tools")
        r.raise_for_status()
        return r.json()          # expected: [{tool_name, description, ...}, …]

    def load_all_tools(self) -> List[MCPRemoteTool]:
        tools = []
        for meta in self.list_tools():
            tools.append(
                MCPRemoteTool(
                    name=meta["tool_name"],
                    description=meta.get("description", ""),
                    base_url=self.base_url,
                    method=meta.get("http_method", "POST"),
                )
            )
        return tools
