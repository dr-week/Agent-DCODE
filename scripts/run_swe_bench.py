#!/usr/bin/env python3
"""
CLI Runner for SWE-bench Lite Task Suite.
Evaluates agent issue resolution against standard benchmark instances and emits markdown scorecard.
"""

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from dcode.harness.scorecard import HarnessScorecard
from dcode.harness.swe_bench_adapter import SWEBenchAdapter


def main() -> None:
    p = argparse.ArgumentParser(description="Agent-DCODE SWE-bench Evaluation Suite")
    p.add_argument("--tasks", default=str(ROOT / "evals" / "swe_bench_mini.json"), help="Path to benchmark JSON")
    p.add_argument("--dir", default=str(ROOT), help="Workspace directory for evaluations")
    p.add_argument("--model", default=None, help="LiteLLM model string override")
    p.add_argument("--json", action="store_true", help="Emit raw JSON results")
    args = p.parse_args()

    adapter = SWEBenchAdapter(workspace_dir=args.dir)
    instances = adapter.load_instances(args.tasks)
    results = []

    for inst in instances:
        res = adapter.evaluate_instance(inst, model=args.model)
        results.append(res)

    eval_items = [
        {
            "id": r["instance_id"],
            "category": "swe_bench",
            "passed": r["resolved"],
            "latency_ms": 15.0,
            "details": f"attempts={r['attempts']} diff_len={len(r['diff'])}",
        }
        for r in results
    ]
    card = HarnessScorecard.calculate(eval_items)

    if args.json:
        print(json.dumps({"results": results, "scorecard": card}, indent=2))
    else:
        print(HarnessScorecard.render_markdown(card))


if __name__ == "__main__":
    main()
