"""
Unit tests for GitWorktreeManager.
Verifies isolated temporary worktree creation, listing, and cleanup.
"""

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dcode.runtime.worktree_manager import GitWorktreeManager


class TestWorktreeAndTooling(unittest.TestCase):
    def setUp(self):
        self.temp_repo = tempfile.TemporaryDirectory()
        subprocess.run(["git", "init"], cwd=self.temp_repo.name, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Tester"], cwd=self.temp_repo.name, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@dcode.ai"], cwd=self.temp_repo.name, capture_output=True)
        test_file = Path(self.temp_repo.name) / "README.md"
        test_file.write_text("# Test Repo\n", encoding="utf-8")
        subprocess.run(["git", "add", "README.md"], cwd=self.temp_repo.name, capture_output=True)
        subprocess.run(["git", "commit", "-m", "init"], cwd=self.temp_repo.name, capture_output=True)

    def tearDown(self):
        self.temp_repo.cleanup()

    def test_worktree_lifecycle(self):
        mgr = GitWorktreeManager(self.temp_repo.name)
        wt_path = mgr.create_worktree()
        self.assertTrue(wt_path.exists())
        self.assertTrue((wt_path / "README.md").exists())

        worktrees = mgr.list_worktrees()
        self.assertGreaterEqual(len(worktrees), 2)

        removed = mgr.remove_worktree(wt_path)
        self.assertTrue(removed)
        self.assertFalse(wt_path.exists())


if __name__ == "__main__":
    unittest.main()
