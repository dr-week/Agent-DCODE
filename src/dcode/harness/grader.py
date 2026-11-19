"""
Agent Harness Automated Grader (<100 lines).
Evaluates agent solutions against test commands, string assertions, and diff criteria.
"""

import subprocess
from typing import Any, Callable, Dict, List, Optional


class HarnessGrader:
    """Grades agent outcomes deterministically using test suites or assertion hooks."""

    def __init__(self, workspace_dir: str):
        self.workspace_dir = workspace_dir

    def grade_command(self, test_command: str, timeout: int = 20) -> Dict[str, Any]:
        """Execute a shell test command inside the workspace and evaluate returncode."""
        try:
            proc = subprocess.run(
                test_command,
                shell=True,
                cwd=self.workspace_dir,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            out = (proc.stdout + "\n" + proc.stderr).strip()
            passed = proc.returncode == 0
            return {
                "passed": passed,
                "score": 1.0 if passed else 0.0,
                "returncode": proc.returncode,
                "output": out[:1000],
            }
        except subprocess.TimeoutExpired:
            return {"passed": False, "score": 0.0, "returncode": -1, "output": f"Timed out after {timeout}s"}
        except Exception as exc:
            return {"passed": False, "score": 0.0, "returncode": -1, "output": str(exc)}

    def grade_assertions(
        self,
        output_text: str,
        expected_substrings: Optional[List[str]] = None,
        custom_hook: Optional[Callable[[str], bool]] = None,
    ) -> Dict[str, Any]:
        """Grade text output against required substrings or a boolean assertion hook."""
        missing = [s for s in (expected_substrings or []) if s not in output_text]
        hook_passed = custom_hook(output_text) if custom_hook else True
        passed = len(missing) == 0 and hook_passed
        return {
            "passed": passed,
            "score": 1.0 if passed else 0.0,
            "missing_substrings": missing,
            "hook_passed": hook_passed,
        }
