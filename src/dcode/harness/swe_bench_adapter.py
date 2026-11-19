"""
SWE-bench Lite Task Adapter.
Consumes SWE-bench instance specifications and grades autonomous issue resolution.
"""

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from dcode.harness.config import HarnessConfig
from dcode.harness.linter_guard import LinterGuard
from dcode.harness.runner import AgentHarness


@dataclass
class SWEBenchInstance:
    instance_id: str
    problem_statement: str
    test_command: str
    repo: str = "workspace"
    test_patch: Optional[str] = None


class SWEBenchAdapter:
    """Evaluates agent resolution on standardized SWE-bench format tasks."""

    def __init__(self, workspace_dir: str = "."):
        self.workspace_dir = workspace_dir

    def load_instances(self, json_path: str | Path) -> List[SWEBenchInstance]:
        """Load benchmark instances from a JSON file."""
        data = json.loads(Path(json_path).read_text(encoding="utf-8"))
        return [
            SWEBenchInstance(
                instance_id=item["instance_id"],
                problem_statement=item["problem_statement"],
                test_command=item.get("test_command", "python3 -m unittest"),
                repo=item.get("repo", "workspace"),
                test_patch=item.get("test_patch"),
            )
            for item in data
        ]

    def evaluate_instance(self, instance: SWEBenchInstance, model: Optional[str] = None) -> Dict[str, Any]:
        """Execute and grade an individual SWE-bench instance."""
        lint_pre = LinterGuard.check_workspace(self.workspace_dir)
        cfg = HarnessConfig(
            max_steps=3,
            step_timeout_sec=30,
            workspace_dir=self.workspace_dir,
            test_command=instance.test_command,
        )
        harness = AgentHarness(cfg)
        run_res = harness.execute_swe_task(instance.problem_statement, model=model)
        lint_post = LinterGuard.check_workspace(self.workspace_dir)

        resolved = (run_res.get("success", False) or run_res.get("resolved", False)) and lint_post.get("clean", True)
        return {
            "instance_id": instance.instance_id,
            "resolved": resolved,
            "diff": run_res.get("diff", ""),
            "attempts": run_res.get("attempts", 1),
            "lint_clean": lint_post.get("clean", True),
            "tokens": run_res.get("metrics", {}).get("total_tokens", 0),
            "cost_usd": run_res.get("metrics", {}).get("total_cost_usd", 0.0),
        }
