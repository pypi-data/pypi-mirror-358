
from __future__ import annotations

import json
import logging
from abc import ABC, abstractmethod
from typing import Any

import httpx

log = logging.getLogger("phoenix.tools")

class ToolInterface(ABC):
    name: str
    description: str

    @abstractmethod
    def execute(self, input: str, **kwargs) -> Any: ...

    def to_openai_tool(self):
        """Return OpenAI tool schema; override if needed"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {"type": "object", "properties": {"input": {"type": "string"}}},
            },
        }

class HttpTool(ToolInterface):
    def __init__(self, name: str, url: str, method: str = "GET", description: str = ""):
        self.name, self.url, self.method, self.description = name, url, method.upper(), description or f"HTTP {method} {url}"

    def execute(self, input: str, **kwargs):
        log.info("HttpTool %s → %s (%s)", self.name, self.url, self.method)
        resp = httpx.request(self.method, self.url, params={"q": input})
        resp.raise_for_status()
        return resp.text

class PythonTool(ToolInterface):
    def __init__(self, name: str, func, description=""):
        self.name, self.func, self.description = name, func, description or func.__doc__ or ""

    def execute(self, input: str, **kwargs):
        return self.func(input, **kwargs)
