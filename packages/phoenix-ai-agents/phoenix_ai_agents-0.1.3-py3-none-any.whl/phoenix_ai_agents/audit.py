
from __future__ import annotations

import datetime
import json
import logging
import os
import uuid
from typing import Any

import httpx

log = logging.getLogger("phoenix.audit")

class AuditClient:
    def __init__(self, api_url: str, api_key: str | None = None):
        self.api_url = api_url.rstrip("/")
        self.headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}

    def emit(self, event_type: str, payload: dict[str, Any]):
        data = {
            "audit_id": str(uuid.uuid4()),
            "event_type": event_type,
            "payload": payload,
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        }
        try:
            httpx.post(f"{self.api_url}/audit", json=data, headers=self.headers, timeout=5.0)
        except Exception as exc:
            log.warning("Audit emit failed: %s", exc)
