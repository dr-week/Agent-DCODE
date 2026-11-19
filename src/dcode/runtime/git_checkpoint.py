"""
Phase 2: Git & File Checkpoint Rollback Runtime.
Captures full file state before autonomous edits, generates unified diffs,
and auto-reverts workspace changes when verification tests fail.
"""

import difflib
import os
import subprocess
from typing import Dict, List, Optional


class GitCheckpoint:
    """Manages atomic snapshots, unified diffs, and instant rollbacks for SWE loops."""

    def __init__(self, workspace_dir: str):
        self.workspace_dir = os.path.abspath(workspace_dir)
        self.snapshots: List[Dict[str, str]] = []

    def snapshot(self) -> int:
        """Capture an in-memory snapshot of all source files in the workspace."""
        state: Dict[str, str] = {}
        for root, dirs, files in os.walk(self.workspace_dir):
            dirs[:] = [d for d in dirs if d not in {".git", "__pycache__", "node_modules", ".venv"}]
            for fname in files:
                if fname.endswith((".py", ".js", ".ts", ".json", ".md", ".html", ".css", ".txt")):
                    full = os.path.join(root, fname)
                    rel = os.path.relpath(full, self.workspace_dir)
                    try:
                        with open(full, "r", encoding="utf-8", errors="ignore") as f:
                            state[rel] = f.read()
                    except Exception:
                        continue
        self.snapshots.append(state)
        return len(self.snapshots) - 1

    def diff_since(self, index: int = -1) -> str:
        """Compute a standard unified diff between the snapshot and current workspace."""
        if not self.snapshots:
            return ""
        before = self.snapshots[index]
        current_idx = self.snapshot()
        after = self.snapshots.pop(current_idx)
        diffs: List[str] = []
        for rel in sorted(set(before.keys()) | set(after.keys())):
            old_lines = before.get(rel, "").splitlines(keepends=True)
            new_lines = after.get(rel, "").splitlines(keepends=True)
            if old_lines != new_lines:
                patch = difflib.unified_diff(old_lines, new_lines, fromfile=f"a/{rel}", tofile=f"b/{rel}")
                diffs.append("".join(patch))
        return "\n".join(diffs)

    def rollback(self, index: int = -1) -> Dict[str, int]:
        """Restore workspace files to the specified snapshot state and clear stale .pyc caches."""
        if not self.snapshots:
            return {"restored": 0}
        target = self.snapshots[index]
        restored = 0
        for rel, content in target.items():
            full = os.path.join(self.workspace_dir, rel)
            os.makedirs(os.path.dirname(full), exist_ok=True)
            with open(full, "w", encoding="utf-8") as f:
                f.write(content)
            restored += 1
        for root, dirs, _ in os.walk(self.workspace_dir):
            if "__pycache__" in dirs:
                import shutil

                shutil.rmtree(os.path.join(root, "__pycache__"), ignore_errors=True)
        return {"restored": restored}

    def git_status(self) -> Optional[str]:
        """Return git status output if workspace is a git repository."""
        try:
            res = subprocess.run(
                ["git", "status", "--short"],
                cwd=self.workspace_dir,
                capture_output=True,
                text=True,
                timeout=5,
            )
            return res.stdout.strip() if res.returncode == 0 else None
        except Exception:
            return None
