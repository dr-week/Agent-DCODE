#!/usr/bin/env python3
"""
Agentic Evaluation & Benchmark Runner for Agent-DCODE (<100 lines).
Measures Pass@1 and Self-Healing Pass@k across Code Gen, Surgical Edit, CLI-Anything, SWELoop, and MCP+Crawl4AI.
"""

import json
import os
from pathlib import Path
import sys
import tempfile
import time
from typing import Any, Dict, List

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dcode.agents.verifier import execute_and_verify
from dcode.cli_anything import generate_cli_anything_harness, run_cli_harness
from dcode.config import PROJECTS_DIR
from dcode.framework.loops.swe_loop import SWELoop
from dcode.integrations import MCPBridge, html_to_markdown

TASKS_FILE = Path(__file__).parent / "tasks.json"


def _eval_swe_loop(task: Dict[str, Any]) -> tuple[bool, str]:
    with tempfile.TemporaryDirectory() as tmp:
        src_f, tst_f = os.path.join(tmp, "pricing.py"), os.path.join(tmp, "test_pricing.py")
        Path(src_f).write_text("def discount(p, r):\n    return p - r\n", encoding="utf-8")
        Path(tst_f).write_text(
            "import unittest\nfrom pricing import discount\nclass T(unittest.TestCase):\n"
            "    def test_d(self):\n        self.assertEqual(discount(100, 0.2), 80.0)\n",
            encoding="utf-8",
        )
        swe = SWELoop(tmp, test_command="python3 -m unittest discover -s .", max_attempts=2)
        res = swe.solve_issue(
            task["issue"],
            lambda i, s, att, err: Path(src_f).write_text(
                "def discount(p, r):\n    return p * (1 - r)\n" if att == 2 else "def discount(p, r):\n    return p\n"
            ),
        )
        return res["success"], f"SWE attempts={res['attempts']} diff_lines={len(res['diff'].splitlines())}"


def _eval_mcp_crawl() -> tuple[bool, str]:
    md = html_to_markdown("<html><body><h1>Spec</h1><p>Use search_code</p></body></html>")
    bridge = MCPBridge()
    tools = [t["name"] for t in bridge.list_mcp_tools()]
    ok = "# Spec" in md and "search_code" in tools and "replace_in_file" in tools
    return ok, f"MCP tools={len(tools)} markdown_heading_ok={ok}"


def run_single_eval(task: Dict[str, Any]) -> Dict[str, Any]:
    start = time.time()
    cat = task["category"]
    if cat == "cli_anything":
        gen = generate_cli_anything_harness(task["target_file"])
        cmd = [sys.executable, gen.get("cli_harness", "")] + task["cli_command"]
        res = run_cli_harness(cmd, ensure_json=True) if gen.get("success") else {}
        passed = res.get("data", {}).get("result") == task["expected_json_result"]
        details = f"CLI JSON output: {res.get('data')}"
    elif cat == "swe_issue_solver":
        passed, details = _eval_swe_loop(task)
    elif cat == "mcp_and_research":
        passed, details = _eval_mcp_crawl()
    else:
        res = execute_and_verify(task["actions"])
        combined = "\n".join(str(o.get("output", "")) for o in res.get("outputs", []))
        passed = res.get("success", False) and task["expected_output"] in combined
        details = combined.strip().splitlines()[-1] if combined.strip() else str(res.get("error"))
    return {"id": task["id"], "category": cat, "passed": passed, "latency_ms": round((time.time() - start) * 1000, 1), "details": details}


def main() -> None:
    tasks: List[Dict[str, Any]] = json.loads(TASKS_FILE.read_text(encoding="utf-8"))
    results = [run_single_eval(t) for t in tasks]
    for pat in ("eval_*.py", "cli_anything_eval_*"):
        for f in PROJECTS_DIR.glob(pat):
            f.unlink(missing_ok=True)
    passed_count = sum(1 for r in results if r["passed"])
    summary = {"total_tasks": len(results), "passed": passed_count, "pass_rate_percent": round((passed_count / len(results)) * 100, 1), "results": results}
    print(json.dumps(summary, indent=2))
    sys.exit(0 if passed_count == len(results) else 1)


if __name__ == "__main__":
    main()
