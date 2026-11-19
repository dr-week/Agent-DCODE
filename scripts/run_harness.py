#!/usr/bin/env python3
"""
CLI Runner for the Agent-DCODE Harness (<100 lines).
Runs agents inside a budget-constrained, trajectory-recording execution harness.
"""

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dcode.config import PROJECT_ROOT
from dcode.harness import AgentHarness, HarnessConfig


def main() -> None:
    p = argparse.ArgumentParser(description="Agent-DCODE AI Agent Harness CLI Runner")
    p.add_argument("task", nargs="?", default="Fix issue", help="Task description or goal")
    p.add_argument("--dir", default=str(PROJECT_ROOT), help="Workspace target directory")
    p.add_argument("--test-cmd", default="python3 -m unittest", help="Verification test command")
    p.add_argument("--max-steps", type=int, default=5, help="Step boundary cap")
    p.add_argument("--timeout", type=float, default=30.0, help="Per-step timeout seconds")
    p.add_argument("--token-budget", type=int, default=20000, help="Max tokens allowed")
    p.add_argument("--cost-limit", type=float, default=0.50, help="Max USD cost allowed")
    p.add_argument("--model", default=None, help="LiteLLM model identifier")
    p.add_argument("--trajectory-out", default=None, help="Custom JSONL trajectory output file")
    p.add_argument("--json", action="store_true", dest="as_json", help="Emit JSON output")
    args = p.parse_args()

    cfg = HarnessConfig(
        max_steps=args.max_steps,
        step_timeout_sec=args.timeout,
        token_budget=args.token_budget,
        cost_limit_usd=args.cost_limit,
        workspace_dir=args.dir,
        test_command=args.test_cmd,
        trajectory_file=args.trajectory_out,
    )
    harness = AgentHarness(cfg)
    result = harness.execute_swe_task(args.task, model=args.model)

    if args.as_json:
        print(json.dumps(result, indent=2))
    else:
        print(f"[HARNESS RESULT] Status: {'PASSED' if result.get('success') else 'FAILED'}")
        print(f"[HARNESS METRICS] {json.dumps(result.get('metrics', {}), indent=2)}")
        if result.get("diff"):
            print(f"[HARNESS DIFF]\n{result['diff']}")

    sys.exit(0 if result.get("success") else 1)


if __name__ == "__main__":
    main()
