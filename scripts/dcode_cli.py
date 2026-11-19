#!/usr/bin/env python3
"""
Agent-DCODE Agent-Native CLI Entrypoint.
Dispatches SWE Fix, Research, QA, Harness, Quantum, and Tool execution.
Strictly under 100 lines. Supports --json, --dry-run, and undo.
"""

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from cli_dispatcher import dispatch_workflow
from dcode.cli_anything import generate_cli_anything_harness
from dcode.config import PROJECT_ROOT


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
        res = dispatch_workflow(args.command, args.target, args.extra, args)
    print(json.dumps(res, indent=2) if args.as_json else f"[DCODE RESULT] {json.dumps(res, indent=2)}")


if __name__ == "__main__":
    main()
