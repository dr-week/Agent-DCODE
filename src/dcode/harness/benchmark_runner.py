"""
Batch Benchmark Evaluation Runner (<100 lines).
Loads evaluation datasets, runs tasks through AgentHarness across models, and computes Pass@1/k.
"""

import json
import time
from typing import Any, Dict, List, Optional
from dcode.harness.config import HarnessConfig
from dcode.harness.runner import AgentHarness
from dcode.harness.scorecard import HarnessScorecard


class BenchmarkRunner:
    """Executes evaluation benchmarks across test suites and models."""

    def __init__(self, workspace_dir: str, default_test_cmd: str = "python3 -m unittest"):
        self.workspace_dir = workspace_dir
        self.default_test_cmd = default_test_cmd

    def run_benchmark_suite(
        self,
        tasks: List[Dict[str, Any]],
        model: Optional[str] = None,
        max_attempts: int = 3,
    ) -> Dict[str, Any]:
        """Run all tasks through the guarded harness and compute aggregate scorecard."""
        results: List[Dict[str, Any]] = []

        for task in tasks:
            t0 = time.time()
            task_id = task.get("id", f"task_{len(results)+1}")
            desc = task.get("description") or task.get("issue", "Solve task")
            test_cmd = task.get("test_command", self.default_test_cmd)

            cfg = HarnessConfig(
                workspace_dir=self.workspace_dir,
                test_command=test_cmd,
                max_steps=max_attempts,
            )
            harness = AgentHarness(cfg)
            res = harness.execute_swe_task(desc, model=model)
            elapsed_ms = (time.time() - t0) * 1000

            results.append({
                "id": task_id,
                "passed": res.get("success", False),
                "attempts": res.get("metrics", {}).get("steps", 1),
                "tokens": res.get("metrics", {}).get("tokens", 0),
                "cost_usd": res.get("metrics", {}).get("cost_usd", 0.0),
                "latency_ms": round(elapsed_ms, 2),
                "diff_lines": len(res.get("diff", "").splitlines()),
            })

        metrics = HarnessScorecard.calculate(results)
        metrics["model"] = model or "default-router"
        return metrics
