"""
Unit tests for Advanced Harness Workflows: Validator, Scorecard, Pipeline, and BenchmarkRunner (<100 lines).
"""

import os
from pathlib import Path
import tempfile
import unittest

from dcode.harness import (
    BenchmarkRunner,
    HarnessPipeline,
    HarnessScorecard,
    HarnessValidator,
)


class TestHarnessWorkflows(unittest.TestCase):
    def test_validator_syntax_check(self):
        with tempfile.TemporaryDirectory() as tmp:
            valid_py = os.path.join(tmp, "ok.py")
            broken_py = os.path.join(tmp, "broken.py")
            Path(valid_py).write_text("def valid():\n    return 1\n", encoding="utf-8")
            Path(broken_py).write_text("def broken(:\n    return 1\n", encoding="utf-8")

            validator = HarnessValidator(tmp)
            self.assertTrue(validator.validate_python_syntax("ok.py")["valid"])
            res_bad = validator.validate_python_syntax("broken.py")
            self.assertFalse(res_bad["valid"])
            self.assertIn("SyntaxError", res_bad["error"])

    def test_scorecard_metrics_calculation(self):
        sample_results = [
            {"id": "t1", "passed": True, "attempts": 1, "tokens": 100, "cost_usd": 0.001, "latency_ms": 50.0},
            {"id": "t2", "passed": True, "attempts": 2, "tokens": 200, "cost_usd": 0.002, "latency_ms": 100.0},
            {"id": "t3", "passed": False, "attempts": 3, "tokens": 300, "cost_usd": 0.003, "latency_ms": 150.0},
        ]
        card = HarnessScorecard.calculate(sample_results)
        self.assertEqual(card["total_tasks"], 3)
        self.assertEqual(card["pass_at_1_count"], 1)
        self.assertEqual(card["pass_at_k_count"], 2)
        self.assertAlmostEqual(card["pass_at_1_percent"], 33.3, places=1)
        self.assertAlmostEqual(card["pass_at_k_percent"], 66.7, places=1)

        md = HarnessScorecard.render_markdown(card)
        self.assertIn("Pass@1", md)
        self.assertIn("Pass@k", md)

    def test_pipeline_execution_and_rollback(self):
        with tempfile.TemporaryDirectory() as tmp:
            fpath = os.path.join(tmp, "state.txt")
            Path(fpath).write_text("initial", encoding="utf-8")

            pipe = HarnessPipeline(tmp, auto_rollback=True)
            pipe.add_stage("stage1", lambda c: {"stage1_ok": True})
            pipe.add_stage("mutate", lambda c: (Path(fpath).write_text("modified", encoding="utf-8"), {"success": True})[1])
            pipe.add_stage("fail", lambda c: {"success": False, "reason": "intentional error"})

            res = pipe.execute()
            self.assertFalse(res["success"])
            self.assertEqual(res["failed_stage"], "fail")
            self.assertEqual(Path(fpath).read_text(encoding="utf-8"), "initial")

    def test_benchmark_runner_mock(self):
        with tempfile.TemporaryDirectory() as tmp:
            runner = BenchmarkRunner(tmp, default_test_cmd="python3 -c 'exit(0)'")
            tasks = [{"id": "b1", "description": "Mock benchmark task 1"}]
            metrics = runner.run_benchmark_suite(tasks)
            self.assertEqual(metrics["total_tasks"], 1)
            self.assertEqual(metrics["pass_at_k_count"], 1)


if __name__ == "__main__":
    unittest.main()
