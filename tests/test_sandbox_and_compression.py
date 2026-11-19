"""
Unit tests for DockerSandbox runtime fallback and ContextCompressor.
Verifies isolation execution and context pruning for SWE agents.
"""

import tempfile
import unittest
from dcode.context.compressor import ContextCompressor
from dcode.runtime.docker_sandbox import DockerSandbox


class TestSandboxAndCompression(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_sandbox_local_execution(self):
        sandbox = DockerSandbox(self.temp_dir.name)
        res = sandbox.run(["python3", "-c", "print('sandbox_live')"], timeout=5)
        self.assertTrue(res["success"])
        self.assertIn("sandbox_live", res["stdout"])
        self.assertIn(res["backend"], ["docker", "local_process"])

    def test_sandbox_timeout_handling(self):
        sandbox = DockerSandbox(self.temp_dir.name)
        res = sandbox.run(["python3", "-c", "import time; time.sleep(2)"], timeout=1)
        self.assertFalse(res["success"])
        self.assertEqual(res["exit_code"], -1)
        self.assertIn("Timeout", res["stderr"])

    def test_compressor_symbol_map_pruning(self):
        sym_map = {
            "src/utils.py": ["def helper()", "def format()"],
            "src/auth/service.py": ["class AuthService", "def login(user, pw)", "def token()"],
            "src/models/user.py": ["class User", "def get_id()"],
        }
        pruned = ContextCompressor.prune_symbol_map(sym_map, query="auth login", max_symbols=5)
        self.assertIn("src/auth/service.py", pruned)
        self.assertTrue(len(pruned["src/auth/service.py"]) <= 5)

    def test_compressor_diff_truncation(self):
        long_diff = ["diff --git a/file.py b/file.py", "--- a/file.py", "+++ b/file.py", "@@ -1,5 +1,5 @@"]
        long_diff.extend([f"+line {i}" for i in range(200)])
        raw_diff = "\n".join(long_diff)
        compressed = ContextCompressor.compress_diff(raw_diff, max_lines=30)
        self.assertTrue(len(compressed.splitlines()) <= 35)
        self.assertIn("truncated", compressed)


if __name__ == "__main__":
    unittest.main()
