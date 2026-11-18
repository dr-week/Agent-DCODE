#!/usr/bin/env python3
"""
Integration test script for the Autonomous Agent loop.
"""

import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dcode.agents.autonomous import run_autonomous_agent


def run_scenario(title: str, goal: str, project: str, max_iter: int = 5, context: str = "") -> bool:
    print(f"\n{'=' * 60}\n{title}\n{'=' * 60}")
    result = run_autonomous_agent(
        goal=goal, project_name=project, max_iterations=max_iter, context=context
    )
    print(json.dumps({
        "success": result["success"],
        "iterations": result["iterations"],
        "actions_executed": result["actions_executed"],
        "errors": result.get("errors", [])[:2],
    }, indent=2))
    return bool(result["success"])


def run_test_1() -> bool:
    return run_scenario(
        "TEST 1: Basic File Creation",
        "Create a Python script in projects/ that prints 'Hello from Autonomous Agent'",
        "test_basic",
        5,
    )


def run_test_2() -> bool:
    return run_scenario(
        "TEST 2: Calculator Script",
        "Create a Python calculator script in projects/calculator.py with add, subtract, multiply, divide",
        "test_calculator",
        7,
    )


def run_test_3() -> bool:
    return run_scenario(
        "TEST 3: Error Recovery",
        "Create and test a regex email validator in projects/email_validator.py",
        "test_recovery",
        8,
    )


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else "all"
    if arg == "1":
        ok = run_test_1()
    elif arg == "2":
        ok = run_test_2()
    elif arg == "3":
        ok = run_test_3()
    else:
        ok = any([run_test_1(), run_test_2(), run_test_3()])
    sys.exit(0 if ok else 1)
