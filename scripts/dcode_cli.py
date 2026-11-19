#!/usr/bin/env python3
"""
Agent-DCODE Agent-Native CLI with SWE Fix, Deep Research, QA, Harness, and Quantum workflows.
Strictly under 100 lines. Supports --json, --dry-run, and undo.
"""

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Optional

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dcode.agents.autonomous import run_autonomous_agent
from dcode.cli_anything import discover_cli_harnesses, generate_cli_anything_harness, get_session_status, undo_last_mutation
from dcode.config import PROJECT_ROOT
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


def _run_prompt(prompt: str, dry_run: bool = False) -> dict:
    for _ in range(3):
        raw = ask_llm(prompt)
        data = extract_json(raw)
        if data:
            return {"success": True, "actions": execute_actions(data.get("actions", []), dry_run=dry_run)}
    return {"success": False, "error": "Failed to extract valid JSON after 3 attempts"}


def _dispatch_workflow(cmd: str, target: str, extra: str, args: Any) -> Any:
    if cmd == "fix":
        return run_fix_workflow(target or extra, repo_dir=args.dir, test_cmd=args.test_cmd, max_attempts=args.max_attempts, model=args.model)
    if cmd == "research":
        return run_research_workflow(target, prompt=extra or "Summarize key architecture and usage", model=args.model)
    if cmd == "qa":
        return run_qa_workflow(target, expect_texts=[s.strip() for s in (args.expect or "").split(",") if s.strip()])
    if cmd == "harness":
        from dcode.harness import AgentHarness, HarnessConfig
        return AgentHarness(HarnessConfig(max_steps=args.max_attempts, workspace_dir=args.dir, test_command=args.test_cmd)).execute_swe_task(target or extra, model=args.model)
    static = {
        "status": get_session_status,
        "undo": undo_last_mutation,
        "list-clis": lambda: {"harnesses": discover_cli_harnesses()},
        "integrations": lambda: {"integrations": get_integration_status()},
        "repomap": lambda: build_repo_map(args.dir),
        "mcp-tools": lambda: {"mcp_tools": MCPBridge().list_mcp_tools()},
        "metrics": lambda: LangfuseTracer().summary(),
        "quantum": lambda: simulate_quantum_circuit(2, [{"gate": "H", "qubit": 0}, {"gate": "CNOT", "control": 0, "target": 1}]),
    }
    if cmd in static:
        return static[cmd]()
    if args.autonomous:
        return run_autonomous_agent(f"{cmd} {target}".strip(), max_iterations=args.max_attempts)
    return _run_prompt(f"{cmd} {target}".strip(), dry_run=args.dry_run)


def main() -> None:
    p = argparse.ArgumentParser(description="Agent-DCODE CLI (fix, research, qa, harness, quantum)")
    p.add_argument("command", nargs="?", help="Subcommand or prompt")
    p.add_argument("target", nargs="?", default="", help="Issue description, URL, or target")
    p.add_argument("extra", nargs="?", default="", help="Research prompt or detail")
    p.add_argument("--dir", default=str(PROJECT_ROOT), help="Workspace target directory")
    p.add_argument("--test-cmd", default="python3 -m unittest", help="Test command for verification")
    p.add_argument("--max-attempts", type=int, default=3, help="Max iterations or patch attempts")
    p.add_argument("--expect", default="", help="Comma-separated texts for QA")
    p.add_argument("--model", default=None, help="LiteLLM model string")
    p.add_argument("--generate-cli", metavar="FILE", help="Generate CLI-Anything harness")
    p.add_argument("--dry-run", action="store_true", help="Preview tool actions without mutating")
    p.add_argument("--autonomous", "-a", action="store_true", help="Run autonomous loop")
    p.add_argument("--json", action="store_true", dest="as_json", help="Emit JSON output")
    args = p.parse_args()

    if args.generate_cli:
        res = generate_cli_anything_harness(args.generate_cli)
    elif not args.command:
        p.print_help()
        return
    else:
        res = _dispatch_workflow(args.command, args.target, args.extra, args)
    print(json.dumps(res, indent=2) if args.as_json else f"[DCODE RESULT] {json.dumps(res, indent=2)}")


if __name__ == "__main__":
    main()
