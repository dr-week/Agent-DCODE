"""
Unit tests for RegressionDetector, PatchResolver, and QuantumTestMinimizer.
Verifies failure detection, fuzzy patch resolution, and QUBO test minimization.
"""

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dcode.harness.patch_resolver import PatchResolver
from dcode.harness.regression_detector import RegressionDetector
from dcode.integrations.quantum_minimizer import QuantumTestMinimizer


class TestHarnessAdvancements(unittest.TestCase):
    def test_regression_detector_finds_failures(self):
        detector = RegressionDetector()
        base = {"test_auth", "test_db", "test_api"}
        post = {"test_auth", "test_cache"}  # test_db and test_api failed!

        res = detector.check_regression(base, post)
        self.assertTrue(res["has_regression"])
        self.assertEqual(res["regressions"], ["test_api", "test_db"])
        self.assertEqual(res["newly_fixed"], ["test_cache"])

    def test_patch_resolver_whitespace_tolerance(self):
        source = "def calc():\n    x = 10\n    return x\n"
        target = "    x = 10 \n    return x"
        replacement = "    x = 42\n    return x"

        ok, new_code, method = PatchResolver.apply_replacement(source, target, replacement)
        self.assertTrue(ok)
        self.assertIn("x = 42", new_code)
        self.assertIn(method, ["exact", "whitespace_normalized"])

    def test_quantum_test_minimizer_reduction(self):
        coverage = {
            "test_auth.py": ["login", "logout", "token"],
            "test_billing.py": ["charge", "refund"],
            "test_user.py": ["get_user", "login"],
        }
        minimizer = QuantumTestMinimizer(coverage)
        res = minimizer.minimize(["charge", "refund"], steps=80)
        self.assertIn("test_billing.py", res["selected_tests"])
        self.assertGreaterEqual(res["reduction_percent"], 0.0)


if __name__ == "__main__":
    unittest.main()
