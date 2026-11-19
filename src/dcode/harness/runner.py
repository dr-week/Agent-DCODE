"""
Agent Harness Runtime Orchestrator (<100 lines).
Executes agents inside a guarded scaffold with budgets, trajectory tracking, and automated grading.
"""

import time
from typing import Any, Dict, Optional
from dcode.config import PROJECT_ROOT
from dcode.harness.config import HarnessConfig
from dcode.harness.grader import HarnessGrader
from dcode.harness.guardian import HarnessGuardian
from dcode.harness.trajectory import TrajectoryRecorder
from dcode.integrations.cli_workflows import run_fix_workflow


class AgentHarness:
    """Production runtime harness providing budget controls, trajectory recording, and grading."""

    def __init__(self, config: Optional[HarnessConfig] = None):
        self.config = config or HarnessConfig()
        self.config.validate()
        self.workspace = self.config.workspace_dir or str(PROJECT_ROOT)
        self.guardian = HarnessGuardian(self.config)
        self.recorder = TrajectoryRecorder(self.config.trajectory_file)
        self.grader = HarnessGrader(self.workspace)

    def execute_swe_task(self, task_description: str, model: Optional[str] = None) -> Dict[str, Any]:
        """Run an autonomous SWE bugfix or feature task inside the guarded harness."""
        t0 = time.time()
        step_idx = 1
        try:
            self.guardian.tick_step(tokens_used=100, cost_used=0.001)
            fix_res = run_fix_workflow(
                issue=task_description,
                repo_dir=self.workspace,
                test_cmd=self.config.test_command,
                max_attempts=self.config.max_steps,
                model=model,
            )
            step_latency = (time.time() - t0) * 1000
            self.guardian.check_timeout(t0)

            diff_str = fix_res.get("diff", "")
            grade = self.grader.grade_command(self.config.test_command)

            self.recorder.log_step(
                step_index=step_idx,
                action_name="swe_fix",
                input_data=task_description,
                output_data=fix_res.get("error", "PASSED" if grade["passed"] else "FAILED"),
                diff=diff_str,
                tokens=self.guardian.total_tokens,
                cost_usd=self.guardian.total_cost_usd,
                latency_ms=step_latency,
                status="ok" if grade["passed"] else "failed",
            )

            return {
                "success": grade["passed"],
                "task": task_description,
                "grade": grade,
                "metrics": self.guardian.get_metrics(),
                "trajectory_file": self.recorder.log_path,
                "diff": diff_str,
            }
        except Exception as exc:
            return {
                "success": False,
                "task": task_description,
                "error": str(exc),
                "metrics": self.guardian.get_metrics(),
                "trajectory_file": self.recorder.log_path,
            }
