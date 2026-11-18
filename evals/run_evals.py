#!/usr/bin/env python3
"""
Agentic Evaluation & Benchmark Runner for Agent-DCODE (<100 lines).
Measures Pass@1 across code generation, surgical editing, and CLI-Anything harness generation.
"""

import json
from pathlib import Path
import sys
import time
from typing import Any, Dict, List

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dcode.agents.verifier import execute_and_verify
from dcode.cli_anything import generate_cli_anything_harness, run_cli_harness
from dcode.config import PROJECTS_DIR

TASKS_FILE = Path(__file__).parent / "tasks.json"


def run_single_eval(task: Dict[str, Any]) -> Dict[str, Any]:
    start = time.time()
    passed = False
    details = ""

    if task["category"] == "cli_anything":
        gen = generate_cli_anything_harness(task["target_file"])
        if gen.get("success"):
            cmd = [sys.executable, gen["cli_harness"]] + task["cli_command"]
            res = run_cli_harness(cmd, ensure_json=True)
            passed = res.get("success", False) and (
                res.get("data", {}).get("result") == task["expected_json_result"]
            )
            details = f"CLI JSON output: {res.get('data')}"
    else:
        res = execute_and_verify(task["actions"])
        combined = "\n".join(str(o.get("output", "")) for o in res.get("outputs", []))
        passed = res.get("success", False) and task["expected_output"] in combined
        details = combined.strip().splitlines()[-1] if combined.strip() else str(res.get("error"))

    return {
        "id": task["id"],
        "category": task["category"],
        "passed": passed,
        "latency_ms": round((time.time() - start) * 1000, 1),
        "details": details,
    }


def cleanup_eval_files() -> None:
    for pattern in ("eval_*.py", "cli_anything_eval_*"):
        for f in PROJECTS_DIR.glob(pattern):
            f.unlink(missing_ok=True)


def main() -> None:
    tasks: List[Dict[str, Any]] = json.loads(TASKS_FILE.read_text(encoding="utf-8"))
    results = [run_single_eval(t) for t in tasks]
    cleanup_eval_files()

    passed_count = sum(1 for r in results if r["passed"])
    summary = {
        "total_tasks": len(results),
        "passed": passed_count,
        "pass_rate_percent": round((passed_count / max(len(results), 1)) * 100, 1),
        "results": results,
    }
    print(json.dumps(summary, indent=2))
    sys.exit(0 if passed_count == len(results) else 1)


if __name__ == "__main__":
    main()
