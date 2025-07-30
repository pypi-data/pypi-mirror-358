
"""Simple CLI wrappers."""
import argparse
import importlib
import json
import logging
import pathlib
import sys

import yaml

from .agent import AgentConfig, PhoenixAgent
from .audit import AuditClient
from .memory import SqliteMemory
from .tools import HttpTool, PythonTool

log = logging.getLogger("phoenix.cli")

def load_tools(tools_cfg):
    tools=[]
    for t in tools_cfg:
        if 'url' in t:
            tools.append(HttpTool(name=t['name'], url=t['url'], description=t.get('description','')))
        elif 'python' in t:
            mod_name, func_name = t['python'].rsplit(":",1)
            fn = getattr(importlib.import_module(mod_name), func_name)
            tools.append(PythonTool(name=t['name'], func=fn, description=t.get('description','')))
    return tools

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="Agent YAML config")
    parser.add_argument("--message", required=True, help="User message")
    parser.add_argument("--audit-endpoint", help="Audit service base URL")
    args=parser.parse_args()

    cfg_data = yaml.safe_load(pathlib.Path(args.config).read_text())
    agent_cfg = AgentConfig(**{k:v for k,v in cfg_data.items() if k not in {'tools'}})
    
    if "mcp_base_url" in cfg_data:
        from .services import ServicesRegistryClient
        tools = ServicesRegistryClient(cfg_data["mcp_base_url"]).load_all_tools()
    else:
        tools = load_tools(cfg_data.get('tools',[]))

    memory = SqliteMemory()
    audit = AuditClient(args.audit_endpoint) if args.audit_endpoint else None
    agent = PhoenixAgent(agent_cfg, tools, memory, audit)
    res = agent.run(args.message)
    print(json.dumps(res.dict(), indent=2))

def orchestrate():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="Orchestration YAML")
    parser.add_argument("--input", required=True)
    args=parser.parse_args()
    print("Orchestration not yet implemented.")  # stub

if __name__ == "__main__":
    main()
