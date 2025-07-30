
from __future__ import annotations

import uuid
from typing import Any, Dict, List

from pydantic import BaseModel

from .agent import PhoenixAgent
from .audit import AuditClient


class TriggerType(str):
    ON_SUCCESS = "on_success"
    ON_FAIL = "on_fail"
    ALWAYS = "always"

class HandoffType(str):
    SEQUENTIAL = "sequential"
    BROADCAST = "broadcast"
    CONDITIONAL = "conditional"

class OrchestrationRule(BaseModel):
    source: str
    target: str
    trigger: str = TriggerType.ON_SUCCESS
    handoff: str = HandoffType.SEQUENTIAL
    conditions: dict[str, Any] = {}
    tool_context_share: bool = False

class PhoenixOrchestrator:
    def __init__(self, rules: List[OrchestrationRule], agents: Dict[str, PhoenixAgent], audit: AuditClient | None = None):
        self.rules = rules
        self.agents = agents
        self.audit = audit

    def run_workflow(self, start_agent: str, input: str) -> dict[str, Any]:
        session_id = str(uuid.uuid4())
        current_agent = start_agent
        payload = input
        trace = []

        while current_agent:
            agent = self.agents[current_agent]
            if self.audit:
                self.audit.emit("handoff.initiated", {"session_id": session_id, "agent": current_agent})
            result = agent.run(payload)
            trace.append({"agent": current_agent, "output": result.output})
            if self.audit:
                self.audit.emit("handoff.completed", {"session_id": session_id, "agent": current_agent})

            # pick next rule
            next_rule = next((r for r in self.rules if r.source == current_agent), None)
            if not next_rule:
                break
            current_agent = next_rule.target
            payload = result.output

        return {"session_id": session_id, "trace": trace}
