"""
Unit tests for LinterGuard and SWEBenchAdapter.
Verifies syntax checking and SWE-bench format execution.
"""

from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dcode.harness.linter_guard import LinterGuard
from dcode.harness.swe_bench_adapter import SWEBenchAdapter, SWEBenchInstance


class TestSWEBenchHarness(unittest.TestCase):
    def test_linter_guard_valid_code(self):
        valid_code = "def add(a: int, b: int) -> int:\n    return a + b\n"
        res = LinterGuard.check_code(valid_code)
        self.assertTrue(res["valid"])
        self.assertEqual(len(res["errors"]), 0)
        self.assertGreater(res["total_nodes"], 0)

    def test_linter_guard_syntax_error(self):
        invalid_code = "def broken(\n    return 42"
        res = LinterGuard.check_code(invalid_code)
        self.assertFalse(res["valid"])
        self.assertGreater(len(res["errors"]), 0)
        self.assertIn("SyntaxError", res["errors"][0])

    def test_swe_bench_instance_evaluation(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            adapter = SWEBenchAdapter(workspace_dir=tmp_dir)
            inst = SWEBenchInstance(
                instance_id="test_task_01",
                problem_statement="Ensure function returns True",
                test_command="python3 -c \"assert True\"",
            )
            res = adapter.evaluate_instance(inst)
            self.assertEqual(res["instance_id"], "test_task_01")
            self.assertTrue(res["resolved"])
            self.assertTrue(res["lint_clean"])


if __name__ == "__main__":
    unittest.main()
