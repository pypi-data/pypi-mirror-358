from __future__ import annotations

import json
import logging
import uuid
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

# Lazy import to keep optional
try:
    from openai import OpenAI
    from openai.agent import Agent as OpenAIAgent
except Exception as e:  # pragma: no cover
    OpenAIAgent = None
    OpenAI = None

from .audit import AuditClient
from .memory import MemoryInterface
from .tools import ToolInterface

log = logging.getLogger("phoenix.agent")

class AgentConfig(BaseModel):
    name: str
    llm_model: str = "gpt-4o"
    system_prompt: str = "You are a helpful assistant"
    tools: List[str] = []
    memory_namespace: str = "default"

class StepContext(BaseModel):
    session_id: str
    step: int
    input: str
    output: Optional[str] = None
    tool_calls: int = 0

class AgentResult(BaseModel):
    session_id: str
    output: str
    steps: int

class PhoenixAgent:
    def __init__(
        self,
        cfg: AgentConfig,
        tools: List[ToolInterface],
        memory: MemoryInterface | None = None,
        audit: AuditClient | None = None,
        openai_client: Optional[OpenAI] = None,
    ):
        self.cfg = cfg
        self.tools_catalog: Dict[str, ToolInterface] = {t.name: t for t in tools}
        self.memory = memory
        self.audit = audit
        self.oa_client = openai_client or (OpenAI() if OpenAI else None)

        if self.oa_client is None or OpenAIAgent is None:
            raise ImportError("openai.agent SDK>=0.1.0 is required")

        self._agent = OpenAIAgent(
            model=self.cfg.llm_model,
            system_prompt=self.cfg.system_prompt,
            tools=[t.to_openai_tool() for t in tools if hasattr(t, "to_openai_tool")],
        )

    @classmethod
    def from_yaml(cls, path: str, tools: List[ToolInterface], memory: MemoryInterface, audit: AuditClient):
        import pathlib

        import yaml
        data = yaml.safe_load(pathlib.Path(path).read_text())
        return cls(cfg=AgentConfig(**data), tools=tools, memory=memory, audit=audit)

    def run(self, message: str) -> AgentResult:
        sid = str(uuid.uuid4())
        ctx = StepContext(session_id=sid, step=1, input=message)
        if self.audit:
            self.audit.emit("agent.step.started", ctx.dict())

        # In-memory loop using OpenAI Agent SDK
        res = self._agent.run(message)

        ctx.output = res
        if self.audit:
            self.audit.emit("agent.step.finished", ctx.dict())

        if self.memory:
            self.memory.save(self.cfg.memory_namespace, sid, {"input": message, "output": res})

        return AgentResult(session_id=sid, output=res, steps=1)
