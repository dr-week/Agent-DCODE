#!/usr/bin/env python3
"""
CLI Benchmark Suite Runner (<100 lines).
Loads evaluation tasks, runs them through the Agent Harness, and emits scorecards with Pass@1 and Pass@k.
"""

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dcode.config import PROJECT_ROOT
from dcode.harness import BenchmarkRunner, HarnessScorecard


def main() -> None:
    p = argparse.ArgumentParser(description="Agent-DCODE Evaluation Benchmark Suite")
    p.add_argument("--tasks", default="evals/tasks.json", help="Path to evaluation tasks JSON file")
    p.add_argument("--dir", default=str(PROJECT_ROOT), help="Workspace target directory")
    p.add_argument("--model", default=None, help="LiteLLM model identifier")
    p.add_argument("--max-attempts", type=int, default=3, help="Max retry attempts for Pass@k")
    p.add_argument("--json", action="store_true", dest="as_json", help="Emit raw JSON metrics")
    p.add_argument("--md-out", default=None, help="Save markdown scorecard to file")
    args = p.parse_args()

    tasks_path = Path(args.tasks)
    if not tasks_path.exists():
        print(f"[ERROR] Tasks file not found: {args.tasks}", file=sys.stderr)
        sys.exit(1)

    tasks = json.loads(tasks_path.read_text(encoding="utf-8"))
    runner = BenchmarkRunner(workspace_dir=args.dir)
    metrics = runner.run_benchmark_suite(tasks, model=args.model, max_attempts=args.max_attempts)

    if args.as_json:
        print(json.dumps(metrics, indent=2))
    else:
        md = HarnessScorecard.render_markdown(metrics)
        print(md)

    if args.md_out:
        Path(args.md_out).write_text(HarnessScorecard.render_markdown(metrics), encoding="utf-8")
        print(f"[SCORECARD SAVED] {args.md_out}")


if __name__ == "__main__":
    main()
