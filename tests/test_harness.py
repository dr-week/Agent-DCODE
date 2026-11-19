"""
Unit tests for the Agent-DCODE AI Agent Harness (<100 lines).
Tests config validation, guardian budget/step/timeout guards, trajectory logging, and grading.
"""

import json
import os
from pathlib import Path
import tempfile
import time
import unittest

from dcode.harness import (
    AgentHarness,
    BudgetExceededError,
    HarnessConfig,
    HarnessGrader,
    HarnessGuardian,
    StepCapExceededError,
    TimeoutExceededError,
    TrajectoryRecorder,
)


class TestAgentHarness(unittest.TestCase):
    def test_config_and_guardian_guards(self):
        with self.assertRaises(ValueError):
            HarnessConfig(max_steps=0).validate()

        cfg = HarnessConfig(max_steps=2, token_budget=500, cost_limit_usd=0.01, step_timeout_sec=0.1)
        guardian = HarnessGuardian(cfg)
        guardian.tick_step(tokens_used=100, cost_used=0.002)

        with self.assertRaises(StepCapExceededError):
            guardian.tick_step(tokens_used=100, cost_used=0.002)
            guardian.tick_step(tokens_used=100, cost_used=0.002)

        guardian_tok = HarnessGuardian(HarnessConfig(max_steps=10, token_budget=150))
        with self.assertRaises(BudgetExceededError):
            guardian_tok.tick_step(tokens_used=200)

        with self.assertRaises(TimeoutExceededError):
            guardian.check_timeout(time.time() - 0.5)

    def test_trajectory_recorder_and_grader(self):
        with tempfile.TemporaryDirectory() as tmp:
            log_file = os.path.join(tmp, "test_traj.jsonl")
            rec = TrajectoryRecorder(log_path=log_file)
            rec.log_step(1, "patch", {"file": "a.py"}, {"status": "ok"}, diff="+new", tokens=50)
            entries = rec.read_trajectory()
            self.assertEqual(len(entries), 1)
            self.assertEqual(entries[0]["action"], "patch")

            grader = HarnessGrader(tmp)
            grade = grader.grade_command("python3 -c 'print(\"GRADE_OK\")'")
            self.assertTrue(grade["passed"])
            self.assertEqual(grade["score"], 1.0)

            str_grade = grader.grade_assertions("Hello World", expected_substrings=["World"])
            self.assertTrue(str_grade["passed"])

    def test_agent_harness_swe_execution(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = os.path.join(tmp, "app.py")
            tst = os.path.join(tmp, "test_app.py")
            Path(src).write_text("def run():\n    return 42\n", encoding="utf-8")
            Path(tst).write_text(
                "import unittest\nfrom app import run\nclass T(unittest.TestCase):\n"
                "    def test_run(self):\n        self.assertEqual(run(), 42)\n",
                encoding="utf-8",
            )
            cfg = HarnessConfig(
                workspace_dir=tmp,
                test_command="python3 -m unittest discover -s .",
                max_steps=2,
                trajectory_file=os.path.join(tmp, "harness_traj.jsonl"),
            )
            harness = AgentHarness(cfg)
            res = harness.execute_swe_task("Verify app works")
            self.assertTrue(res["success"])
            self.assertIn("steps", res["metrics"])


if __name__ == "__main__":
    unittest.main()
