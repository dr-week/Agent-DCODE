#!/usr/bin/env python3
"""
Agent-DCODE Agent-Native CLI (with HKUDS/CLI-Anything protocol support).
Supports --json, --dry-run, autonomous mode, CLI harness generation, session status, and undo.
"""

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dcode.agents.autonomous import run_autonomous_agent
from dcode.cli_anything import (
    discover_cli_harnesses,
    generate_cli_anything_harness,
    get_session_status,
    undo_last_mutation,
)
from dcode.llm.ollama_client import ask_llm
from dcode.llm.parser import extract_json
from dcode.tools.executor import execute_actions


def _run_prompt(prompt: str, dry_run: bool = False) -> dict:
    for _ in range(3):
        raw = ask_llm(prompt)
        data = extract_json(raw)
        if data:
            actions = data.get("actions", [])
            return {"success": True, "actions": execute_actions(actions, dry_run=dry_run)}
    return {"success": False, "error": "Failed to extract valid JSON after 3 attempts"}


def main() -> None:
    p = argparse.ArgumentParser(description="DCode Agent-Native CLI (CLI-Anything compatible)")
    p.add_argument("instruction", nargs="?", help="Coding instruction or subcommand (status, undo, list-clis)")
    p.add_argument("--autonomous", "-a", action="store_true", help="Run multi-step autonomous loop")
    p.add_argument("--max-iterations", type=int, default=5, help="Max autonomous loop iterations")
    p.add_argument("--generate-cli", metavar="FILE", help="Generate a CLI-Anything harness for a file in projects/")
    p.add_argument("--dry-run", action="store_true", help="Preview tool actions without mutating files")
    p.add_argument("--json", action="store_true", dest="as_json", help="Emit deterministic JSON output")
    args = p.parse_args()

    if args.generate_cli:
        res = generate_cli_anything_harness(args.generate_cli)
    elif args.instruction == "status":
        res = get_session_status()
    elif args.instruction == "undo":
        res = undo_last_mutation()
    elif args.instruction == "list-clis":
        res = {"harnesses": discover_cli_harnesses()}
    elif not args.instruction:
        p.print_help()
        return
    elif args.autonomous:
        res = run_autonomous_agent(args.instruction, max_iterations=args.max_iterations)
    else:
        res = _run_prompt(args.instruction, dry_run=args.dry_run)

    if args.as_json:
        print(json.dumps(res, indent=2))
    else:
        print(f"[DCODE RESULT] {json.dumps(res, indent=2)}")


if __name__ == "__main__":
    main()
