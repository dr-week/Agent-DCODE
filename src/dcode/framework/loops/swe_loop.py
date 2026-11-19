"""
Phase 2: Autonomous SWE Issue-to-PR Loop (inspired by SWE-agent/mini-swe-agent).
Executes a deterministic 4-stage pipeline:
  1. Locate (RepoMap AST scan)
  2. Snapshot (GitCheckpoint before edits)
  3. Patch (Apply surgical change via LLM or callable patcher)
  4. Verify & Commit/Rollback (Run test command; auto-rollback if verification fails)
"""

import subprocess
from typing import Any, Callable, Dict, Optional
from dcode.integrations.repomap import RepoMap
from dcode.runtime.git_checkpoint import GitCheckpoint


class SWELoop:
    """Autonomous Issue-to-PR software engineering loop with automatic test-driven rollback."""

    def __init__(
        self,
        workspace_dir: str,
        test_command: str = "python3 -m unittest",
        max_attempts: int = 3,
        auto_rollback: bool = True,
    ):
        self.workspace_dir = workspace_dir
        self.test_command = test_command
        self.max_attempts = max_attempts
        self.auto_rollback = auto_rollback
        self.repomap = RepoMap(workspace_dir)
        self.checkpoint = GitCheckpoint(workspace_dir)

    def solve_issue(
        self,
        issue_description: str,
        patch_fn: Callable[[str, Dict[str, Any], int, str], None],
    ) -> Dict[str, Any]:
        """Run the SWE loop until test_command passes or max_attempts is reached."""
        symbols = self.repomap.scan()
        snap_idx = self.checkpoint.snapshot()
        last_error = ""
        history = []

        for attempt in range(1, self.max_attempts + 1):
            patch_fn(issue_description, symbols, attempt, last_error)
            diff_text = self.checkpoint.diff_since(snap_idx)
            passed, output = self._run_verification()
            history.append(
                {
                    "attempt": attempt,
                    "passed": passed,
                    "output": output[:500],
                    "diff_lines": len(diff_text.splitlines()),
                }
            )
            if passed:
                return {
                    "success": True,
                    "issue": issue_description,
                    "attempts": attempt,
                    "diff": diff_text,
                    "history": history,
                }
            last_error = output
            if self.auto_rollback:
                self.checkpoint.rollback(snap_idx)

        return {
            "success": False,
            "issue": issue_description,
            "attempts": self.max_attempts,
            "diff": "",
            "history": history,
            "error": last_error[:500],
        }

    def _run_verification(self, timeout: int = 15) -> tuple[bool, str]:
        """Execute test_command inside workspace_dir and return (passed, combined_output)."""
        try:
            proc = subprocess.run(
                self.test_command,
                shell=True,
                cwd=self.workspace_dir,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            out = (proc.stdout + "\n" + proc.stderr).strip()
            return proc.returncode == 0, out
        except Exception as exc:
            return False, str(exc)
