"""
Automated Regression Detector for AI Agent Harness.
Compares pre-patch and post-patch test execution results to prevent introducing regressions.
"""

import subprocess
from typing import Any, Dict, List, Set


class RegressionDetector:
    """Detects whether an agent patch broke previously passing tests."""

    @staticmethod
    def parse_test_output(output: str) -> Set[str]:
        """Extract set of test identifiers from unittest/pytest output."""
        passed_tests: Set[str] = set()
        for line in output.splitlines():
            line_str = line.strip()
            if " ... ok" in line_str:
                test_name = line_str.split(" ... ok")[0].strip()
                passed_tests.add(test_name)
            elif "PASSED" in line_str and "::" in line_str:
                test_name = line_str.split()[0].strip()
                passed_tests.add(test_name)
        return passed_tests

    def run_tests(self, test_cmd: str, cwd: str) -> Dict[str, Any]:
        """Execute test suite and parse passing tests."""
        try:
            res = subprocess.run(
                test_cmd, shell=True, cwd=cwd, capture_output=True, text=True, timeout=30
            )
            passed = self.parse_test_output(res.stdout + "\n" + res.stderr)
            return {"exit_code": res.returncode, "passed_tests": passed, "raw": res.stdout + res.stderr}
        except Exception as e:
            return {"exit_code": -1, "passed_tests": set(), "raw": str(e)}

    def check_regression(
        self, baseline_passed: Set[str], post_passed: Set[str]
    ) -> Dict[str, Any]:
        """Compare passing tests before and after patch application."""
        regressions = sorted(list(baseline_passed - post_passed))
        new_fixes = sorted(list(post_passed - baseline_passed))

        return {
            "has_regression": len(regressions) > 0,
            "regressions": regressions,
            "newly_fixed": new_fixes,
            "retained_passing": len(baseline_passed & post_passed),
        }
