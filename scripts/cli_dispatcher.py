"""
CLI Subcommand Dispatcher for Agent-DCODE.
Routes commandline invocations to specialized workflows, autonomous loops, or LLM tools.
"""

from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from dcode.agents.autonomous import run_autonomous_agent
from dcode.cli_anything import discover_cli_harnesses, get_session_status, undo_last_mutation
from dcode.integrations import (
    LangfuseTracer,
    MCPBridge,
    build_repo_map,
    get_integration_status,
    run_fix_workflow,
    run_qa_workflow,
    run_research_workflow,
    simulate_quantum_circuit,
)
from dcode.llm.ollama_client import ask_llm
from dcode.llm.parser import extract_json
from dcode.tools.executor import execute_actions


def run_prompt_action(prompt: str, dry_run: bool = False) -> dict:
    """Prompt LLM and execute returned structured JSON actions."""
    for _ in range(3):
        raw = ask_llm(prompt)
        data = extract_json(raw)
        if data:
            return {"success": True, "actions": execute_actions(data.get("actions", []), dry_run=dry_run)}
    return {"success": False, "error": "Failed to extract valid JSON after 3 attempts"}


def dispatch_workflow(cmd: str, target: str, extra: str, args: Any) -> Any:
    """Route command to fix, research, qa, harness, quantum, or autonomous execution."""
    if cmd == "fix":
        return run_fix_workflow(target or extra, repo_dir=args.dir, test_cmd=args.test_cmd, max_attempts=args.max_attempts, model=args.model)
    if cmd == "research":
        return run_research_workflow(target, prompt=extra or "Summarize key architecture and usage", model=args.model)
    if cmd == "qa":
        return run_qa_workflow(target, expect_texts=[s.strip() for s in (args.expect or "").split(",") if s.strip()])
    if cmd == "harness":
        from dcode.harness import AgentHarness, HarnessConfig
        return AgentHarness(HarnessConfig(max_steps=args.max_attempts, workspace_dir=args.dir, test_command=args.test_cmd)).execute_swe_task(target or extra, model=args.model)

    static_handlers = {
        "status": get_session_status,
        "undo": undo_last_mutation,
        "list-clis": lambda: {"harnesses": discover_cli_harnesses()},
        "integrations": lambda: {"integrations": get_integration_status()},
        "repomap": lambda: build_repo_map(args.dir),
        "mcp-tools": lambda: {"mcp_tools": MCPBridge().list_mcp_tools()},
        "metrics": lambda: LangfuseTracer().summary(),
        "quantum": lambda: simulate_quantum_circuit(2, [{"gate": "H", "qubit": 0}, {"gate": "CNOT", "control": 0, "target": 1}]),
    }
    if cmd in static_handlers:
        return static_handlers[cmd]()
    if args.autonomous:
        return run_autonomous_agent(f"{cmd} {target}".strip(), max_iterations=args.max_attempts)
    return run_prompt_action(f"{cmd} {target}".strip(), dry_run=args.dry_run)
